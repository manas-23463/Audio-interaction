# Two-Way Conversational AI with ElevenLabs

A real-time, two-way conversational AI system that enables natural voice interactions using ElevenLabs TTS/STT and OpenAI's conversational AI.

## Features

- 🎤 **Real-time microphone input** with automatic speech detection
- 🗣️ **Natural-sounding TTS** using ElevenLabs voice synthesis
- 🔍 **Speech-to-text** using ElevenLabs STT service
- 🤖 **Conversational AI** responses using OpenAI GPT
- 📝 **Conversation logging** for later review
- 🎛️ **Configurable** voice selection and settings
- 🔄 **Low-latency** real-time conversation loop
- 🌐 **Web interface** with modern UI
- 🛑 **Graceful shutdown** with Ctrl+C

## Prerequisites

- Python 3.10+ (recommended)
- macOS (tested on macOS 14+) for local CLI version
- Working microphone and speakers/headphones
- ElevenLabs API key with TTS and STT permissions
- OpenAI API key

## Installation

1. **Clone or download this project**
   ```bash
   cd AUDIO_INTERACTION
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies** (if needed)
   ```bash
   # On macOS
   brew install portaudio
   ```

4. **Configure your API keys**
   ```bash
   cp config.env.example .env
   # Edit .env and add your API keys
   ```

## Configuration

Edit the `.env` file with your API keys and preferences:

```env
# Required API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional Settings
AGENT_ID=your_agent_id_here
VOICE_ID=your_voice_id_here

# Audio Settings
SAMPLE_RATE=44100
CHUNK_SIZE=1024
CHANNELS=1

# Optional Features
ENABLE_VOICE_CLONING=false
ENABLE_CONVERSATION_LOGGING=true
LOG_FILE_PATH=conversation_log.txt
```

### API Key Setup

**ElevenLabs API Key:**
- Sign up at [ElevenLabs](https://elevenlabs.io/)
- Create an API key with access to:
  - Text-to-Speech (TTS)
  - Speech-to-Text (STT)
  - Voice selection (optional)

**OpenAI API Key:**
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Create an API key for GPT-3.5/4 access

## Usage

### Web Interface (Recommended)
```bash
python app.py
```
- Open http://localhost:8080 in your browser
- Click and hold the microphone button to speak
- Modern, responsive web interface
- Works on desktop and mobile devices

### Real-time Voice Conversation (CLI)
```bash
python main.py
```
- Speak into your microphone
- The AI will transcribe, respond, and speak back
- Press Ctrl+C to exit

### Text-based Conversation (Testing)
```bash
python main_simple.py
```
- Type your messages and press Enter
- Good for testing TTS and OpenAI integration
- Type 'quit' to exit

## Deployment on Render

This application can be deployed on Render as a web service. The web interface is optimized for cloud deployment.

### Quick Deploy

1. **Fork or clone this repository** to your GitHub account

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service:**
   - **Name**: `audio-interaction-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT`

4. **Set Environment Variables:**
   - `ELEVENLABS_API_KEY`: Your ElevenLabs API key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: A random secret key for Flask

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Environment Variables for Render

Set these in your Render dashboard:

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_random_secret_key_here
AGENT_ID=
VOICE_ID=
SAMPLE_RATE=44100
CHUNK_SIZE=1024
CHANNELS=1
ENABLE_VOICE_CLONING=false
ENABLE_CONVERSATION_LOGGING=true
LOG_FILE_PATH=conversation_log.txt
```

### Deployment Files

The following files are included for Render deployment:
- `render.yaml` - Render configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version specification
- Updated `requirements.txt` with production dependencies

## Project Structure

```
AUDIO_INTERACTION/
├── main.py                 # Main voice conversation application (CLI)
├── app.py                  # Web application (Flask + SocketIO)
├── main_simple.py          # Text-based conversation for testing
├── config.py              # Configuration management
├── audio_handler.py       # Microphone input and audio playback (CLI only)
├── elevenlabs_client.py   # ElevenLabs TTS/STT integration
├── openai_client.py       # OpenAI conversational AI
├── conversation_logger.py # Conversation logging
├── requirements.txt       # Python dependencies
├── config.env.example     # Example configuration
├── render.yaml            # Render deployment configuration
├── Procfile               # Process definition for Render
├── runtime.txt            # Python version for Render
├── .env                   # Your configuration (create this)
├── templates/             # Web interface templates
│   └── index.html        # Main web page
├── static/               # Web assets
│   ├── css/style.css     # Styling
│   └── js/app.js         # Frontend JavaScript
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **"API key missing permissions"**
   - Ensure your ElevenLabs API key has TTS and STT permissions
   - Check your OpenAI API key is valid

2. **"File upload is corrupted"**
   - The microphone audio format issue is being worked on
   - Use `main_simple.py` for text-based testing

3. **"portaudio.h not found"**
   - Install portaudio: `brew install portaudio`

4. **"Client.__init__() got unexpected keyword argument 'proxies'"**
   - This is a dependency version conflict
   - Run: `pip install -r requirements.txt --force-reinstall`

5. **Microphone not working**
   - Check system permissions for microphone access
   - Ensure microphone is not muted
   - Try adjusting `SILENCE_THRESHOLD` in audio_handler.py

6. **WebSocket connection issues on Render**
   - The app uses eventlet for WebSocket support
   - Ensure all environment variables are set correctly
   - Check Render logs for any errors

### Audio Settings

You can adjust audio settings in the `.env` file:

- `SAMPLE_RATE`: Audio sample rate (default: 44100)
- `CHUNK_SIZE`: Audio processing chunk size (default: 1024)
- `CHANNELS`: Number of audio channels (default: 1)

### Voice Selection

To use a specific voice:
1. Get your voice ID from ElevenLabs dashboard
2. Set `VOICE_ID=your_voice_id` in `.env`
3. Or leave empty to use default voice

## Development

### Adding New Features

- **Voice Cloning**: Implement in `elevenlabs_client.py`
- **Custom Voices**: Add voice management functions
- **Different LLMs**: Modify `openai_client.py`
- **Audio Effects**: Extend `audio_handler.py`

### Testing

```bash
# Test audio format
python test_audio.py

# Test text conversation
python main_simple.py

# Test full voice conversation
python main.py

# Test web interface
python app.py
```

## Logs

Conversations are logged to `conversation_log.txt` by default:
```
--- New Conversation Session: 2025-06-25 11:30:00 ---
[2025-06-25 11:30:05] User: Hello, how are you?
[2025-06-25 11:30:08] AI: I'm doing well, thank you for asking!
```

## License

This project is for educational and personal use. Please respect the terms of service for ElevenLabs and OpenAI APIs.

## Support

For issues:
1. Check the troubleshooting section above
2. Verify your API keys and permissions
3. Test with `main_simple.py` first
4. Check the conversation logs for errors
5. For deployment issues, check Render logs

## Contributing

Feel free to submit issues and enhancement requests! 