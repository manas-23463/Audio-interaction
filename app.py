from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import base64
import io
import wave
import threading
import time
from elevenlabs_client import ElevenLabsClient
from openai_client import OpenAIClient
from conversation_logger import ConversationLogger
from config import Config
import tempfile
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Initialize clients
elevenlabs_client = ElevenLabsClient()
openai_client = OpenAIClient()
conversation_logger = ConversationLogger()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio_data(data):
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'])
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            emit('status', {'message': '🔎 Transcribing...'})
            with open(temp_file_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            transcript = elevenlabs_client.stt(audio_bytes)
            
            if transcript and transcript.strip():
                emit('transcript', {'text': transcript})
                conversation_logger.log('User', transcript)
                
                # Generate AI response
                emit('status', {'message': '🤖 Generating response...'})
                response = openai_client.ask(transcript)
                emit('ai_response', {'text': response})
                conversation_logger.log('AI', response)
                
                # Generate speech
                emit('status', {'message': '🗣️ Generating speech...'})
                audio_bytes = elevenlabs_client.tts(response)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    # Create proper WAV file from PCM data
                    import wave
                    with wave.open(temp_audio.name, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(22050)  # 22.05kHz sample rate
                        wav_file.writeframes(audio_bytes)
                    audio_file_path = temp_audio.name
                
                # Read audio file and encode to base64
                with open(audio_file_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                emit('audio_response', {'audio': audio_base64})
                
                # Clean up temporary audio file
                os.unlink(audio_file_path)
                
        finally:
            # Clean up temporary input file
            os.unlink(temp_file_path)
            
    except Exception as e:
        emit('error', {'message': f'Error processing audio: {str(e)}'})

@socketio.on('reset_conversation')
def handle_reset():
    openai_client.reset_history()
    # Log the conversation reset
    conversation_logger.log('System', 'Conversation reset')
    emit('status', {'message': '🔄 Conversation reset'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🌐 Starting web server...")
    print(f"🔧 Current Configuration:")
    print(f"  Voice Cloning: {'Enabled' if Config.ENABLE_VOICE_CLONING else 'Disabled'}")
    print(f"  Conversation Logging: {'Enabled' if Config.ENABLE_CONVERSATION_LOGGING else 'Disabled'}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    socketio.run(app, debug=False, host='0.0.0.0', port=port) 