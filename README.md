# Revoice.AI

Revoice.AI is a tool that converts audio/video content to different voices, making content more engaging by transforming boring or monotonous voices into voices you prefer.

## Features

- Convert audio from various sources (YouTube, direct uploads)
- Support for multiple file formats (.mp3, .wav, .mp4)
- Voice conversion using Kokoro TTS
- Speaker-aware transcription using Whisper
- Simple, user-friendly interface

## Project Structure

```
revoice_ai/
│── backend/
│   │── audio_processing/
│   │   ├── transcriber.py  # Uses Whisper to transcribe and diarize
│   │   ├── converter.py    # Uses Kokoro TTS for voice conversion
│   │   ├── downloader.py   # Handles video/audio downloads
│   │   ├── utils.py        # Helper functions
│   │── main.py             # FastAPI backend
│
│── frontend/
│   │── app.py              # Gradio UI
│   │── components.py       # UI components
│
│── models/                 # Pretrained models
│── config.py              # Configuration settings
│── requirements.txt       # Dependencies
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/revoice.ai.git
cd revoice.ai
```

2. Install system dependencies:

For macOS:
```bash
brew install espeak-ng
```

For Ubuntu/Debian:
```bash
sudo apt-get install espeak-ng
```

3. Create and set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python frontend/app.py
```

## Usage

1. Upload an audio/video file or provide a YouTube URL
2. Choose your desired voice
3. Wait for processing
4. Download the converted audio

## Technologies Used

- Whisper: For accurate speech-to-text transcription
- Kokoro TTS: For high-quality voice synthesis
- FastAPI: Backend API framework
- Gradio: User interface
- PyTubeFix: YouTube video processing
- espeak-ng: Required for English OOD fallback and some non-English languages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```