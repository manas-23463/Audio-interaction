"""
Audio Handler Module
Handles microphone input and audio playback for real-time conversation
"""

import pyaudio
import numpy as np
import wave
import threading
import time
import io
from typing import Optional, Callable
from config import Config

class AudioHandler:
    """Handles real-time audio input and output"""
    
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.audio_buffer = []
        self.silence_threshold = 0.01
        self.silence_duration = 1.0  # seconds
        self.last_audio_time = time.time()
        
    def start_recording(self, on_audio_data: Callable[[bytes], None]):
        """Start recording from microphone"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.audio_buffer = []
        self.last_audio_time = time.time()
        
        def callback(in_data, frame_count, time_info, status):
            if self.is_recording:
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                audio_level = np.abs(audio_data).mean() / 32768.0
                
                if audio_level > self.silence_threshold:
                    self.last_audio_time = time.time()
                    self.audio_buffer.extend(audio_data)
                elif self.audio_buffer and (time.time() - self.last_audio_time) > self.silence_duration:
                    if self.audio_buffer:
                        # Convert to WAV format for ElevenLabs STT
                        wav_data = self._convert_to_wav(np.array(self.audio_buffer, dtype=np.int16))
                        on_audio_data(wav_data)
                        self.audio_buffer = []
                
            return (in_data, pyaudio.paContinue)
        
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=Config.CHANNELS,
            rate=Config.SAMPLE_RATE,
            input=True,
            output=False,
            frames_per_buffer=Config.CHUNK_SIZE,
            stream_callback=callback
        )
        
        self.stream.start_stream()
        print("🎤 Microphone recording started...")
    
    def _convert_to_wav(self, audio_data: np.ndarray) -> bytes:
        """Convert audio data to WAV format"""
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(Config.CHANNELS)
            wav_file.setsampwidth(2)  # 2 bytes for int16
            wav_file.setframerate(Config.SAMPLE_RATE)
            wav_file.writeframes(audio_data.tobytes())
        return buffer.getvalue()
    
    def stop_recording(self):
        """Stop recording from microphone"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        print("🎤 Microphone recording stopped")
    
    def play_audio(self, audio_data: bytes):
        """Play audio data through speakers"""
        try:
            output_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=Config.CHANNELS,
                rate=Config.SAMPLE_RATE,
                output=True
            )
            
            chunk_size = Config.CHUNK_SIZE * 2
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if chunk:
                    output_stream.write(chunk)
            
            output_stream.stop_stream()
            output_stream.close()
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
    
    def save_audio_to_file(self, audio_data: bytes, filename: str):
        """Save audio data to a WAV file"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(Config.CHANNELS)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(Config.SAMPLE_RATE)
                wf.writeframes(audio_data)
            print(f"💾 Audio saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_recording()
        if self.p:
            self.p.terminate() 