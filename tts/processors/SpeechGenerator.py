# tts/processors/SpeechGenerator.py
import os
from mutagen.mp3 import MP3
from AppConfig import AppConfig
from GoogleTextToSpeech import GoogleTextToSpeech
#from pydub import AudioSegment

class SpeechGenerator:
    def __init__(self, google_tts: GoogleTextToSpeech):
        self.google_tts = google_tts
        self.config = AppConfig()

    def generate_speech(self, sleep: int, text: str, output_file: str, voice_name: str, gender: str, language_code: str, speaking_rate: float = 1.0) -> tuple[str, int]:
        """Generate speech from text and return the file path and duration."""
        self.google_tts.synthesize_speech(
            text=text,
            output_filename=output_file,
            voice_name=voice_name,
            gender=gender,
            language_code=language_code,
            speaking_rate=speaking_rate
        )

        audio = MP3(output_file)
        if not sleep:
            sleep = 0
        audio_length = int((audio.info.length + sleep) * 1000)  # Length in milliseconds
        print(f"Real length: {audio.info.length}, Generated audio length: {audio_length} ms for file: {output_file} and sleep {sleep}")
        # if sleep and sleep > 0:
        #     audio = AudioSegment.from_file(output_file, format="mp3")
        #     silence = AudioSegment.silent(duration=int(sleep * 1000))
        #     combined = audio + silence
        #     combined.export(output_file, format="mp3")

        # audio = MP3(output_file)
        # audio_length = int(audio.info.length * 1000)  # Length in milliseconds
        # print(f"Extended audio length: {audio_length} ms for file: {output_file}")
        return output_file, audio_length