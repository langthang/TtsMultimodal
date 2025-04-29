from tts.TextToSlideProcessor import TextToSlideProcessor

# Path to the JSON file
json_file_path = "tts/data/breakfast01/breakfast01_short.json"

# Process slides for conversations
slide_processor = TextToSlideProcessor(json_file_path)
slide_processor.run()