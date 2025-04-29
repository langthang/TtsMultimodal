from google.cloud import texttospeech

def synthesize_speech(text, output_filename):
    """Synthesizes speech from input text and saves to an audio file."""
    # Initialize the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Configure the input text
    input_text = texttospeech.SynthesisInput(text=text)

    # Configure the voice settings
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",  # Change to your preferred language
        name="en-US-Wavenet-F",  # Specific female voice
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
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
    print(f"Audio content written to file: {output_filename}")

# Example usage
if __name__ == "__main__":
    text_to_speak = "Hello, how can I assist you today?"
    output_file = "output.mp3"
    synthesize_speech(text_to_speak, output_file)
