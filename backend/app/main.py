"""
Script2Sound FastAPI Application
Main API server that handles HTTP requests and integrates with TTS service
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import io
import logging
from dotenv import load_dotenv
import os

# Import our TTS service
from app.tts_service import TTSService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Script2Sound API",
    description="Convert text scripts to natural-sounding audio using Google Cloud TTS",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion"""
    text: str = Field(..., min_length=1, max_length=50000, description="Text to convert to speech")
    voice_name: str = Field(default="en-US-Neural2-D", description="Google TTS voice name")
    language_code: str = Field(default="en-US", description="Language code")
    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0, description="Speaking rate")
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0, description="Voice pitch")

class VoiceInfo(BaseModel):
    """Model for voice information"""
    name: str
    language_code: str
    gender: str
    natural_sample_rate: int

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    detail: Optional[str] = None

# Initialize TTS service
tts_service = TTSService()

# Dependency to get TTS service
def get_tts_service() -> TTSService:
    """Dependency injection for TTS service"""
    return tts_service

@app.get("/", response_model=dict)
async def root():
    """Health check endpoint"""
    return {
        "message": "Script2Sound API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health", response_model=dict)
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Test TTS service connectivity
        test_voices = await tts_service.get_available_voices()
        return {
            "status": "healthy",
            "tts_service": "connected",
            "available_voices": len(test_voices)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="TTS service unavailable")

@app.post("/generate-audio")
async def generate_audio(
    request: TextToSpeechRequest,
    tts: TTSService = Depends(get_tts_service)
):
    """
    Generate audio from text using Google Cloud TTS
    
    Args:
        request: Text-to-speech request parameters
        tts: TTS service dependency
        
    Returns:
        Audio file as streaming response
    """
    try:
        logger.info(f"Audio generation requested for {len(request.text)} characters")
        
        # Validate voice if needed
        if not tts.validate_voice(request.voice_name, request.language_code):
            logger.warning(f"Voice validation failed for {request.voice_name}")
        
        # Generate audio
        audio_data = await tts.text_to_speech(
            text=request.text,
            voice_name=request.voice_name,
            language_code=request.language_code,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch
        )
        
        logger.info("Audio generation completed successfully")
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=generated_audio.mp3",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Audio generation failed: {str(e)}"
        )

@app.get("/voices", response_model=List[VoiceInfo])
async def get_voices(
    language_code: str = "en-US",
    tts: TTSService = Depends(get_tts_service)
):
    """
    Get available TTS voices
    
    Args:
        language_code: Language code to filter voices
        tts: TTS service dependency
        
    Returns:
        List of available voices
    """
    try:
        logger.info(f"Voices requested for language: {language_code}")
        voices = await tts.get_available_voices(language_code)
        return voices
    except Exception as e:
        logger.error(f"Failed to fetch voices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch voices: {str(e)}"
        )

@app.post("/validate-text")
async def validate_text(request: dict):
    """
    Validate text before processing
    
    Args:
        request: Dictionary containing text to validate
        
    Returns:
        Validation result
    """
    try:
        text = request.get("text", "")
        
        if not text.strip():
            return {"valid": False, "error": "Text cannot be empty"}
        
        if len(text) > 50000:
            return {"valid": False, "error": "Text too long (max 50,000 characters)"}
        
        # Estimate processing time (rough calculation)
        estimated_time = len(text) / 1000 * 2  # ~2 seconds per 1000 chars
        
        return {
            "valid": True,
            "character_count": len(text),
            "estimated_time_seconds": round(estimated_time, 1),
            "chunks_needed": (len(text) // 5000) + 1
        }
        
    except Exception as e:
        logger.error(f"Text validation failed: {e}")
        raise HTTPException(status_code=500, detail="Validation failed")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": "The requested endpoint does not exist"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Something went wrong on our end"}
    )

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )