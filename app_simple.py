from flask import Flask, render_template, request, jsonify
import base64
import wave
import tempfile
import os
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

@app.route('/')
def index():
    return render_template('index_simple.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'])
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            with open(temp_file_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            transcript = elevenlabs_client.stt(audio_bytes)
            
            if not transcript or not transcript.strip():
                return jsonify({'error': 'No speech detected'}), 400
            
            # Log user input
            conversation_logger.log('User', transcript)
            
            # Generate AI response
            response = openai_client.ask(transcript)
            conversation_logger.log('AI', response)
            
            # Generate speech
            audio_bytes = elevenlabs_client.tts(response)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                # Create proper WAV file from PCM data
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
            
            # Clean up temporary audio file
            os.unlink(audio_file_path)
            
            return jsonify({
                'transcript': transcript,
                'response': response,
                'audio': audio_base64
            })
            
        finally:
            # Clean up temporary input file
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"Error processing audio: {e}")
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    openai_client.reset_history()
    conversation_logger.log('System', 'Conversation reset')
    return jsonify({'message': 'Conversation reset'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🌐 Starting simple web server...")
    print(f"🔧 Current Configuration:")
    print(f"  Voice Cloning: {'Enabled' if Config.ENABLE_VOICE_CLONING else 'Disabled'}")
    print(f"  Conversation Logging: {'Enabled' if Config.ENABLE_CONVERSATION_LOGGING else 'Disabled'}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    app.run(debug=False, host='0.0.0.0', port=port) 