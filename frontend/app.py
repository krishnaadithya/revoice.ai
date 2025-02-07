import gradio as gr
import requests
import os
import tempfile
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config import settings
from backend.audio_processing import Transcriber, VoiceConverter, VideoDownloader

API_URL = f"http://localhost:{settings.API_PORT}/convert"

# Initialize backend services
transcriber = Transcriber()
converter = VoiceConverter()
downloader = VideoDownloader()

# Available Kokoro voices and accents
KOKORO_VOICES = {
    "af_heart": "American Female",
    "am_heart": "American Male",
    "bf_heart": "British Female",
    "bm_heart": "British Male"
}

ACCENTS = {
    'a': '🇺🇸 American English',
    'b': '🇬🇧 British English',
    'j': '🇯🇵 Japanese',
    'z': '🇨🇳 Mandarin Chinese'
}

def process_audio(input_audio, youtube_url, target_voice, accent):
    try:
        if input_audio is None and not youtube_url:
            return None, "Please provide either an audio file or YouTube URL"
        
        files = {}
        data = {
            "target_voice": target_voice,
            "accent": accent
        }
        
        if youtube_url:
            data["youtube_url"] = youtube_url
        elif input_audio:
            files = {"file": open(input_audio, "rb")}
        
        # Make request to API
        response = requests.post(API_URL, files=files, data=data)
        
        if response.status_code != 200:
            return None, f"Error: {response.json()['detail']}"
        
        # Save the response audio to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(response.content)
        temp_file.close()
        
        return temp_file.name, "Conversion successful!"
    
    except Exception as e:
        return None, f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Revoice.AI") as interface:
    gr.Markdown("# Revoice.AI")
    gr.Markdown("Convert any voice to your preferred voice!")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(label="Upload Audio")
            youtube_url = gr.Textbox(label="Or Enter YouTube URL")
            
            with gr.Row():
                accent = gr.Dropdown(
                    choices=list(ACCENTS.keys()),
                    value='a',
                    label="Select Accent",
                    info="Choose the accent for the output voice"
                )
                target_voice = gr.Dropdown(
                    choices=list(KOKORO_VOICES.keys()),
                    value="af_heart",
                    label="Select Voice",
                    info="Choose the voice type"
                )
            
            convert_btn = gr.Button("Convert")
        
        with gr.Column():
            output_audio = gr.Audio(label="Converted Audio")
            status = gr.Textbox(label="Status")
    
    # Update voice choices based on accent
    def update_voices(accent):
        if accent == 'j':
            return gr.Dropdown(choices=["j_heart"])
        elif accent == 'z':
            return gr.Dropdown(choices=["z_heart"])
        else:
            return gr.Dropdown(choices=list(KOKORO_VOICES.keys()))
    
    accent.change(
        update_voices,
        inputs=[accent],
        outputs=[target_voice]
    )
    
    convert_btn.click(
        process_audio,
        inputs=[audio_input, youtube_url, target_voice, accent],
        outputs=[output_audio, status]
    )

if __name__ == "__main__":
    # Start FastAPI server in a separate process
    import subprocess
    import sys
    from pathlib import Path
    
    backend_path = Path(__file__).parent.parent / "backend" / "main.py"
    subprocess.Popen([sys.executable, str(backend_path)])
    
    # Start Gradio interface
    interface.launch()