from tts.Conversations import Conversations

# Load the JSON file
conversation_data = Conversations("tts/data/breakfast01/breakfast01_short.json")

# Access speakers
print("Speakers:")
for name, speaker in conversation_data.speakers.items():
    print(speaker)

# Get specific speaker details
print("\nAnna's Details:", conversation_data.get_speaker("Anna"))
print("Tom's Details:", conversation_data.get_speaker("Tom"))
print("Unknown Speaker:", conversation_data.get_speaker("Unknown"))

# Access conversations
print("\nConversations:")
for conv in conversation_data.get_conversations():
    print(conv)

# Access specific speaker details
print("\nAnna's Details:", conversation_data.get_speaker("Anna"))
print("Tom's Details:", conversation_data.get_speaker("Tom"))

# Access new words
print("\nNew Words:")
for word in conversation_data.get_new_words():
    print(word)