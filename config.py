from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # File Settings
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE: int = 1024 * 1024 * 100  # 100MB
    
    # Model Settings
    WHISPER_MODEL: str = "base"  # Options: tiny, base, small, medium, large
    
    # Supported Formats
    SUPPORTED_AUDIO_FORMATS: list = [".mp3", ".wav", ".m4a", ".ogg"]
    SUPPORTED_VIDEO_FORMATS: list = [".mp4", ".mkv", ".webm"]
    
    class Config:
        env_file = ".env"

settings = Settings() 