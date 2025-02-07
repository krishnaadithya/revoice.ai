import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Audio Configuration
SAMPLE_RATE = 24000
DEFAULT_VOICE = "af_heart"
DEFAULT_LANG_CODE = "a"

# Paths
OUTPUT_DIR = "outputs" 