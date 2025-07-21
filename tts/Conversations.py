import json
from typing import List, Dict, Any, Optional, Union
from database.MongoDBConnection import MongoDBConnection


class Conversation:
    """Represents a single conversation line."""
    def __init__(self, order: int, speaker: 'Speaker', text: str, native_text: Optional[str] = None, translated_text: Optional[str] = None, slide: Optional[str] = None, video: Optional[str] = None, audio_length: Optional[int] = None, audio: Optional[str] = None, sleep: Optional[int] = None):
        """
        Initialize a Conversation object.
        :param order: The order of the conversation.
        :param speaker: The speaker of the conversation (Speaker object).
        :param text: The text of the conversation.
        :param slide: Path to the slide file (optional).
        :param video: Path to the video file (optional).
        :param audio_length: Length of the audio in seconds (optional).
        :param audio: Path to the audio file (optional).
        :param sleep: Seconds of silence to append after the audio (optional).
        """
        self.order = order
        self.speaker = speaker
        self.text = text
        self.native_text = native_text # not using for now, use text instead
        self.translated_text = translated_text
        self.slide = slide  # Path to the slide file
        self.video = video  # Path to the video file
        self.audio_length = audio_length  # Length of the audio in seconds
        self.audio = audio  # Path to the audio file
        self.sleep = sleep  # Seconds of silence to append after the audio

    def __repr__(self):
        return (f"Conversation(order={self.order}, speaker={self.speaker}, text='{self.text}', "
                f"native_text='{self.native_text}', translated_text='{self.translated_text}', "
                f"slide='{self.slide}', video='{self.video}', audio_length={self.audio_length}, audio='{self.audio}', sleep={self.sleep})")


class NewWord:
    """Represents a single new word entry."""
    def __init__(self, order: int, word: str, meaning: str, example: str, translated_word: Optional[str] = None, translated_meaning: Optional[str] = None, translated_example: Optional[str] = None, slide: Optional[str] = None, video: Optional[str] = None, audio_length: Optional[int] = None, audio: Optional[str] = None, sleep: Optional[int] = None):
        self.order = order
        self.word = word
        self.meaning = meaning
        self.example = example
        self.translated_word = translated_word
        self.translated_meaning = translated_meaning
        self.translated_example = translated_example
        self.slide = slide  # Path to the slide file
        self.video = video  # Path to the video file
        self.audio_length = audio_length  # Length of the audio in seconds
        self.audio = audio  # Path to the audio file
        self.sleep = sleep  # Seconds of silence to append after the audio

    def __repr__(self):
        return (f"NewWord(order={self.order}, word='{self.word}', meaning='{self.meaning}', example='{self.example}', "
                f"translated_word='{self.translated_word}', translated_meaning='{self.translated_meaning}', "
                f"translated_example='{self.translated_example}', "
                f"slide='{self.slide}', video='{self.video}', audio_length={self.audio_length}, audio='{self.audio}', sleep={self.sleep})")


class Speaker:
    """Represents a single speaker."""
    def __init__(self, name: str, gender: str):
        self.name = name
        self.gender = gender

    def __repr__(self):
        return f"Speaker(name='{self.name}', gender='{self.gender}')"


class Conversations:
    """Represents the entire conversation structure."""
    def __init__(self, source: Union[str, dict]):
        """
        Initialize the class by loading from either a JSON file path or MongoDB document.
        
        Args:
            source: Either a JSON file path (str) or a MongoDB document (dict)
        """
        self.document_id = None  # Initialize document_id
        
        if isinstance(source, str):
            self._load_from_json(source)
        elif isinstance(source, dict):
            self._load_from_dict(source)
        else:
            raise ValueError("Source must be either a JSON file path or a MongoDB document")

    def _load_from_json(self, json_file: str):
        """Load conversation data from a JSON file."""
        with open(json_file, "r") as file:
            data = json.load(file)
        self._load_from_dict(data)

    def _load_from_dict(self, data: dict):
        """Load conversation data from a dictionary."""
        # Parse the data
        self.document_id = data.get("_id") or data.get("document_id")  # Try MongoDB _id first
        self.topic = data.get("topic")
        self.description = data.get("description")
        self.title = data.get("title")
        self.audience = data.get("audience")
        self.level = data.get("level")
        self.category = data.get("category")
        self.language = data.get("language")
        self.hashtags = data.get("hashtags", [])
        self.location = data.get("location")
        self.conversations_background = data.get("conversations_background")
        self.new_words_background = data.get("new_words_background")
        self.merged_video_conversations = data.get("merged_video_conversations")
        self.merged_video_new_words = data.get("merged_video_new_words")
        self.merged_video_all = data.get("merged_video_all")
        self.youtube_video_url = data.get("youtube_video_url")
        self.thumbnail = data.get("thumbnail")  # Add thumbnail field

        # Parse speakers
        self.speakers = {
            name: Speaker(name=name, gender=details.get("gender", "unknown"))
            for name, details in data.get("speakers", {}).items()
        }

        # Parse conversations and map speaker strings to Speaker objects
        self.conversations = [
            Conversation(
                order=conv["order"],
                speaker=self.speakers.get(conv["speaker"], Speaker(name=conv["speaker"], gender="unknown")),
                text=conv["text"],
                native_text=conv.get("native_text"),
                translated_text=conv.get("translated_text"),
                slide=conv.get("slide"),
                video=conv.get("video"),
                audio_length=conv.get("audio_length"),
                audio=conv.get("audio"),
                sleep=conv.get("sleep") 
            )
            for conv in data.get("conversations", [])
        ]

        # Parse new words
        self.new_words = [
            NewWord(
                order=word.get("order"),
                word=word.get("word"),
                meaning=word.get("meaning"),
                example=word.get("example"),
                translated_word=word.get("translated_word"),
                translated_meaning=word.get("translated_meaning"),
                translated_example=word.get("translated_example"),
                slide=word.get("slide"),
                video=word.get("video"),
                audio_length=word.get("audio_length"),
                audio=word.get("audio"),
                sleep=word.get("sleep")
            )
            for word in data.get("new_words", [])
        ]

    @classmethod
    def from_mongodb(cls, conversation_id: str) -> 'Conversations':
        """
        Create a Conversations instance from MongoDB document.
        
        Args:
            conversation_id: The ID of the conversation to load
            
        Returns:
            A new Conversations instance
        """
        # Get MongoDB connection
        mongo_conn = MongoDBConnection()
        
        # Connect to database
        mongo_conn.connect()
        
        try:
            # Get conversation document
            conversation_data = mongo_conn.get_conversation_by_id(conversation_id)
            if conversation_data is None:
                raise ValueError(f"Conversation with ID {conversation_id} not found")
            
            # Set the document_id in the data
            conversation_data["document_id"] = conversation_id
                
            # Create new instance
            return cls(conversation_data)
        except Exception as e:
            print(f"Error loading conversation from MongoDB: {e}")
            raise
        finally:
            # Always disconnect
            mongo_conn.disconnect()

    def get_speaker(self, name: str) -> Speaker:
        """Return a Speaker object for the given name."""
        return self.speakers.get(name, Speaker(name=name, gender="unknown"))

    def get_conversations(self) -> List[Conversation]:
        """Return the conversation as a list of Conversation objects."""
        return self.conversations

    def get_new_words(self) -> List[NewWord]:
        """Return the new words as a list of NewWord objects."""
        return self.new_words
    
    def get_conversations_background(self) -> str:
        """Return the conversations background."""
        return self.conversations_background
    
    def get_new_words_background(self) -> str:
        """Return the new words background."""
        return self.new_words_background
    
    def get_location(self) -> str:
        """Return the location."""
        return self.location

    def get_document_id(self) -> Optional[str]:
        """Return the MongoDB document ID if it exists."""
        return self.document_id