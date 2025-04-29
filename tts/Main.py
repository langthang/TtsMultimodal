from tts.TextToSpeechProcessor import TextToSpeechProcessor

if __name__ == "__main__":
    # Initialize the processor with the JSON file path
    processor = TextToSpeechProcessor("data/breakfast01/breakfast01_short.json")
    processor.run()