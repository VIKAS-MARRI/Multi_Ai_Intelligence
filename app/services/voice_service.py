"""
Voice Service Module
Handles speech-to-text and text-to-speech functionality
Enterprise-grade implementation with multiple voice engine support
"""

import logging
import os
from typing import Dict, Any, Optional
from config import Config
import speech_recognition as sr

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Service for handling voice input/output
    Supports multiple TTS engines: pyttsx3, edge-tts, etc.
    """
    
    def __init__(self):
        """Initialize voice service"""
        self.voice_engine = Config.VOICE_ENGINE
        self.voice_rate = Config.VOICE_RATE
        self.voice_volume = Config.VOICE_VOLUME
        
        # Initialize recognizer for STT
        self.recognizer = sr.Recognizer()
        
        # Initialize TTS engine
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize text-to-speech engine"""
        try:
            if self.voice_engine == 'pyttsx3':
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.voice_rate)
                self.tts_engine.setProperty('volume', self.voice_volume)
            elif self.voice_engine == 'edge-tts':
                # edge-tts is used for async operations
                import edge_tts
                self.edge_tts = edge_tts
            else:
                logger.warning(f"Unknown voice engine: {self.voice_engine}")
        except ImportError as e:
            logger.warning(f"Voice engine {self.voice_engine} not available: {e}")
    
    async def speech_to_text(self, audio_data: bytes = None) -> Dict[str, Any]:
        """
        Convert speech to text from microphone or audio data
        
        Args:
            audio_data (bytes): Optional audio data (if None, captures from microphone)
        
        Returns:
            Dict with transcribed text or error message
        """
        try:
            if audio_data:
                # Use provided audio data
                audio = sr.AudioData(audio_data, 16000, 2)
            else:
                # Capture from microphone
                with sr.Microphone() as source:
                    logger.info("Listening for audio...")
                    audio = self.recognizer.listen(source, timeout=10)
            
            # Try Google Speech Recognition (free option)
            try:
                text = self.recognizer.recognize_google(audio)
                return {
                    'status': 'success',
                    'text': text,
                    'engine': 'google_speech_recognition'
                }
            except sr.UnknownValueError:
                return {
                    'status': 'error',
                    'message': 'Could not understand audio',
                    'engine': 'google_speech_recognition'
                }
            except sr.RequestError as e:
                return {
                    'status': 'error',
                    'message': f'Speech Recognition service error: {str(e)}',
                    'engine': 'google_speech_recognition'
                }
        
        except sr.RequestError as e:
            logger.error(f"Speech Recognition error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Audio capture error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in speech_to_text: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }
    
    async def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech and save/play audio
        
        Args:
            text (str): Text to convert to speech
        
        Returns:
            Dict with audio file path or status
        """
        try:
            if not text or len(text) == 0:
                return {
                    'status': 'error',
                    'message': 'No text provided for speech synthesis'
                }
            
            # Limit text length for voice synthesis
            max_voice_length = 500
            text_to_speak = text[:max_voice_length] if len(text) > max_voice_length else text
            
            if self.voice_engine == 'pyttsx3':
                return await self._tts_pyttsx3(text_to_speak)
            elif self.voice_engine == 'edge-tts':
                return await self._tts_edge(text_to_speak)
            else:
                return {
                    'status': 'error',
                    'message': f'TTS engine not configured: {self.voice_engine}'
                }
        
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'Text-to-speech error: {str(e)}'
            }
    
    async def _tts_pyttsx3(self, text: str) -> Dict[str, Any]:
        """
        Use pyttsx3 for text-to-speech
        
        Args:
            text (str): Text to convert to speech
        
        Returns:
            Dict with status
        """
        try:
            # Save to file
            output_path = 'static/audio/response.mp3'
            os.makedirs('static/audio', exist_ok=True)
            
            self.tts_engine.save_to_file(text, output_path)
            self.tts_engine.runAndWait()
            
            return {
                'status': 'success',
                'audio_url': '/static/audio/response.mp3',
                'engine': 'pyttsx3'
            }
        
        except Exception as e:
            logger.error(f"pyttsx3 error: {str(e)}")
            return {
                'status': 'error',
                'message': f'pyttsx3 error: {str(e)}'
            }
    
    async def _tts_edge(self, text: str) -> Dict[str, Any]:
        """
        Use edge-tts for text-to-speech (async)
        
        Args:
            text (str): Text to convert to speech
        
        Returns:
            Dict with status
        """
        try:
            import edge_tts
            import asyncio
            
            output_path = 'static/audio/response.mp3'
            os.makedirs('static/audio', exist_ok=True)
            
            # Use edge-tts to generate speech
            communicate = edge_tts.Communicate(text=text, voice="en-US-AriaNeural")
            await communicate.save(output_path)
            
            return {
                'status': 'success',
                'audio_url': '/static/audio/response.mp3',
                'engine': 'edge-tts'
            }
        
        except ImportError:
            logger.error("edge-tts not installed")
            return {
                'status': 'error',
                'message': 'edge-tts not installed'
            }
        except Exception as e:
            logger.error(f"edge-tts error: {str(e)}")
            return {
                'status': 'error',
                'message': f'edge-tts error: {str(e)}'
            }


# Singleton instance
voice_service = VoiceService()
