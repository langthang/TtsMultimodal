# tts/TextToSpeechProcessor.py
import os
import json
from typing import Dict, Set, Union
from moviepy import *
from AppConfig import AppConfig
from Conversations import Conversations
from GoogleTextToSpeech import GoogleTextToSpeech
from processors.SpeechGenerator import SpeechGenerator
from processors.SlideGenerator import SlideGenerator
from processors.VideoGenerator import VideoGenerator
from database.MongoDBConnection import MongoDBConnection
from uploaders.YouTubeUploader import YouTubeUploader
from config.YouTubeConfig import YouTubeConfig

# Mapping gender to Google TTS voice names
GENDER_TO_GOOGLE_TTS_VOICE_NAMES = {
    "female": ["en-US-Chirp3-HD-Aoede", "en-US-Chirp3-HD-Callirrhoe", "en-US-Chirp3-HD-Erinome", "en-US-Chirp3-HD-Kore", "en-US-Chirp3-HD-Leda"],
    "male": ["en-US-Chirp3-HD-Achird", "en-US-Chirp3-HD-Alnilam", "en-US-Chirp3-HD-Algenib", "en-US-Chirp3-HD-Charon", "en-US-Chirp3-HD-Sadachbia"],
    "neutral": ["en-US-Chirp3-HD-Achird"]
}

# Mapping language to Google TTS language codes
LANGUAGE_TO_GOOGLE_TTS_LANGUAGE_CODE = {
    "English": "en-US",
    "French": "fr-FR",
    "Spanish": "es-ES"
}

class TextToSpeechProcessor:
    def __init__(self, source: Union[str, dict]):
        """
        Initialize the processor with either a JSON file path or MongoDB document ID.
        
        Args:
            source: Either a JSON file path (str ending with .json) or MongoDB document ID (str)
        """
        self.config = AppConfig()
        
        # Initialize processors
        google_tts = GoogleTextToSpeech()
        self.speech_generator = SpeechGenerator(google_tts)
        self.slide_generator = SlideGenerator()
        self.video_generator = VideoGenerator()
        
        # Voice management
        self.speaker_to_voice: Dict[str, str] = {}
        self.used_voices: Set[str] = set()

        # Load conversations data
        if isinstance(source, str) and source.endswith('.json'):
            self.json_file = source
            self.conversations_data = Conversations(source)
        else:
            # Assume it's a MongoDB document ID
            self.conversations_data = Conversations.from_mongodb(source)
            # Set json_file path for output directory structure
            self.json_file = self.conversations_data.get_location()
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
        
        # Initialize voice assignments
        self.assign_voices_to_speakers()

    def _get_language_code(self) -> str:
        """Get the language code for the current conversation."""
        language = self.conversations_data.language
        return LANGUAGE_TO_GOOGLE_TTS_LANGUAGE_CODE.get(
            language, 
            LANGUAGE_TO_GOOGLE_TTS_LANGUAGE_CODE[self.config.default_language]
        )

    def assign_voices_to_speakers(self):
        """Assign unique voices to each speaker based on their gender."""
        for speaker_name, speaker in self.conversations_data.speakers.items():
            gender = speaker.gender.lower()
            available_voices = GENDER_TO_GOOGLE_TTS_VOICE_NAMES.get(
                gender, 
                GENDER_TO_GOOGLE_TTS_VOICE_NAMES[self.config.default_speaker]
            )

            # Find the next available voice
            for voice in available_voices:
                if voice not in self.used_voices:
                    self.speaker_to_voice[speaker_name] = voice
                    self.used_voices.add(voice)
                    break

            # If no voice assigned, use default
            if speaker_name not in self.speaker_to_voice:
                self.speaker_to_voice[speaker_name] = GENDER_TO_GOOGLE_TTS_VOICE_NAMES[self.config.default_speaker][0]

    def process_conversations(self):
        """Process conversations and generate media files."""
        json_dir = os.path.dirname(os.path.abspath(self.json_file))
        
        for conversation in self.conversations_data.get_conversations():
            # Create necessary directories
            audio_dir = os.path.join(json_dir, "audio_conversations")
            slide_dir = os.path.join(json_dir, "slide_conversations")
            video_dir = os.path.join(json_dir, "video_conversations")
            
            for directory in [audio_dir, slide_dir, video_dir]:
                os.makedirs(directory, exist_ok=True)

            # Generate speech
            audio_file = os.path.join(audio_dir, f"{conversation.order}_{conversation.speaker.name}.{self.config.audio_format}")
            audio_file, audio_length = self.speech_generator.generate_speech(
                text=conversation.text,
                output_file=audio_file,
                voice_name=self.speaker_to_voice[conversation.speaker.name],
                gender=conversation.speaker.gender.upper(),
                language_code=self._get_language_code()
            )
            
            # Generate slide
            slide_file = os.path.join(slide_dir, f"{conversation.order}_{conversation.speaker.name}.pptx")
            slide_file = self.slide_generator.create_slide(
                title=conversation.speaker.name,
                content=conversation.text,
                background_image=self.conversations_data.get_conversations_background(),
                output_file=slide_file
            )
            
            # Generate video
            video_file = os.path.join(video_dir, f"{conversation.order}_{conversation.speaker.name}.{self.config.video_format}")
            video_file = self.video_generator.create_video(
                slide_file=slide_file,
                audio_file=audio_file,
                audio_length=audio_length,
                output_file=video_file
            )
            
            # Update conversation object
            conversation.audio = audio_file
            conversation.audio_length = audio_length
            conversation.slide = slide_file
            conversation.video = video_file

    def process_new_words(self):
        """Process new words and generate media files."""
        json_dir = os.path.dirname(os.path.abspath(self.json_file))
        
        for new_word in self.conversations_data.get_new_words():
            # Create necessary directories
            audio_dir = os.path.join(json_dir, "audio_new_words")
            slide_dir = os.path.join(json_dir, "slide_new_words")
            video_dir = os.path.join(json_dir, "video_new_words")
            
            for directory in [audio_dir, slide_dir, video_dir]:
                os.makedirs(directory, exist_ok=True)

            # Prepare text for speech
            text_to_speak = self._prepare_new_word_text(new_word)

            # Generate speech
            audio_file = os.path.join(audio_dir, f"new_word_{new_word.order}.{self.config.audio_format}")
            audio_file, audio_length = self.speech_generator.generate_speech(
                text=text_to_speak,
                output_file=audio_file,
                voice_name=GENDER_TO_GOOGLE_TTS_VOICE_NAMES[self.config.default_speaker][0],
                gender=self.config.default_speaker,
                language_code=self._get_language_code()
            )

            # Generate slide
            slide_file = os.path.join(slide_dir, f"new_word_{new_word.order}.pptx")
            content = self._prepare_new_word_slide_content(new_word)
            slide_file = self.slide_generator.create_slide(
                title=new_word.word or "",
                content=content,
                background_image=self.conversations_data.get_new_words_background(),
                output_file=slide_file
            )

            # Generate video
            video_file = os.path.join(video_dir, f"new_word_{new_word.order}.{self.config.video_format}")
            video_file = self.video_generator.create_video(
                slide_file=slide_file,
                audio_file=audio_file,
                audio_length=audio_length,
                output_file=video_file
            )

            # Update new word object
            new_word.audio = audio_file
            new_word.audio_length = audio_length
            new_word.slide = slide_file
            new_word.video = video_file

    def _prepare_new_word_text(self, new_word) -> str:
        """Prepare text for new word speech synthesis."""
        if new_word.order == 0 or new_word.word is None or new_word.meaning is None:
            return new_word.example
        return f"{new_word.word}. Meaning: {new_word.meaning}. Example:  {new_word.example}."

    def _prepare_new_word_slide_content(self, new_word) -> str:
        """Prepare content for new word slide."""
        if new_word.order == 0 or new_word.word is None or new_word.meaning is None:
            return new_word.example
        return f"Meaning: {new_word.meaning}\n\nExample: {new_word.example}"

    def merge_videos(self):
        """Merge all videos into final outputs."""
        self._merge_conversation_videos()
        self._merge_new_word_videos()
        self._merge_all_videos()

    def _merge_conversation_videos(self):
        """Merge conversation videos into one video."""
        conversations = self.conversations_data.get_conversations()
        
        if not conversations:
            output_file = "EMPTY"
        else:
            output_file = os.path.splitext(self.json_file)[0] + "_conversations_merged_video.mp4"
            self._merge_video_clips(
                [conv.video for conv in conversations],
                output_file
            )
        
        self.conversations_data.merged_video_conversations = output_file

    def _merge_new_word_videos(self):
        """Merge new word videos into one video."""
        new_words = self.conversations_data.get_new_words()
        
        if not new_words:
            output_file = "EMPTY"
        else:
            output_file = os.path.splitext(self.json_file)[0] + "_new_words_merged_video.mp4"
            self._merge_video_clips(
                [word.video for word in new_words],
                output_file
            )
        
        self.conversations_data.merged_video_new_words = output_file

    def _merge_all_videos_v2(self):
        """Merge the conversations and new words videos into one final video."""
        output_file = os.path.splitext(self.json_file)[0] + "_merged_video.mp4"
        
        # Get the merged videos
        conversations_video = self.conversations_data.merged_video_conversations
        new_words_video = self.conversations_data.merged_video_new_words
        
        # Collect valid videos
        videos = []
        
        # Add conversation video if it exists and is not EMPTY
        if conversations_video and conversations_video != "EMPTY" and os.path.exists(conversations_video):
            videos.append(conversations_video)
            
        # Add new words video if it exists and is not EMPTY
        if new_words_video and new_words_video != "EMPTY" and os.path.exists(new_words_video):
            videos.append(new_words_video)
            
        # If no valid videos, set output to EMPTY
        if not videos:
            output_file = "EMPTY"
        else:
            self._merge_video_clips(videos, output_file)
            
        self.conversations_data.merged_video_all = output_file

    def _merge_all_videos(self):
        """Merge all videos into one final video."""
        if self.config.use_v2_merge_all:
            print("Using V2 merge all method (merge only main videos)")
            return self._merge_all_videos_v2()
        else:
            print("Using V1 merge all method (merge all individual videos)")
            output_file = os.path.splitext(self.json_file)[0] + "_merged_video.mp4"
            
            # Get conversations and new words
            conversations = self.conversations_data.get_conversations()
            new_words = self.conversations_data.get_new_words()
            
            # Collect valid videos
            videos = []
            
            # Add conversation videos if they exist
            if conversations:
                videos.extend([conv.video for conv in conversations])
                
            # Add new word videos if they exist
            if new_words:
                videos.extend([word.video for word in new_words])
                
            # If no valid videos, set output to EMPTY
            if not videos:
                output_file = "EMPTY"
            else:
                self._merge_video_clips(videos, output_file)
                
            self.conversations_data.merged_video_all = output_file

    def _merge_video_clips_v2(self, video_files: list, output_file: str):
        """Merge multiple video files into one, never merging more than batch_size videos at once."""
        if not video_files:
            print("No videos found to merge.")
            return

        print(f"Merging {len(video_files)} videos into {output_file}")
        # Create a temporary directory for intermediate files
        temp_dir = os.path.join(os.path.dirname(output_file), "temp_merges")
        os.makedirs(temp_dir, exist_ok=True)
        temp_files = []

        try:
            # If we have more than batch_size videos, split into smaller groups
            batch_size = self.config.video_batch_size
            if len(video_files) > batch_size:
                # Split into two groups
                mid = len(video_files) // 2
                left_group = video_files[:mid]
                right_group = video_files[mid:]
                
                # Create temporary files for each group
                left_temp = os.path.join(temp_dir, "left_temp.mp4")
                right_temp = os.path.join(temp_dir, "right_temp.mp4")
                temp_files.extend([left_temp, right_temp])
                
                # Recursively merge each group
                self._merge_video_clips_v2(left_group, left_temp)
                self._merge_video_clips_v2(right_group, right_temp)
                
                # Merge the two temporary files
                clips = [VideoFileClip(left_temp), VideoFileClip(right_temp)]
                final_video = concatenate_videoclips(clips, method="compose")
                final_video.write_videofile(
                    output_file,
                    codec=f"{self.config.merged_video_codec}",
                    audio_codec=f"{self.config.merged_audio_codec}",
                    fps=self.config.merged_video_fps
                )
                print(f"Final merged video saved to {output_file}")
                
                # Close clips
                for clip in clips:
                    clip.close()
                final_video.close()
            else:
                # If we have batch_size or fewer videos, merge them directly
                clips = []
                for video_file in video_files:
                    if video_file and os.path.exists(video_file):
                        clips.append(VideoFileClip(video_file))
                    else:
                        print(f"Video file not found: {video_file}")
                
                if clips:
                    final_video = concatenate_videoclips(clips, method="compose")
                    final_video.write_videofile(
                        output_file,
                        codec=f"{self.config.merged_video_codec}",
                        audio_codec=f"{self.config.merged_audio_codec}",
                        fps=self.config.merged_video_fps
                    )
                    print(f"Video saved to {output_file}")
                    
                    # Close clips
                    for clip in clips:
                        clip.close()
                    final_video.close()

        finally:
            # Clean up temporary files and directory
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"Error removing temporary file {temp_file}: {e}")
            
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error removing temporary directory {temp_dir}: {e}")

    def _merge_video_clips(self, video_files: list, output_file: str):
        """Merge multiple video files into one."""
        if self.config.use_v2_merge:
            print("Using V2 merge method (recursive binary tree)")
            return self._merge_video_clips_v2(video_files, output_file)
        else:
            print("Using V1 merge method (sequential batches)")
            if not video_files:
                print("No videos found to merge.")
                return

            print(f"Merging {len(video_files)} videos into {output_file}")
            # Create a temporary directory for intermediate files
            temp_dir = os.path.join(os.path.dirname(output_file), "temp_merges")
            os.makedirs(temp_dir, exist_ok=True)
            temp_files = []

            try:
                # Process videos in batches
                batch_size = self.config.video_batch_size
                for i in range(0, len(video_files), batch_size):
                    batch = video_files[i:i + batch_size]
                    clips = []
                    
                    # Load clips for this batch
                    for video_file in batch:
                        if video_file and os.path.exists(video_file):
                            clips.append(VideoFileClip(video_file))
                        else:
                            print(f"Video file not found: {video_file}")

                    if clips:
                        # Create temporary file for this batch
                        temp_output = os.path.join(temp_dir, f"temp_merge_{i//batch_size}.mp4")
                        print(f"Creating temporary file: {temp_output}")
                        temp_files.append(temp_output)

                        # Merge batch and write to temporary file
                        batch_video = concatenate_videoclips(clips, method="compose")
                        batch_video.write_videofile(
                            temp_output,
                            codec=f"{self.config.merged_video_codec}",
                            audio_codec=f"{self.config.merged_audio_codec}",
                            fps=self.config.merged_video_fps
                        )
                        print(f"Batch {i//batch_size + 1} merged to temporary file: {temp_output}")

                        # Close clips to free memory
                        for clip in clips:
                            clip.close()
                        batch_video.close()

                # If we have multiple temporary files, merge them
                if len(temp_files) > 1:
                    final_clips = [VideoFileClip(f) for f in temp_files]
                    final_video = concatenate_videoclips(final_clips, method="compose")
                    final_video.write_videofile(
                        output_file,
                        codec=f"{self.config.merged_video_codec}",
                        audio_codec=f"{self.config.merged_audio_codec}",
                        fps=self.config.merged_video_fps
                    )
                    print(f"Final merged video saved to {output_file}")

                    # Close final clips
                    for clip in final_clips:
                        clip.close()
                    final_video.close()
                elif len(temp_files) == 1:
                    # If only one batch, just rename the temporary file
                    os.rename(temp_files[0], output_file)
                    print(f"Single batch video saved to {output_file}")

            finally:
                # Clean up temporary files and directory
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception as e:
                            print(f"Error removing temporary file {temp_file}: {e}")
                
                try:
                    os.rmdir(temp_dir)
                except Exception as e:
                    print(f"Error removing temporary directory {temp_dir}: {e}")
                
    def save_decorated_data(self):
        """Save the updated data to both JSON file and MongoDB if applicable."""
        data = {
            "document_id": self.conversations_data.get_document_id(),
            "topic": self.conversations_data.topic,
            "description": self.conversations_data.description,
            "title": self.conversations_data.title,
            "audience": self.conversations_data.audience,
            "level": self.conversations_data.level,
            "category": self.conversations_data.category,
            "language": self.conversations_data.language,
            "hashtags": self.conversations_data.hashtags,
            "conversations_background": self.conversations_data.conversations_background,
            "new_words_background": self.conversations_data.new_words_background,
            "location": self.conversations_data.get_location(),
            "merged_video_conversations": self.conversations_data.merged_video_conversations,
            "merged_video_new_words": self.conversations_data.merged_video_new_words,
            "merged_video_all": self.conversations_data.merged_video_all,
            "youtube_video_url": getattr(self.conversations_data, 'youtube_video_url', None),
            "thumbnail": getattr(self.conversations_data, 'thumbnail', None),
            "speakers": {
                name: {"gender": speaker.gender}
                for name, speaker in self.conversations_data.speakers.items()
            },
            "conversations": [
                {
                    "order": conv.order,
                    "speaker": conv.speaker.name,
                    "text": conv.text,
                    "slide": conv.slide,
                    "video": conv.video,
                    "audio_length": conv.audio_length,
                    "audio": conv.audio
                }
                for conv in self.conversations_data.get_conversations()
            ],
            "new_words": [
                {
                    "order": word.order,
                    "word": word.word,
                    "meaning": word.meaning,
                    "example": word.example,
                    "slide": word.slide,
                    "video": word.video,
                    "audio_length": word.audio_length,
                    "audio": word.audio
                }
                for word in self.conversations_data.get_new_words()
            ]
        }

        # Save to JSON file
        output_file = os.path.splitext(self.json_file)[0] + "_decorated.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Updated data saved to {output_file}")

        # If this was loaded from MongoDB, update the MongoDB document
        document_id = self.conversations_data.get_document_id()
        if document_id:
            mongo_conn = None
            try:
                # Connect to MongoDB
                mongo_conn = MongoDBConnection()
                mongo_conn.connect()
                
                # Update the MongoDB document
                try:
                    mongo_conn.update_conversation(document_id, data)
                    print(f"Successfully updated MongoDB document {document_id}")
                except ValueError as ve:
                    print(f"MongoDB Update Error - Invalid ID format: {ve}")
                except RuntimeError as re:
                    print(f"MongoDB Update Error - Connection issue: {re}")
                except Exception as e:
                    print(f"MongoDB Update Error: {str(e)}")
            finally:
                # Always disconnect if we connected
                if mongo_conn:
                    mongo_conn.disconnect()

    def _clean_hashtags(self, hashtags: list) -> list:
        """
        Remove '#' symbol from the beginning of each hashtag if present.
        
        Args:
            hashtags: List of hashtags that may or may not start with '#'
            
        Returns:
            List of hashtags with '#' removed from the beginning
        """
        return [tag.lstrip('#') for tag in hashtags] if hashtags else []

    def upload_thumbnail(self, video_id: str):
        """
        Upload a thumbnail for the YouTube video. If conversations_data has a thumbnail, use it;
        otherwise, use the conversations background.
        
        Args:
            video_id: The ID of the YouTube video to set thumbnail for
            
        Raises:
            Exception: If both thumbnail and background image are not found or if upload fails
        """
        # First try to use thumbnail from conversations data
        thumbnail_file = getattr(self.conversations_data, 'thumbnail', None)
        
        # If no specific thumbnail, use conversations background
        if thumbnail_file is None or not os.path.exists(thumbnail_file):
            thumbnail_file = self.conversations_data.get_conversations_background()
            print(f"Specific thumbnail not found, using conversations background: {thumbnail_file}")
        else:
            print(f"Using specific thumbnail from conversations data: {thumbnail_file}")
            
        if thumbnail_file is None or not os.path.exists(thumbnail_file):
            raise Exception("No valid thumbnail or background image found")
            
        try:
            # Initialize YouTube configuration and uploader
            youtube_config = YouTubeConfig()
            uploader = YouTubeUploader(youtube_config.client_secrets_file)
            uploader.authenticate()
            
            # Upload thumbnail
            print(f"Uploading thumbnail from: {thumbnail_file}")
            uploader.set_thumbnail(video_id, thumbnail_file)
            print("Thumbnail uploaded successfully")
        except Exception as e:
            print(f"Error uploading thumbnail: {e}")
            raise Exception(f"Error uploading thumbnail: {e}")

    def upload_to_youtube(self):
        """
        Upload the merged videos to YouTube and store the video URLs in the conversation data.
        
        Returns:
            List of upload results containing video IDs and URLs
            
        Raises:
            Exception: If video upload fails or merged video is not found
        """
        
        # Initialize YouTube configuration
        youtube_config = YouTubeConfig()
        
        # Initialize YouTube uploader
        uploader = YouTubeUploader(youtube_config.client_secrets_file)
        uploader.authenticate()
        
        # Upload videos
        upload_results = []
        
        # Upload complete merged video
        print(f"Uploading complete merged video: {self.conversations_data.merged_video_all}")   
        if self.conversations_data.merged_video_all is not None and os.path.exists(self.conversations_data.merged_video_all):
            try:
                # Clean hashtags for tags and format for description
                clean_tags = self._clean_hashtags(self.conversations_data.hashtags)
                
                result = uploader.upload_video(
                    video_file=self.conversations_data.merged_video_all,
                    title=self.conversations_data.title,
                    description=self.conversations_data.description,
                    tags=clean_tags,
                    privacy_status=youtube_config.default_privacy_status,
                    category_id=youtube_config.default_category_id,
                    language=self._get_language_code()
                )
                upload_results.append(result)
                
                # Store the YouTube video URL in the conversation data
                print(f"Upload result: {result}")
                if result and 'video_url' in result:
                    self.conversations_data.youtube_video_url = result['video_url']
                    print(f"YouTube video URL: {result['video_url']}")
                
            except Exception as e:
                print(f"Error uploading complete video: {e}")
                raise Exception(f"Error uploading complete video: {e}")
        else:
            raise Exception(f"Merged video not found: {self.conversations_data.merged_video_all}")
        
        return upload_results
    

    def delete_media_folders(self):
        """Delete audio, slide, and video folders for both conversations and new words."""
        json_dir = os.path.dirname(os.path.abspath(self.json_file))
        
        # Folders to delete
        folders_to_delete = [
            os.path.join(json_dir, "audio_conversations"),
            os.path.join(json_dir, "slide_conversations"),
            os.path.join(json_dir, "video_conversations"),
            os.path.join(json_dir, "audio_new_words"),
            os.path.join(json_dir, "slide_new_words"),
            os.path.join(json_dir, "video_new_words")
        ]
        
        for folder in folders_to_delete:
            try:
                if os.path.exists(folder):
                    # Remove all files in the folder
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            else:
                                os.rmdir(file_path)  # Remove subdirectories if any
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
                    
                    # Remove the folder itself
                    os.rmdir(folder)
                    print(f"Successfully deleted folder: {folder}")
                else:
                    print(f"Folder does not exist: {folder}")
            except Exception as e:
                print(f"Error deleting folder {folder}: {e}")

    def generate(self):
        """Run the entire text-to-speech processing pipeline."""
        self.process_conversations()
        self.process_new_words()
        self.merge_videos()
        self.save_decorated_data()
        self.delete_media_folders()

    def upload(self):
        try:
            # Upload video first
            upload_results = self.upload_to_youtube()
            self.save_decorated_data()  # Save to store the YouTube URL
            
            # Then set thumbnail if we have a video ID
            if upload_results and upload_results[0] and 'video_id' in upload_results[0]:
                self.upload_thumbnail(upload_results[0]['video_id'])
                
        except Exception as e:
            print(f"Error in YouTube upload process: {e}")
            raise