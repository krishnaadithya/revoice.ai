from pytubefix import YouTube
from pytubefix.cli import on_progress
from groq import Groq
import os
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
from pydub import AudioSegment
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def _timestamp_to_seconds(timestamp: str) -> float:
        """Convert SRT timestamp to seconds."""
        if ',' in timestamp:
            timestamp = timestamp.replace(',', '.')
        
        parts = timestamp.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return 0

def _parse_srt_captions(srt_captions: str):
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
              current_segment['start'] = _timestamp_to_seconds(start.strip())
              current_segment['end'] = _timestamp_to_seconds(end.strip())
          elif line:  # Text content
              if 'text' in current_segment:
                  current_segment['text'] += ' ' + line
              else:
                  current_segment['text'] = line
      
      if current_segment:
          segments.append(current_segment)
      
      return segments

def combine_text(segments):
  text = ""
  for info in segments:
    text+=info['text']+" "
  return text


def get_youtub_caption(video_url):
    yt = YouTube(url=video_url)

    if yt.captions and 'a.en' in yt.captions:
        caption = yt.captions['a.en']
        raw_captions = caption.generate_srt_captions()
        segments = _parse_srt_captions(raw_captions)

    # Fall back to manual English captions
    if yt.captions and 'en' in yt.captions:
        caption = yt.captions['en']
        raw_captions = caption.generate_srt_captions()
        segments = _parse_srt_captions(raw_captions)
    
    return combine_text(segments)

def text_to_audio(text, lang_code = 'a', voice = 'af_heart', save_path="output.wav"):
  pipeline = KPipeline(lang_code=lang_code) # <= make sure lang_code matches voice

  # Create an empty AudioSegment to store the combined audio
  combined_audio = AudioSegment.empty()

  # 4️⃣ Generate, display, and save audio files in a loop.
  generator = pipeline(
      text, voice=voice, # <= change voice here
      speed=1, split_pattern=r'\n+'
  )
  for i, (gs, ps, audio) in enumerate(generator):      
      # Save individual segment
      segment_path = f'{i}.wav'
      sf.write(segment_path, audio, 24000)
      
      # Load the segment and append to combined audio
      segment = AudioSegment.from_wav(segment_path)
      combined_audio += segment

  # Export the combined audio
  combined_audio.export(save_path, format="wav")

def transcribe_audio(audio_path):
  with open(audio_path, "rb") as file:
      transcription = client.audio.transcriptions.create(
        file=(audio_path, file.read()),
        model="whisper-large-v3",
        response_format="verbose_json",
      )
     
  return transcription.text

def process_youtube(video_url):
    """Process YouTube video and return generated audio"""
    try:
        youtube_caption_text = get_youtub_caption(video_url)
        vid_name = video_url.split("=")[-1]
        output_path = f"outputs/{vid_name}.wav"
        os.makedirs("outputs", exist_ok=True)
        
        text_to_audio(youtube_caption_text, save_path=output_path)
        # Read the audio file and return in Gradio-compatible format
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
        output_path = f"outputs/{os.path.basename(audio_file)}_output.wav"
        os.makedirs("outputs", exist_ok=True)
        
        text_to_audio(transcription, voice="af_river", save_path=output_path)
        # Read the audio file and return in Gradio-compatible format
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

if __name__ == "__main__":
    demo.launch()
