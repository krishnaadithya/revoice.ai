from kokoro import KPipeline
import numpy as np
from typing import List, Dict
import os
from .utils import save_audio
from config import settings

class VoiceConverter:
    def __init__(self):
        self.pipelines = {}
        self.supported_langs = {
            'a': 'American English',
            'b': 'British English',
            'j': 'Japanese',
            'z': 'Mandarin Chinese'
        }
    
    def get_pipeline(self, lang_code: str) -> KPipeline:
        """Get or create pipeline for specified language."""
        if lang_code not in self.pipelines:
            self.pipelines[lang_code] = KPipeline(lang_code=lang_code)
        return self.pipelines[lang_code]
    
    async def convert_segments(
        self,
        segments: List[Dict],
        target_voice: str,
        output_path: str,
        accent: str = 'a'
    ) -> str:
        """
        Convert transcribed segments to target voice using Kokoro.
        accent: 'a' for American, 'b' for British, 'j' for Japanese, 'z' for Mandarin
        """
        try:
            if accent not in self.supported_langs:
                raise ValueError(f"Unsupported accent: {accent}")
            
            pipeline = self.get_pipeline(accent)
            all_audio = []
            
            # Process each segment
            for segment in segments:
                text = segment["text"]
                
                # Generate audio for the segment
                generator = pipeline(
                    text,
                    voice=target_voice,
                    speed=1,
                    split_pattern=r'\n+'
                )
                
                # Collect all audio chunks
                for _, _, audio in generator:
                    all_audio.append(audio)
            
            # Combine all audio segments
            if all_audio:
                combined_audio = np.concatenate(all_audio)
                
                # Save the combined audio
                save_audio(combined_audio, 24000, output_path)  # Kokoro uses 24kHz sample rate
                
                return output_path
            
            return None
        
        except Exception as e:
            print(f"Error in voice conversion: {str(e)}")
            return None 