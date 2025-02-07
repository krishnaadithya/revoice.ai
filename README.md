# revoice.ai

A simple web application that converts YouTube videos and audio files into synthesized speech using AI models.

## Features

- Process YouTube videos by extracting and converting captions to speech
- Convert uploaded audio files through transcription and voice synthesis
- User-friendly web interface built with Gradio
- Multiple voice options for synthesis
- Automatic caption extraction from YouTube videos

## Project Structure

```
project/
├── src/
│   ├── utils/
│   │   ├── audio.py      # Audio processing functions
│   │   └── youtube.py    # YouTube caption extraction
│   ├── app.py           # Gradio interface
│   └── config.py        # Configuration settings
├── requirements.txt     # Dependencies
├── .env.example        # Example environment variables
└── README.md           # Documentation
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install system dependencies (Linux):
```bash
apt-get install espeak-ng
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python src/app.py
```

2. Open your web browser and navigate to the provided URL (usually http://127.0.0.1:7860)

3. Use the app by either:
   - Entering a YouTube URL
   - Uploading an audio file

4. Click "Process" and wait for the generated audio

## Technologies Used

- [Gradio](https://gradio.app/): Web interface framework
- [Kokoro](https://github.com/kairess/kokoro): Text-to-speech synthesis
- [Groq](https://groq.com/): Audio transcription using Whisper model
- [PyTubeFix](https://github.com/JuanBindez/pytubefix): YouTube video processing
- [soundfile](https://github.com/bastibe/python-soundfile): Audio file handling
- [pydub](https://github.com/jiaaro/pydub): Audio processing

## Requirements

- Python 3.8+
- Groq API key
- espeak-ng (for Linux systems)
- Internet connection for YouTube processing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.