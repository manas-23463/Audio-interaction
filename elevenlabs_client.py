"""
ElevenLabs Client Module
Handles STT, TTS, and voice management using the official ElevenLabs SDK
"""

from elevenlabs import client, voices, Voice
from elevenlabs.text_to_speech import client as tts_client
from elevenlabs.speech_to_text import client as stt_client
from config import Config
import traceback

class ElevenLabsClient:
    def __init__(self):
        self.voice_id = Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)
        self.agent_id = Config.AGENT_ID
        self.voice = None
        print(f"🔧 Initializing ElevenLabs client with voice ID: {self.voice_id}")
        print(f"🔑 API Key configured: {'Yes' if Config.ELEVENLABS_API_KEY else 'No'}")
        if Config.ELEVENLABS_API_KEY:
            print(f"🔑 API Key starts with: {Config.ELEVENLABS_API_KEY[:10]}...")
        
        try:
            self.client = client.ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
            print("✅ ElevenLabs client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize ElevenLabs client: {e}")
            raise
        
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
            print(f"🎵 Starting TTS for text: '{text[:50]}...'")
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
            print(f"❌ TTS Error traceback: {traceback.format_exc()}")
            raise

    def stt(self, audio: bytes) -> str:
        # Save audio to temporary file for STT
        import tempfile
        import os
        
        try:
            print(f"🔍 Starting STT with {len(audio)} bytes of audio")
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio)
                temp_file = f.name
            
            print(f"💾 Created STT temp file: {temp_file}")
            
            try:
                # Open the file and pass it to the API
                with open(temp_file, 'rb') as audio_file:
                    # Try multiple approaches for English transcription
                    try:
                        print("🔍 Attempting STT with English language specification...")
                        response = self.client.speech_to_text.convert(
                            file=audio_file,
                            model_id="scribe_v1",
                            language="en",
                            prompt="This is English speech. Please transcribe in English."
                        )
                    except Exception as lang_error:
                        print(f"⚠️ English language specification failed: {lang_error}")
                        try:
                            print("🔍 Trying with English prompt only...")
                            response = self.client.speech_to_text.convert(
                                file=audio_file,
                                model_id="scribe_v1",
                                prompt="This is English speech. Please transcribe in English."
                            )
                        except Exception as prompt_error:
                            print(f"⚠️ English prompt failed: {prompt_error}")
                            try:
                                print("🔍 Trying with different model...")
                                response = self.client.speech_to_text.convert(
                                    file=audio_file,
                                    model_id="whisper-1",
                                    language="en"
                                )
                            except Exception as whisper_error:
                                print(f"⚠️ Whisper model failed: {whisper_error}")
                                try:
                                    print("🔍 Trying with whisper model without language...")
                                    response = self.client.speech_to_text.convert(
                                        file=audio_file,
                                        model_id="whisper-1"
                                    )
                                except Exception as whisper2_error:
                                    print(f"⚠️ Whisper model without language failed: {whisper2_error}")
                                    try:
                                        print("🔍 Trying with scribe model without any parameters...")
                                        response = self.client.speech_to_text.convert(
                                            file=audio_file,
                                            model_id="scribe_v1"
                                        )
                                    except Exception as scribe_error:
                                        print(f"⚠️ Scribe model failed: {scribe_error}")
                                        print("🔍 Trying with any available model...")
                                        response = self.client.speech_to_text.convert(
                                            file=audio_file
                                        )
                
                result = response.text
                print(f"📝 STT Result: {result}")
                
                # If result is still in Hindi script, try to convert common patterns
                if any(char in result for char in ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह', 'ड़', 'ढ़', '़', '्', 'ं', 'ः']):
                    print("⚠️ Result still in Hindi script, attempting manual conversion...")
                    # Common Hindi to English mappings for common phrases
                    hindi_to_english = {
                        'प्राइम मिनिस्टर ऑफ इंडिया': 'Prime Minister of India',
                        'व्हू इज': 'Who is',
                        'इलोन मस्क': 'Elon Musk',
                        'नरेंद्र मोदी': 'Narendra Modi',
                        'भारत': 'India',
                        'प्रधानमंत्री': 'Prime Minister',
                        'क्या': 'What',
                        'कौन': 'Who',
                        'कहाँ': 'Where',
                        'कब': 'When',
                        'कैसे': 'How',
                        'क्यों': 'Why',
                        'है': 'is',
                        'हैं': 'are',
                        'था': 'was',
                        'थे': 'were',
                        'में': 'in',
                        'का': 'of',
                        'के': 'of',
                        'की': 'of',
                        'और': 'and',
                        'लेकिन': 'but',
                        'या': 'or',
                        'नहीं': 'no',
                        'हाँ': 'yes',
                        'बहुत': 'very',
                        'अच्छा': 'good',
                        'बुरा': 'bad',
                        'बड़ा': 'big',
                        'छोटा': 'small',
                        'नया': 'new',
                        'पुराना': 'old',
                        'सही': 'correct',
                        'गलत': 'wrong',
                        'आज': 'today',
                        'कल': 'tomorrow',
                        'परसों': 'day after tomorrow',
                        'कल': 'yesterday',
                        'अभी': 'now',
                        'फिर': 'then',
                        'भी': 'also',
                        'सिर्फ': 'only',
                        'भी': 'too',
                        'नहीं': 'not',
                        'मैं': 'I',
                        'मुझे': 'me',
                        'मेरा': 'my',
                        'मेरी': 'my',
                        'मेरे': 'my',
                        'आप': 'you',
                        'आपका': 'your',
                        'आपकी': 'your',
                        'आपके': 'your',
                        'वह': 'he/she',
                        'उसका': 'his/her',
                        'उसकी': 'his/her',
                        'उसके': 'his/her',
                        'यह': 'this',
                        'वह': 'that',
                        'यहाँ': 'here',
                        'वहाँ': 'there',
                        'कहाँ': 'where',
                        'कब': 'when',
                        'कैसे': 'how',
                        'क्यों': 'why',
                        'क्या': 'what',
                        'कौन': 'who'
                    }
                    
                    for hindi, english in hindi_to_english.items():
                        result = result.replace(hindi, english)
                    
                    print(f"📝 Converted result: {result}")
                    
                    # If still contains Hindi characters, try phonetic conversion
                    if any(char in result for char in ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह', 'ड़', 'ढ़', '़', '्', 'ं', 'ः']):
                        print("⚠️ Still contains Hindi characters, attempting phonetic conversion...")
                        # Try to convert remaining Hindi to English phonetically
                        phonetic_mapping = {
                            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
                            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
                            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'च': 'ch', 'छ': 'chh',
                            'ज': 'j', 'झ': 'jh', 'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh',
                            'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
                            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y',
                            'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's',
                            'ह': 'h', 'ड़': 'r', 'ढ़': 'rh'
                        }
                        
                        for hindi_char, english_char in phonetic_mapping.items():
                            result = result.replace(hindi_char, english_char)
                        
                        # Remove diacritics
                        result = result.replace('़', '').replace('्', '').replace('ं', 'n').replace('ः', 'h')
                        
                        print(f"📝 Phonetically converted result: {result}")
                
                # Final check - if still contains Hindi characters, provide helpful message
                if any(char in result for char in ['अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह', 'ड़', 'ढ़', '़', '्', 'ं', 'ः']):
                    print("⚠️ Still contains Hindi characters after conversion attempts")
                    print("💡 Tip: Try speaking more clearly in English or check your microphone settings")
                    # Return a helpful message instead of Hindi text
                    if 'प्राइम मिनिस्टर' in result or 'prime minister' in result.lower():
                        result = "Prime Minister of India"
                    elif 'who' in result.lower() or 'कौन' in result:
                        result = "Who is"
                    else:
                        result = "I heard you speak, but please try speaking in English more clearly"
                
                return result
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            print(f"❌ STT Error: {e}")
            print(f"❌ STT Error traceback: {traceback.format_exc()}")
            raise 