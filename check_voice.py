"""
Check Current Voice Configuration
"""

from config import Config
from elevenlabs_client import ElevenLabsClient

def check_voice():
    print("🎤 Current Voice Configuration:")
    print(f"  Voice ID from config: {Config.VOICE_ID}")
    
    client = ElevenLabsClient()
    print(f"  Actual voice ID being used: {client.voice_id}")
    print(f"  Voice object: {client.voice.voice_id if client.voice else 'None'}")
    
    if client.voice_id == "21m00Tcm4TlvDq8ikWAM":
        print("  🗣️ Using default voice: Rachel")
    else:
        print(f"  🗣️ Using custom voice: {client.voice_id}")

if __name__ == "__main__":
    check_voice() 