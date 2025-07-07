"""
Configuration module for ElevenLabs Conversational AI
Handles environment variables and application settings
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the conversational AI system"""
    
    # ElevenLabs API Configuration
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Conversational AI Settings
    AGENT_ID: str = os.getenv("AGENT_ID", "")
    VOICE_ID: str = os.getenv("VOICE_ID", "")
    
    # Audio Settings
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "44100"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1024"))
    CHANNELS: int = int(os.getenv("CHANNELS", "1"))
    
    # Voice Cloning Settings
    ENABLE_VOICE_CLONING: bool = os.getenv("ENABLE_VOICE_CLONING", "false").lower() == "true"
    CLONED_VOICE_NAME: str = os.getenv("CLONED_VOICE_NAME", "my_cloned_voice")
    
    # Logging Settings
    ENABLE_CONVERSATION_LOGGING: bool = os.getenv("ENABLE_CONVERSATION_LOGGING", "true").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "conversation_log.txt")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        required_fields = [
            ("ELEVENLABS_API_KEY", cls.ELEVENLABS_API_KEY),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing_fields = []
        for field_name, field_value in required_fields:
            if not field_value:
                missing_fields.append(field_name)
        
        if missing_fields:
            print(f"❌ Missing required configuration: {', '.join(missing_fields)}")
            print("Please set these environment variables or add them to your .env file")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("🔧 Current Configuration:")
        print(f"  Sample Rate: {cls.SAMPLE_RATE} Hz")
        print(f"  Chunk Size: {cls.CHUNK_SIZE}")
        print(f"  Channels: {cls.CHANNELS}")
        print(f"  Voice Cloning: {'Enabled' if cls.ENABLE_VOICE_CLONING else 'Disabled'}")
        print(f"  Conversation Logging: {'Enabled' if cls.ENABLE_CONVERSATION_LOGGING else 'Disabled'}")
        if cls.AGENT_ID:
            print(f"  Agent ID: {cls.AGENT_ID}")
        if cls.VOICE_ID:
            print(f"  Voice ID: {cls.VOICE_ID}") 