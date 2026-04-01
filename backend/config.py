import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_PATH = BASE_DIR / "backend" / "chromadb"

# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gemini-2.5-flash"

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# FastAPI Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
