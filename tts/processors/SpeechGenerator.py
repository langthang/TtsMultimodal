# tts/processors/SpeechGenerator.py
import os
from mutagen.mp3 import MP3
from AppConfig import AppConfig
from GoogleTextToSpeech import GoogleTextToSpeech

class SpeechGenerator:
    def __init__(self, google_tts: GoogleTextToSpeech):
        self.google_tts = google_tts
        self.config = AppConfig()

    def generate_speech(self, text: str, output_file: str, voice_name: str, gender: str, language_code: str) -> tuple[str, int]:
        """Generate speech from text and return the file path and duration."""
        self.google_tts.synthesize_speech(
            text=text,
            output_filename=output_file,
            voice_name=voice_name,
            gender=gender,
            language_code=language_code
        )

        audio = MP3(output_file)
        audio_length = int(audio.info.length * 1000)  # Length in milliseconds
        
        return output_file, audio_length