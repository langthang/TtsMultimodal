from google.cloud import texttospeech
from tts.TextToSpeechService import TextToSpeechService

class GoogleTextToSpeech(TextToSpeechService):
    """Implementation of TextToSpeechService using Google Cloud Text-to-Speech."""

    def synthesize_speech(
        self, 
        text: str, 
        output_filename: str, 
        voice_name: str = "en-US-Wavenet-F", 
        gender: str = "FEMALE", 
        language_code: str = "en-US"
    ):
        # Initialize the Text-to-Speech client
        client = texttospeech.TextToSpeechClient()

        # Configure the input text
        input_text = texttospeech.SynthesisInput(text=text)

        # Map gender string to SsmlVoiceGender enum
        gender_enum = {
            "FEMALE": texttospeech.SsmlVoiceGender.FEMALE,
            "MALE": texttospeech.SsmlVoiceGender.MALE,
            "NEUTRAL": texttospeech.SsmlVoiceGender.NEUTRAL
        }.get(gender.upper(), texttospeech.SsmlVoiceGender.FEMALE)

        # Configure the voice settings
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,  # Use the provided language code
            name=voice_name,  # Specific voice name
            ssml_gender=gender_enum
        )

        # Configure the audio settings
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3  # Output format
        )

        # Synthesize speech
        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )

        # Save the audio to the specified file
        with open(output_filename, "wb") as audio_file:
            audio_file.write(response.audio_content)
        print(f"Google TTS: Audio content written to file: {output_filename}")