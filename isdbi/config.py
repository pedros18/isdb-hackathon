# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vector Database Configuration
DB_DIRECTORY = "aaoifi_vector_db"
COLLECTION_NAME = "aaoifi_standards"

# PDF Processing Configuration
PDF_FOLDER = "pdf_eng"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Models Configuration
EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI embedding model
GPT4_MODEL = "gpt-4"
GPT35_MODEL = "gpt-3.5-turbo"

# Output Configuration
OUTPUT_DIR = "results"