from abc import ABC, abstractmethod

class TextToSpeechService(ABC):
    """Abstract base class for text-to-speech services."""

    @abstractmethod
    def synthesize_speech(
        self, 
        text: str, 
        output_filename: str, 
        voice_name: str = "en-US-Wavenet-F", 
        gender: str = "FEMALE", 
        language_code: str = "en-US"
    ):
        """Synthesizes speech from input text and saves to an audio file."""
        pass