export GOOGLE_APPLICATION_CREDENTIALS="" # for text to speech

brew install --cask libreoffice
sudo apt install libreoffice

brew install poppler
sudo apt-get install poppler-utils

brew install ffmpeg
sudo apt-get install ffmpeg

# Text-to-Speech Video Generator

This application processes conversation data to generate videos with text-to-speech narration and uploads them to YouTube.

## Prerequisites

1. Python 3.7 or higher
2. MongoDB (if using conversation IDs)
3. Google Cloud account with Text-to-Speech and YouTube Data API v3 enabled
4. OAuth 2.0 client credentials for YouTube API

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# YouTube Configuration
YOUTUBE_CLIENT_SECRETS_FILE=/path/to/your/client_secrets.json # for youtube uploader
YOUTUBE_DEFAULT_PRIVACY=private
YOUTUBE_DEFAULT_CATEGORY=27
YOUTUBE_DEFAULT_TAGS=education,learning,language

# MongoDB Configuration (if using conversation IDs)
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION=your_collection_name
```

## Usage

The application can process conversations from either a JSON file or a MongoDB document ID:

### Using a JSON file:
```bash
python Main.py path/to/your/conversations.json [--privacy private|unlisted|public]
```

### Using a MongoDB document ID:
```bash
python Main.py your_conversation_id [--privacy private|unlisted|public]
```

### Privacy Options:
- `private`: Only you can view the video (default)
- `unlisted`: Anyone with the link can view the video
- `public`: Anyone can view the video

## Input Data Format

### JSON File Format:
```json
{
    "topic": "Example Topic",
    "description": "Example description",
    "title": "Example Title",
    "audience": "Beginners",
    "level": "Basic",
    "category": "Education",
    "language": "English",
    "hashtags": ["education", "learning"],
    "conversations_background": "path/to/background.jpg",
    "new_words_background": "path/to/background.jpg",
    "speakers": {
        "Speaker1": {
            "gender": "female"
        },
        "Speaker2": {
            "gender": "male"
        }
    },
    "conversations": [
        {
            "order": 1,
            "speaker": "Speaker1",
            "text": "Hello, how are you?"
        }
    ],
    "new_words": [
        {
            "order": 1,
            "word": "example",
            "meaning": "a representative instance",
            "example": "This is an example sentence."
        }
    ]
}
```

## Output

The application generates:
1. Individual audio files for each conversation and new word
2. Slides for each conversation and new word
3. Individual videos for each conversation and new word
4. Three merged videos:
   - Conversations video
   - New words video
   - Complete video (both conversations and new words)
5. Uploads the complete video to YouTube

## Error Handling

- The application validates input files and MongoDB IDs
- Checks for proper YouTube configuration
- Provides detailed error messages for troubleshooting
- Gracefully handles processing and upload failures