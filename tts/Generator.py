import os
import sys
from TextToSpeechProcessor import TextToSpeechProcessor
from AppConfig import AppConfig

def get_project_root():
    """Get the absolute path to the project root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def main():
    """Main entry point of the application."""
    try:
        # Check for command-line argument
        if len(sys.argv) <= 2:
            print("Usage: python Main.py <conversation_id_or_json_file> [speaking_rate]")
            return
        
        conversation_id_or_json_file = sys.argv[1]
        if conversation_id_or_json_file.lower().endswith('.json') and not os.path.isfile(conversation_id_or_json_file):
            print(f"JSON file not found: {conversation_id_or_json_file}")
            return

        # Read speaking_rate from sys.argv if provided
        speaking_rate = 1.0
        if len(sys.argv) > 2:
            try:
                speaking_rate = float(sys.argv[2])
            except ValueError:
                print(f"Invalid speaking_rate '{sys.argv[2]}', using default 1.0")

        # Initialize configuration
        config = AppConfig()
        
        # Initialize the processor with the JSON file path and speaking_rate
        processor = TextToSpeechProcessor(conversation_id_or_json_file, speaking_rate=speaking_rate)
        processor.generate()
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()