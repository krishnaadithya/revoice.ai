from pytubefix import YouTube
from pytubefix.cli import on_progress
from groq import Groq
import os
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
from pydub import AudioSegment
import gradio as gr


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
      #print(i)  # i => index
      #print(gs) # gs => graphemes/text
      #print(ps) # ps => phonemes
      #display(Audio(data=audio, rate=24000, autoplay=i==0))
      
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

#stictc
video_url = "https://www.youtube.com/watch?v=ZcI2B92JlJU"
youtube_caption_text = get_youtub_caption(video_url)
vid_name = video_url.split("=")[-1]
text_to_audio(youtube_caption_text, save_path=vid_name+'.wav')



audio_path = "/content/test.mp3"
vid_name = os.path.basename(audio_path).split(".")[0]
text_to_audio(youtube_caption_text, voice = "af_river", save_path=vid_name+'.wav')

def greet(name):
    return f"Hello, {name}!"

# Create the Gradio interface
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Enter your name"),
    outputs=gr.Textbox(label="Output"),
    title="Simple Greeting App",
    description="Enter your name and get a personalized greeting!"
)

if __name__ == "__main__":
    demo.launch()
