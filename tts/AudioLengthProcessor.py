import os
import json
from mutagen.mp3 import MP3


class AudioLengthProcessor:
    def __init__(self, json_file: str):
        """Initialize the processor with the JSON file path."""
        self.json_file = json_file
        self.json_dir = os.path.dirname(json_file)
        self.audios_dir = os.path.join(self.json_dir, "audio_conversations")

    def calculate_audio_lengths(self) -> dict:
        """Calculate the length of each audio file in the audios directory."""
        audio_lengths = {}
        if not os.path.exists(self.audios_dir):
            raise FileNotFoundError(f"The directory {self.audios_dir} does not exist.")

        for audio_file in os.listdir(self.audios_dir):
            if audio_file.endswith(".mp3"):
                audio_path = os.path.join(self.audios_dir, audio_file)
                audio = MP3(audio_path)
                # Convert length to milliseconds
                audio_lengths[audio_file] = int(audio.info.length * 1000)  # Length in milliseconds

        return audio_lengths

    def update_json_with_audio_lengths(self):
        """Update the JSON file with audio lengths for each conversation."""
        # Load the JSON file
        with open(self.json_file, "r") as file:
            data = json.load(file)

        # Calculate audio lengths
        audio_lengths = self.calculate_audio_lengths()

        # Update each conversation with the audio length
        for conversation in data.get("conversations", []):
            order = conversation["order"]
            speaker = conversation["speaker"]
            audio_file_name = f"{order}_{speaker}.mp3"
            conversation["audio_length"] = audio_lengths.get(audio_file_name, 0)  # Default to 0 if not found

        # Generate the new file name
        new_file_name = os.path.splitext(self.json_file)[0] + "_withlength.json"

        # Save the updated JSON data to the new file
        with open(new_file_name, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Generated {new_file_name} with audio lengths.")