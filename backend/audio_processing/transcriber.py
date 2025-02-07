from typing import Dict, List, Tuple
import os
from groq import Groq
from config import settings
import time
from pytubefix import YouTube
import logging

logger = logging.getLogger(__name__)

class Transcriber:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=api_key)
        self.max_retries = 3
    
    def get_youtube_transcript(self, video_url: str) -> Dict[str, List[Dict]]:
        """Get transcript from YouTube captions."""
        try:
            # Initialize YouTube object with retry logic
            for attempt in range(self.max_retries):
                try:
                    yt = YouTube(url=video_url)  # pytubefix syntax
                    
                    time.sleep(1)  # Prevent rate limiting
                    
                    # Try auto-generated English captions first
                    if yt.captions and 'a.en' in yt.captions:
                        caption = yt.captions['a.en']
                        raw_captions = caption.generate_srt_captions()
                        segments = self._parse_srt_captions(raw_captions)
                        return {"segments": segments, "language": "en"}
                    
                    # Fall back to manual English captions
                    if yt.captions and 'en' in yt.captions:
                        caption = yt.captions['en']
                        raw_captions = caption.generate_srt_captions()
                        segments = self._parse_srt_captions(raw_captions)
                        return {"segments": segments, "language": "en"}
                    
                    logger.error("No captions available for this video")
                    return {"segments": [], "language": None}
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed after {self.max_retries} attempts: {str(e)}")
                        return {"segments": [], "language": None}
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error getting YouTube transcript: {str(e)}")
            return {"segments": [], "language": None}
    
    def _parse_srt_captions(self, srt_captions: str) -> List[Dict]:
        """Parse SRT format captions into segments."""
        segments = []
        current_segment = {}
        
        for line in srt_captions.split('\n'):
            line = line.strip()
            
            if line.isdigit():  # Segment number
                if current_segment:
                    segments.append(current_segment)
                current_segment = {}
            elif '-->' in line:  # Timestamp
                start, end = line.split('-->')
                current_segment['start'] = self._timestamp_to_seconds(start.strip())
                current_segment['end'] = self._timestamp_to_seconds(end.strip())
            elif line:  # Text content
                if 'text' in current_segment:
                    current_segment['text'] += ' ' + line
                else:
                    current_segment['text'] = line
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert SRT timestamp to seconds."""
        if ',' in timestamp:
            timestamp = timestamp.replace(',', '.')
        
        parts = timestamp.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return 0
    
    def transcribe(self, audio_path: str, is_youtube_url: bool = False) -> Dict[str, List[Dict]]:
        """
        Transcribe content - either from YouTube captions or using Groq API.
        """
        try:
            # Handle YouTube URLs
            if is_youtube_url:
                return self.get_youtube_transcript(audio_path)  # audio_path is actually the URL here
            
            # Handle direct audio/video uploads using Groq
            with open(audio_path, "rb") as file:
                result = self.client.audio.transcriptions.create(
                    file=(audio_path, file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json"
                )
            
            # Format segments from the response
            segments = []
            for segment in result.segments:
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                })
            
            return {
                "segments": segments,
                "language": result.language
            }
        
        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            return {"segments": [], "language": None} 