from tts.AudioLengthProcessor import AudioLengthProcessor

"""Process audio lengths for the audio_conversations folder."""
json_file_path = "tts/data/breakfast01/breakfast01_short.json"
audio_processor = AudioLengthProcessor(json_file_path)
audio_processor.update_json_with_audio_lengths()