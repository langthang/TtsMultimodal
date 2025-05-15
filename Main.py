# #!/usr/bin/env python3
# import os
# import sys
# import argparse
# from dotenv import load_dotenv
# from tts.TextToSpeechProcessor2 import TextToSpeechProcessor2
# from tts.config.YouTubeConfig import YouTubeConfig

# def is_valid_json_file(path):
#     """Check if the path is a valid JSON file."""
#     return path.endswith('.json') and os.path.isfile(path)

# def is_valid_conversation_id(id_str):
#     """Check if the string could be a valid MongoDB ObjectId."""
#     from bson.objectid import ObjectId
#     try:
#         ObjectId(id_str)
#         return True
#     except:
#         return False

# def main():
#     # Load environment variables
#     load_dotenv()

#     # Set up argument parser
#     parser = argparse.ArgumentParser(description='Process conversations and upload to YouTube')
#     parser.add_argument('source', help='Path to JSON file or conversation ID')
#     # parser.add_argument('--privacy', choices=['private', 'unlisted', 'public'], 
#     #                    default='private', help='YouTube video privacy status')
    
#     args = parser.parse_args()

#     try:
#         # Determine if the source is a JSON file or conversation ID
#         if is_valid_json_file(args.source):
#             print(f"Processing JSON file: {args.source}")
#             source = args.source
#         elif is_valid_conversation_id(args.source):
#             print(f"Processing conversation ID: {args.source}")
#             source = args.source
#         else:
#             raise ValueError("Invalid source. Must be either a .json file path or a valid conversation ID")

#         # Initialize YouTube config to ensure environment variables are set
#         youtube_config = YouTubeConfig()
#         if not youtube_config.is_initialized:
#             raise ValueError("YouTube configuration not properly initialized. Check your .env file.")

#         # Initialize and run the processor
#         processor = TextToSpeechProcessor2(source)
        
#         # Process the conversations and generate videos
#         print("Processing conversations and generating videos...")
#         processor.run()
#         print("Processing and upload complete!")

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main() 