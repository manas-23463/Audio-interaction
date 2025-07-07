"""
Simple TTS Test Script
Test if ElevenLabs TTS and audio playback are working
"""

from elevenlabs_client import ElevenLabsClient
from config import Config

def test_tts():
    print("🧪 Testing ElevenLabs TTS...")
    
    # Initialize client
    client = ElevenLabsClient()
    
    # Test text
    test_text = "Hello! This is a test of the ElevenLabs text to speech system."
    
    print(f"🗣️ Converting text: '{test_text}'")
    
    try:
        # Generate audio
        audio_bytes = client.tts(test_text)
        print(f"✅ TTS successful! Generated {len(audio_bytes)} bytes of audio")
        
        # Test playback
        print("🔊 Playing audio...")
        client.play_audio(audio_bytes)
        print("✅ Audio playback completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_tts() 