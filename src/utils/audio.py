import os
import soundfile as sf
from pydub import AudioSegment
from kokoro import KPipeline
from groq import Groq
from ..config import GROQ_API_KEY, SAMPLE_RATE, OUTPUT_DIR

client = Groq(api_key=GROQ_API_KEY)

def text_to_audio(text, lang_code='a', voice='af_heart', save_path="output.wav"):
    """Convert text to audio using Kokoro."""
    pipeline = KPipeline(lang_code=lang_code)
    combined_audio = AudioSegment.empty()

    generator = pipeline(
        text, 
        voice=voice,
        speed=1, 
        split_pattern=r'\n+'
    )

    for i, (_, _, audio) in enumerate(generator):
        segment_path = f'{i}.wav'
        sf.write(segment_path, audio, SAMPLE_RATE)
        
        segment = AudioSegment.from_wav(segment_path)
        combined_audio += segment
        os.remove(segment_path)  # Clean up temporary file

    combined_audio.export(save_path, format="wav")

def transcribe_audio(audio_path):
    """Transcribe audio using Groq."""
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    return transcription.text 