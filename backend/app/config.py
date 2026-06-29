import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

OLLAMA_EMBEDDING_URL = "http://localhost:11434/api/embeddings"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2"

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

UPLOAD_DIR = Path("uploads")
