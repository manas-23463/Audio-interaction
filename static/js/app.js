class VoiceChatApp {
    constructor() {
        this.socket = io({
            transports: ['websocket', 'polling'],
            timeout: 20000,
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupSocketListeners();
        this.requestMicrophonePermission();
    }

    initializeElements() {
        this.recordBtn = document.getElementById('recordBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.statusText = document.getElementById('statusText');
        this.chatMessages = document.getElementById('chatMessages');
        this.audioVisualizer = document.getElementById('audioVisualizer');
    }

    setupEventListeners() {
        // Record button - hold to speak
        this.recordBtn.addEventListener('mousedown', () => this.startRecording());
        this.recordBtn.addEventListener('mouseup', () => this.stopRecording());
        this.recordBtn.addEventListener('mouseleave', () => this.stopRecording());
        
        // Touch events for mobile
        this.recordBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.recordBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        
        // Reset button
        this.resetBtn.addEventListener('click', () => this.resetConversation());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !this.isRecording) {
                e.preventDefault();
                this.startRecording();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space' && this.isRecording) {
                e.preventDefault();
                this.stopRecording();
            }
        });
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            this.updateStatus('🌐 Connected to server');
        });

        this.socket.on('disconnect', () => {
            this.updateStatus('❌ Disconnected from server');
        });

        this.socket.on('connect_error', (error) => {
            this.updateStatus('❌ Connection error: ' + error.message);
        });

        this.socket.on('status', (data) => {
            this.updateStatus(data.message);
        });

        this.socket.on('transcript', (data) => {
            this.addMessage('user', data.text);
        });

        this.socket.on('ai_response', (data) => {
            this.addMessage('ai', data.text);
        });

        this.socket.on('audio_response', (data) => {
            this.playAudioResponse(data.audio);
        });

        this.socket.on('error', (data) => {
            this.updateStatus(`❌ ${data.message}`);
            this.showError(data.message);
        });
    }

    async requestMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 44100,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            this.audioStream = stream;
            this.updateStatus('🎤 Ready to listen...');
        } catch (error) {
            this.showError('Microphone permission denied. Please allow microphone access and refresh the page.');
            this.updateStatus('❌ Microphone access required');
        }
    }

    startRecording() {
        if (!this.audioStream || this.isRecording) return;

        this.isRecording = true;
        this.audioChunks = [];
        
        // Update UI
        this.recordBtn.classList.add('recording');
        this.recordBtn.innerHTML = '<i class="fas fa-stop"></i><span>Release to Send</span>';
        this.audioVisualizer.classList.add('active');
        this.updateStatus('🎤 Recording...');

        // Start recording
        this.mediaRecorder = new MediaRecorder(this.audioStream, {
            mimeType: 'audio/webm;codecs=opus'
        });

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = () => {
            this.processRecording();
        };

        this.mediaRecorder.start();
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        this.isRecording = false;
        
        // Update UI
        this.recordBtn.classList.remove('recording');
        this.recordBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Hold to Speak</span>';
        this.audioVisualizer.classList.remove('active');
        
        this.mediaRecorder.stop();
    }

    async processRecording() {
        if (this.audioChunks.length === 0) {
            this.updateStatus('🎤 Ready to listen...');
            return;
        }

        try {
            // Create blob from recorded chunks
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
            
            // Convert to WAV format
            const wavBlob = await this.convertToWav(audioBlob);
            
            // Convert to base64
            const reader = new FileReader();
            reader.onload = () => {
                const base64Audio = reader.result.split(',')[1];
                this.socket.emit('audio_data', { audio: base64Audio });
            };
            reader.readAsDataURL(wavBlob);
            
        } catch (error) {
            this.showError('Error processing audio: ' + error.message);
            this.updateStatus('🎤 Ready to listen...');
        }
    }

    async convertToWav(audioBlob) {
        // Create audio context
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Convert blob to array buffer
        const arrayBuffer = await audioBlob.arrayBuffer();
        
        // Decode audio data
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        // Convert to WAV
        const wavBuffer = this.audioBufferToWav(audioBuffer);
        
        return new Blob([wavBuffer], { type: 'audio/wav' });
    }

    audioBufferToWav(buffer) {
        const length = buffer.length;
        const numberOfChannels = buffer.numberOfChannels;
        const sampleRate = buffer.sampleRate;
        const arrayBuffer = new ArrayBuffer(44 + length * numberOfChannels * 2);
        const view = new DataView(arrayBuffer);
        
        // WAV header
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };
        
        writeString(0, 'RIFF');
        view.setUint32(4, 36 + length * numberOfChannels * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numberOfChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * numberOfChannels * 2, true);
        view.setUint16(32, numberOfChannels * 2, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, length * numberOfChannels * 2, true);
        
        // PCM data
        let offset = 44;
        for (let i = 0; i < length; i++) {
            for (let channel = 0; channel < numberOfChannels; channel++) {
                const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
                view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                offset += 2;
            }
        }
        
        return arrayBuffer;
    }

    playAudioResponse(base64Audio) {
        try {
            const audioData = atob(base64Audio);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const uint8Array = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                uint8Array[i] = audioData.charCodeAt(i);
            }
            
            const audioBlob = new Blob([arrayBuffer], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            audio.onloadeddata = () => {
                this.updateStatus('🔊 Playing response...');
            };
            
            audio.onended = () => {
                this.updateStatus('🎤 Ready to listen...');
                URL.revokeObjectURL(audioUrl);
            };
            
            audio.onerror = () => {
                this.updateStatus('❌ Audio playback failed');
                URL.revokeObjectURL(audioUrl);
            };
            
            audio.play();
            
        } catch (error) {
            this.showError('Error playing audio: ' + error.message);
            this.updateStatus('🎤 Ready to listen...');
        }
    }

    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = type === 'user' ? 'You' : 'AI Assistant';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(header);
        messageDiv.appendChild(contentDiv);
        
        // Remove welcome message if it exists
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateStatus(message) {
        this.statusText.textContent = message;
    }

    showError(message) {
        console.error('Error:', message);
        // You could add a toast notification here
    }

    resetConversation() {
        this.socket.emit('reset_conversation');
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <i class="fas fa-microphone"></i>
                <h3>Conversation Reset!</h3>
                <p>Click the microphone button and start speaking</p>
            </div>
        `;
        this.updateStatus('🎤 Ready to listen...');
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceChatApp();
}); 