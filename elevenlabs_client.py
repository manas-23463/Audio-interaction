"""
ElevenLabs Client Module
Handles STT, TTS, and voice management using the official ElevenLabs SDK
"""

from elevenlabs import client, voices, Voice
from elevenlabs.text_to_speech import client as tts_client
from elevenlabs.speech_to_text import client as stt_client
from config import Config

class ElevenLabsClient:
    def __init__(self):
        self.voice_id = Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)
        self.agent_id = Config.AGENT_ID
        self.voice = None
        self.client = client.ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        self._init_voice()

    def _init_voice(self):
        if Config.ENABLE_VOICE_CLONING:
            self.voice = self.clone_voice(Config.CLONED_VOICE_NAME)
        elif self.voice_id:
            # Create a simple voice object with the ID
            self.voice = type('Voice', (), {'voice_id': self.voice_id})()
        else:
            # Use default voice ID
            self.voice = type('Voice', (), {'voice_id': "21m00Tcm4TlvDq8ikWAM"})()

    def get_voice(self, voice_id: str) -> Voice:
        # Create a simple voice object with the ID
        return type('Voice', (), {'voice_id': voice_id})()

    def clone_voice(self, name: str) -> Voice:
        # This is a placeholder; actual voice cloning requires audio samples and API support
        # For demo, just return the default voice
        print(f"[INFO] Voice cloning requested for: {name}")
        return type('Voice', (), {'voice_id': "21m00Tcm4TlvDq8ikWAM"})()

    def tts(self, text: str) -> bytes:
        if not self.voice:
            raise ValueError("No voice selected")
        
        try:
            # Use higher quality PCM format with correct sample rate
            response = self.client.text_to_speech.convert(
                voice_id=self.voice.voice_id,
                text=text,
                model_id="eleven_turbo_v2",
                output_format="pcm_22050"  # 22.05kHz PCM format
            )
            
            # Convert generator to bytes
            audio_bytes = b""
            for chunk in response:
                audio_bytes += chunk
            
            print(f"🎵 Generated {len(audio_bytes)} bytes of PCM audio")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            raise

    def stt(self, audio: bytes) -> str:
        # Save audio to temporary file for STT
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            temp_file = f.name
        
        try:
            # Open the file and pass it to the API
            with open(temp_file, 'rb') as audio_file:
                response = self.client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1"
                )
            return response.text
        finally:
            os.unlink(temp_file) 