from typing import Optional
from pytubefix import YouTube
import os
from .utils import generate_filename
from config import settings

class VideoDownloader:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR

    async def download_from_youtube(self, url: str) -> Optional[str]:
        """
        Download audio from YouTube video.
        Returns path to downloaded audio file.
        """
        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                raise Exception("No audio stream found")
            
            # Generate output filename
            output_filename = generate_filename(".mp3")
            output_path = os.path.join(self.upload_dir, output_filename)
            
            # Download the audio
            audio_stream.download(output_path=self.upload_dir, filename=output_filename)
            
            return output_path
        
        except Exception as e:
            print(f"Error downloading YouTube video: {str(e)}")
            return None 