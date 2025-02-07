import os
import gradio as gr
import soundfile as sf
from utils.youtube import get_youtube_caption
from utils.audio import text_to_audio, transcribe_audio
from config import OUTPUT_DIR

def process_youtube(video_url):
    """Process YouTube video and return generated audio"""
    try:
        youtube_caption_text = get_youtube_caption(video_url)
        vid_name = video_url.split("=")[-1]
        output_path = os.path.join(OUTPUT_DIR, f"{vid_name}.wav")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        text_to_audio(youtube_caption_text, save_path=output_path)
        audio_data, sample_rate = sf.read(output_path)
        return (sample_rate, audio_data), "Success! Audio generated from YouTube captions."
    except Exception as e:
        return None, f"Error processing YouTube video: {str(e)}"

def process_audio_file(audio_file):
    """Process uploaded audio file and return generated audio"""
    try:
        if audio_file is None:
            return None, "Please upload an audio file"
            
        transcription = transcribe_audio(audio_file)
        output_path = os.path.join(OUTPUT_DIR, f"{os.path.basename(audio_file)}_output.wav")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        text_to_audio(transcription, voice="af_river", save_path=output_path)
        audio_data, sample_rate = sf.read(output_path)
        return (sample_rate, audio_data), "Success! Audio generated from uploaded file."
    except Exception as e:
        return None, f"Error processing audio file: {str(e)}"

def process_input(youtube_url, audio_file):
    """Main processing function that handles both input types"""
    if youtube_url:
        return process_youtube(youtube_url)
    elif audio_file:
        return process_audio_file(audio_file)
    else:
        return None, "Please provide either a YouTube URL or upload an audio file"

# Create the Gradio interface
def create_interface():
    with gr.Blocks(title="Audio Processing App") as demo:
        gr.Markdown("# Audio Processing App")
        gr.Markdown("Enter a YouTube URL or upload an audio file to process")
        
        with gr.Row():
            with gr.Column():
                youtube_input = gr.Textbox(
                    label="YouTube URL",
                    placeholder="Enter YouTube URL here..."
                )
                audio_input = gr.Audio(
                    label="Or upload audio file",
                    type="filepath"
                )
                process_btn = gr.Button("Process")
            
            with gr.Column():
                audio_output = gr.Audio(label="Generated Audio")
                status_output = gr.Textbox(label="Status")
        
        process_btn.click(
            fn=process_input,
            inputs=[youtube_input, audio_input],
            outputs=[audio_output, status_output]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch() 