from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
from typing import Optional
from pydantic import BaseModel

from audio_processing.downloader import VideoDownloader
from audio_processing.transcriber import Transcriber
from audio_processing.converter import VoiceConverter
from audio_processing.utils import (
    create_directories,
    generate_filename,
    is_valid_format
)
from config import settings

app = FastAPI(title="Revoice.AI API")
downloader = VideoDownloader()
transcriber = Transcriber()
converter = VoiceConverter()

# Create necessary directories
create_directories()

class ConversionRequest(BaseModel):
    youtube_url: Optional[str] = None
    target_voice: str
    accent: str = 'a'  # Default to American English

@app.post("/convert")
async def convert_audio(
    request: ConversionRequest = None,
    file: UploadFile = File(None),
    background_tasks: BackgroundTasks
):
    try:
        # Handle YouTube URL
        if request and request.youtube_url:
            # Get transcription directly from YouTube captions
            result = transcriber.transcribe(request.youtube_url, is_youtube_url=True)
            if not result["segments"]:
                raise HTTPException(status_code=400, detail="Failed to get YouTube captions")
            
            # Download audio only if we need to process it
            audio_path = await downloader.download_from_youtube(request.youtube_url)
            if not audio_path:
                raise HTTPException(status_code=400, detail="Failed to download YouTube video")
        
        # Handle file upload
        elif file:
            if not is_valid_format(file.filename):
                raise HTTPException(status_code=400, detail="Unsupported file format")
            
            audio_path = os.path.join(settings.UPLOAD_DIR, generate_filename(os.path.splitext(file.filename)[1]))
            with open(audio_path, "wb") as buffer:
                buffer.write(await file.read())
            
            # Transcribe uploaded file using Groq
            result = transcriber.transcribe(audio_path, is_youtube_url=False)
            if not result["segments"]:
                raise HTTPException(status_code=500, detail="Transcription failed")
        else:
            raise HTTPException(status_code=400, detail="No input provided")
        
        # Convert voice
        output_path = os.path.join(settings.OUTPUT_DIR, generate_filename(".wav"))
        converted_path = await converter.convert_segments(
            result["segments"],
            request.target_voice,
            output_path,
            request.accent
        )
        
        if not converted_path:
            raise HTTPException(status_code=500, detail="Voice conversion failed")
        
        # Clean up input file in background
        background_tasks.add_task(os.remove, audio_path)
        
        return FileResponse(
            converted_path,
            media_type="audio/wav",
            filename="converted_audio.wav"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 