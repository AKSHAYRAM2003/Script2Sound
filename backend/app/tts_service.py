"""
Text-to-Speech Service
Handles Google Cloud TTS API integration and audio processing
"""

from google.cloud import texttospeech
import asyncio
import logging
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    """
    Text-to-Speech service using Google Cloud TTS API
    Handles text chunking, voice synthesis, and audio generation
    """
    
    def __init__(self):
        """Initialize the TTS client and configuration"""
        try:
            self.client = texttospeech.TextToSpeechClient()
            self.max_chars = 10000  # Increased from 5000 to 10000
            logger.info("TTS Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS Service: {e}")
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split large text into manageable chunks for TTS processing
        
        Args:
            text: Input text to be chunked
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.max_chars:
            return [text]
        
        chunks = []
        # Split by sentences to maintain natural speech flow
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence exceeds limit
            test_chunk = current_chunk + sentence + '. '
            if len(test_chunk) <= self.max_chars:
                current_chunk = test_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks

    async def text_to_speech(
        self, 
        text: str, 
        voice_name: str = "en-US-Neural2-D",
        language_code: str = "en-US",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        is_ssml: bool = False
    ) -> bytes:
        """
        Convert text to speech using Google Cloud TTS
        
        Args:
            text: Text to convert to speech (plain text or SSML)
            voice_name: Google TTS voice name
            language_code: Language code (e.g., 'en-US')
            speaking_rate: Speech speed (0.25 to 4.0)
            pitch: Voice pitch (-20.0 to 20.0)
            is_ssml: Whether the input text is SSML formatted
            
        Returns:
            Audio data as bytes
        """
        try:
            if not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Clean the text
            text = self._clean_text(text)
            
            logger.info(f"Converting text to speech: {len(text)} characters, SSML: {is_ssml}")
            
            # Split text into chunks if needed
            chunks = self._chunk_text(text)
            audio_segments = []
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Configure synthesis input - use SSML if specified
                if is_ssml and chunk.strip().startswith('<?xml'):
                    synthesis_input = texttospeech.SynthesisInput(ssml=chunk)
                else:
                    synthesis_input = texttospeech.SynthesisInput(text=chunk)
                
                # Configure voice parameters
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=voice_name
                )
                
                # Configure audio output with enhanced settings
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speaking_rate,
                    pitch=pitch,
                    effects_profile_id=["headphone-class-device"],  # Optimize for headphones
                    sample_rate_hertz=24000  # Higher quality sample rate
                )
                
                # Make async call to Google TTS API
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice,
                        audio_config=audio_config
                    )
                )
                
                audio_segments.append(response.audio_content)
                logger.info(f"Chunk {i+1} processed successfully")
            
            # Combine all audio segments
            combined_audio = b''.join(audio_segments)
            logger.info(f"Audio generation completed: {len(combined_audio)} bytes")
            
            return combined_audio
            
        except Exception as e:
            logger.error(f"TTS conversion failed: {str(e)}")
            raise

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better TTS processing
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize line breaks
        text = ' '.join(text.split())  # Replace multiple spaces/newlines with single space
        
        # Handle common text formatting issues
        text = text.replace('\n', ' ')  # Replace newlines with spaces
        text = text.replace('\r', ' ')  # Replace carriage returns
        text = text.replace('\t', ' ')  # Replace tabs with spaces
        
        # Remove any XML/HTML tags that might be accidentally included
        import re
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML/XML tags
        
        return text.strip()

    async def get_available_voices(self, language_code: str = "en-US") -> List[Dict]:
        """
        Get list of available voices from Google TTS
        
        Args:
            language_code: Language code to filter voices
            
        Returns:
            List of available voices with metadata
        """
        try:
            logger.info(f"Fetching available voices for {language_code}")
            
            # Make async call to get voices
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.list_voices(language_code=language_code)
            )
            
            voices = []
            for voice in response.voices:
                # Focus on high-quality Neural2 voices
                if "Neural2" in voice.name:
                    voices.append({
                        "name": voice.name,
                        "language_code": voice.language_codes[0] if voice.language_codes else language_code,
                        "gender": voice.ssml_gender.name,
                        "natural_sample_rate": getattr(voice, 'natural_sample_rate_hertz', 24000)
                    })
            
            logger.info(f"Found {len(voices)} high-quality voices")
            return voices[:15]  # Return top 15 voices
            
        except Exception as e:
            logger.error(f"Failed to fetch voices: {str(e)}")
            raise

    def validate_voice(self, voice_name: str, language_code: str = "en-US") -> bool:
        """
        Validate if a voice name is available
        
        Args:
            voice_name: Voice name to validate
            language_code: Language code to check against
            
        Returns:
            True if voice is valid, False otherwise
        """
        try:
            # This is a simple validation - in production you might cache the voice list
            common_voices = [
                "en-US-Neural2-A", "en-US-Neural2-C", "en-US-Neural2-D",
                "en-US-Neural2-E", "en-US-Neural2-F", "en-US-Neural2-G",
                "en-US-Neural2-H", "en-US-Neural2-I", "en-US-Neural2-J"
            ]
            return voice_name in common_voices
        except Exception:
            return False
