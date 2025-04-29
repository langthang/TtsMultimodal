import json
from typing import List, Dict, Any, Optional


class Conversation:
    """Represents a single conversation line."""
    def __init__(self, order: int, speaker: 'Speaker', text: str, slide: Optional[str] = None, video: Optional[str] = None, audio_length: Optional[int] = None, audio: Optional[str] = None):
        """
        Initialize a Conversation object.
        :param order: The order of the conversation.
        :param speaker: The speaker of the conversation (Speaker object).
        :param text: The text of the conversation.
        :param slide: Path to the slide file (optional).
        :param video: Path to the video file (optional).
        :param audio_length: Length of the audio in seconds (optional).
        :param audio: Path to the audio file (optional).
        """
        self.order = order
        self.speaker = speaker
        self.text = text
        self.slide = slide  # Path to the slide file
        self.video = video  # Path to the video file
        self.audio_length = audio_length  # Length of the audio in seconds
        self.audio = audio  # Path to the audio file

    def __repr__(self):
        return (f"Conversation(order={self.order}, speaker={self.speaker}, text='{self.text}', "
                f"slide='{self.slide}', video='{self.video}', audio_length={self.audio_length}, audio='{self.audio}')")


class NewWord:
    """Represents a single new word entry."""
    def __init__(self, order: int, word: str, meaning: str, example: str):
        self.order = order
        self.word = word
        self.meaning = meaning
        self.example = example

    def __repr__(self):
        return f"NewWord(order={self.order}, word='{self.word}', meaning='{self.meaning}', example='{self.example}')"


class Speaker:
    """Represents a single speaker."""
    def __init__(self, name: str, gender: str):
        self.name = name
        self.gender = gender

    def __repr__(self):
        return f"Speaker(name='{self.name}', gender='{self.gender}')"


class Conversations:
    """Represents the entire JSON structure."""
    def __init__(self, json_file: str):
        """Initialize the class by loading the JSON file."""
        with open(json_file, "r") as file:
            data = json.load(file)

        # Parse the JSON data
        self.topic = data.get("topic")
        self.description = data.get("description")
        self.title = data.get("title")
        self.audience = data.get("audience")
        self.level = data.get("level")
        self.category = data.get("category")
        self.language = data.get("language")
        self.hashtags = data.get("hashtags", [])

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
                slide=conv.get("slide"),
                video=conv.get("video"),
                audio_length=conv.get("audio_length"),
                audio=conv.get("audio")
            )
            for conv in data.get("conversations", [])
        ]

        # Parse new words
        self.new_words = [
            NewWord(**word) for word in data.get("new_words", [])
        ]

    def get_speaker(self, name: str) -> Speaker:
        """Return a Speaker object for the given name."""
        return self.speakers.get(name, Speaker(name=name, gender="unknown"))

    def get_conversations(self) -> List[Conversation]:
        """Return the conversation as a list of Conversation objects."""
        return self.conversations

    def get_new_words(self) -> List[NewWord]:
        """Return the new words as a list of NewWord objects."""
        return self.new_words