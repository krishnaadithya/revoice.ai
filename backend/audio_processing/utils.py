import os
import uuid
from pathlib import Path
import soundfile as sf
import librosa
import numpy as np
from config import settings

def create_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

def generate_filename(extension: str) -> str:
    """Generate a unique filename with the given extension."""
    return f"{uuid.uuid4()}{extension}"

def load_audio(file_path: str) -> tuple:
    """Load audio file and return audio data with sample rate."""
    audio, sr = librosa.load(file_path, sr=None)
    return audio, sr

def save_audio(audio: np.ndarray, sample_rate: int, file_path: str):
    """Save audio data to file."""
    sf.write(file_path, audio, sample_rate)

def get_duration(file_path: str) -> float:
    """Get duration of audio file in seconds."""
    return librosa.get_duration(filename=file_path)

def is_valid_format(filename: str) -> bool:
    """Check if file format is supported."""
    ext = Path(filename).suffix.lower()
    return ext in settings.SUPPORTED_AUDIO_FORMATS + settings.SUPPORTED_VIDEO_FORMATS 