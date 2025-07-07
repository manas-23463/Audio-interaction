"""
Simplified Main Conversational AI Loop
A simpler version for testing the conversation flow
"""

import signal
import sys
from config import Config
from elevenlabs_client import ElevenLabsClient
from openai_client import OpenAIClient
from conversation_logger import ConversationLogger

# Initialize modules
elevenlabs_client = ElevenLabsClient()
openai_client = OpenAIClient()
logger = ConversationLogger()

# Print config for user
Config.print_config()

# Graceful shutdown
running = True
def signal_handler(sig, frame):
    global running
    print("\n👋 Exiting. Cleaning up...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("\n🗣️  Simple Text-based Conversation Mode")
print("Type your message and press Enter (or 'quit' to exit)")

# Simple text-based conversation loop
while running:
    try:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        if not user_input:
            continue
            
        print("🤖 Generating response...")
        ai_response = openai_client.ask(user_input)
        print(f"🤖 AI: {ai_response}")
        
        print("🗣️  Speaking...")
        ai_audio = elevenlabs_client.tts(ai_response)
        elevenlabs_client.play_audio(ai_audio)
        
        # Log the conversation
        logger.log("User", user_input)
        logger.log("AI", ai_response)
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"❌ Error in conversation loop: {e}")

print("👋 Goodbye!") 