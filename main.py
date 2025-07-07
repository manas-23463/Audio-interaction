"""
Main Conversational AI Loop
Ties together audio, ElevenLabs, OpenAI, and logging for real-time two-way conversation
"""

import signal
import sys
from config import Config
from audio_handler import AudioHandler
from elevenlabs_client import ElevenLabsClient
from openai_client import OpenAIClient
from conversation_logger import ConversationLogger

# Initialize modules
audio_handler = AudioHandler()
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
    audio_handler.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("\n🗣️  Start speaking! (Press Ctrl+C to exit)")

# Main conversational loop
def on_audio_data(audio_bytes):
    print("🔎 Transcribing...")
    try:
        user_text = elevenlabs_client.stt(audio_bytes)
        print(f"👤 You: {user_text}")
        logger.log("User", user_text)
        print("🤖 Generating response...")
        ai_text = openai_client.ask(user_text)
        print(f"🤖 AI: {ai_text}")
        logger.log("AI", ai_text)
        print("🗣️  Speaking...")
        ai_audio = elevenlabs_client.tts(ai_text)
        elevenlabs_client.play_audio(ai_audio)
    except Exception as e:
        print(f"❌ Error in conversation loop: {e}")

try:
    audio_handler.start_recording(on_audio_data)
    while running:
        signal.pause()  # Wait for signals (Ctrl+C)
except KeyboardInterrupt:
    signal_handler(None, None) 