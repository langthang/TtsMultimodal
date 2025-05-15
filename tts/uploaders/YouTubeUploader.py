import os
import pickle
from typing import Optional, Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class YouTubeUploader:
    """Class to handle YouTube video uploads."""
    
    # OAuth 2.0 scopes required for uploading videos
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, client_secrets_file: str):
        """
        Initialize the YouTube uploader.
        
        Args:
            client_secrets_file: Path to the OAuth 2.0 client secrets file
        """
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self.youtube = None
        
    def authenticate(self):
        """
        Authenticate with YouTube using OAuth 2.0.
        Loads saved credentials if they exist, otherwise starts the OAuth flow.
        """
        # Token file stores the user's credentials from previously successful logins
        token_file = "youtube_token.pickle"
        
        if os.path.exists(token_file):
            print("Loading saved credentials...")
            with open(token_file, "rb") as token:
                self.credentials = pickle.load(token)
        
        # If there are no valid credentials available, authenticate
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                print("Refreshing access token...")
                self.credentials.refresh(Request())
            else:
                print("Fetching new tokens...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, "wb") as token:
                print("Saving credentials for future use...")
                pickle.dump(self.credentials, token)
        
        # Build the YouTube service
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        print("Successfully authenticated with YouTube")
    
    def upload_video(
        self,
        video_file: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        privacy_status: str = "private",
        category_id: str = "27",  # Default to "Education" category
        language: str = "en"
    ) -> Dict:
        """
        Upload a video to YouTube.
        
        Args:
            video_file: Path to the video file
            title: Video title
            description: Video description
            tags: List of video tags (optional)
            privacy_status: Video privacy status ("private", "unlisted", or "public")
            category_id: Video category ID (default: "27" for Education)
            language: Video language code (default: "en" for English)
            
        Returns:
            Dictionary containing video information including the video ID
        """
        if not self.youtube:
            raise RuntimeError("YouTube service not initialized. Call authenticate() first.")
        
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file not found: {video_file}")
        
        # Prepare the video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id,
                'defaultLanguage': language,
                'defaultAudioLanguage': language
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create the video insert request
        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(
                video_file,
                chunksize=-1,
                resumable=True
            )
        )
        
        # Execute the request and handle the response
        try:
            print(f"Uploading video: {title}")
            response = insert_request.execute()
            print(f"Video uploaded successfully! Video ID: {response['id']}")
            
            video_url = f"https://www.youtube.com/watch?v={response['id']}"
            return {
                'video_id': response['id'],
                'video_url': video_url,
                'title': title,
                'privacy_status': privacy_status
            }
            
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            raise
    
    def update_video_privacy(self, video_id: str, privacy_status: str) -> bool:
        """
        Update the privacy status of a video.
        
        Args:
            video_id: The ID of the video to update
            privacy_status: New privacy status ("private", "unlisted", or "public")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.youtube:
            raise RuntimeError("YouTube service not initialized. Call authenticate() first.")
        
        try:
            self.youtube.videos().update(
                part="status",
                body={
                    "id": video_id,
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            ).execute()
            print(f"Updated video {video_id} privacy status to {privacy_status}")
            return True
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return False
    
    def set_thumbnail(self, video_id: str, thumbnail_file: str) -> bool:
        """
        Set a custom thumbnail for a YouTube video.
        
        Args:
            video_id: The ID of the video to update
            thumbnail_file: Path to the image file to use as thumbnail
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If YouTube service is not initialized
            FileNotFoundError: If thumbnail file doesn't exist
            HttpError: If the API request fails
        """
        if not self.youtube:
            raise RuntimeError("YouTube service not initialized. Call authenticate() first.")
            
        if not os.path.exists(thumbnail_file):
            raise FileNotFoundError(f"Thumbnail file not found: {thumbnail_file}")
            
        try:
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(
                    thumbnail_file, 
                    mimetype='image/jpeg',
                    resumable=True
                )
            ).execute()
            print(f"Successfully set thumbnail for video {video_id}")
            return True
            
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            raise
    
    def get_video_status(self, video_id: str) -> Dict:
        """
        Get the current status of a video.
        
        Args:
            video_id: The ID of the video to check
            
        Returns:
            Dictionary containing video status information
        """
        if not self.youtube:
            raise RuntimeError("YouTube service not initialized. Call authenticate() first.")
        
        try:
            response = self.youtube.videos().list(
                part="status,snippet",
                id=video_id
            ).execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    'video_id': video_id,
                    'privacy_status': video['status']['privacyStatus'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'tags': video['snippet'].get('tags', [])
                }
            else:
                raise ValueError(f"Video {video_id} not found")
                
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            raise 