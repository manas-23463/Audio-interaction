from flask import Flask, render_template, request, jsonify
import base64
import wave
import tempfile
import os
import traceback
import gc
import psutil
from elevenlabs_client import ElevenLabsClient
from openai_client import OpenAIClient
from conversation_logger import ConversationLogger
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize clients
elevenlabs_client = ElevenLabsClient()
openai_client = OpenAIClient()
conversation_logger = ConversationLogger()

def log_memory_usage():
    """Log current memory usage"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"💾 Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

@app.route('/')
def index():
    return render_template('index_simple.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        log_memory_usage()
        
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        print(f"🔍 Processing audio request - data size: {len(data['audio'])}")
        
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'])
        print(f"🎵 Decoded audio size: {len(audio_data)} bytes")
        
        # Limit audio size to prevent memory issues
        if len(audio_data) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({'error': 'Audio file too large'}), 400
        
        # Create temporary WAV file
        temp_file_path = None
        temp_audio_path = None
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            print(f"💾 Created temp file: {temp_file_path}")
            
            # Transcribe audio
            print("🔎 Starting STT...")
            with open(temp_file_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            transcript = elevenlabs_client.stt(audio_bytes)
            print(f"📝 Transcript: {transcript}")
            
            # Clear audio bytes from memory
            del audio_bytes
            gc.collect()
            
            if not transcript or not transcript.strip():
                return jsonify({'error': 'No speech detected'}), 400
            
            # Log user input
            conversation_logger.log('User', transcript)
            
            # Generate AI response
            print("🤖 Generating AI response...")
            response = openai_client.ask(transcript)
            print(f"🤖 AI Response: {response}")
            conversation_logger.log('AI', response)
            
            # Generate speech
            print("🗣️ Generating speech...")
            tts_audio_bytes = elevenlabs_client.tts(response)
            print(f"🎵 Generated {len(tts_audio_bytes)} bytes of audio")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                # Create proper WAV file from PCM data
                with wave.open(temp_audio.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(22050)  # 22.05kHz sample rate
                    wav_file.writeframes(tts_audio_bytes)
                temp_audio_path = temp_audio.name
            
            print(f"💾 Created audio file: {temp_audio_path}")
            
            # Read audio file and encode to base64
            with open(temp_audio_path, 'rb') as audio_file:
                final_audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(final_audio_bytes).decode('utf-8')
            
            # Clear audio data from memory
            del tts_audio_bytes, final_audio_bytes
            gc.collect()
            
            print(f"✅ Successfully processed request")
            log_memory_usage()
            
            return jsonify({
                'transcript': transcript,
                'response': response,
                'audio': audio_base64
            })
            
        finally:
            # Clean up temporary files
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            # Force garbage collection
            gc.collect()
            
    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        log_memory_usage()
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    openai_client.reset_history()
    conversation_logger.log('System', 'Conversation reset')
    gc.collect()  # Clean up memory
    return jsonify({'message': 'Conversation reset'})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        log_memory_usage()
        return jsonify({'status': 'healthy', 'memory_usage_mb': psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🌐 Starting simple web server...")
    print(f"🔧 Current Configuration:")
    print(f"  Voice Cloning: {'Enabled' if Config.ENABLE_VOICE_CLONING else 'Disabled'}")
    print(f"  Conversation Logging: {'Enabled' if Config.ENABLE_CONVERSATION_LOGGING else 'Disabled'}")
    log_memory_usage()
    print(f"🌐 Open http://localhost:{port} in your browser")
    app.run(debug=False, host='0.0.0.0', port=port) 