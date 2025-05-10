import os
import logging
import time
import random
import string
from django.conf import settings as django_settings

# Configure logging (can use Django's setup or a specific one for AI components)
logger = logging.getLogger('standards_analysis.ai_system') # Specific logger

class AIConfig:
    OPENAI_API_KEY = django_settings.OPENAI_API_KEY

    # Vector Database Configuration
    # These paths are now taken from Django settings
    DB_BASE_PARENT_DIR = django_settings.AI_DB_BASE_PARENT_DIR
    DB_DIRECTORY = django_settings.AI_DEFAULT_DB_DIR # Initial default
    COLLECTION_NAME = "aaoifi_standards_django" # Use a different name to avoid conflicts

    # PDF Processing Configuration (for bulk processing via admin command)
    PDF_INPUT_FOLDER = django_settings.AI_PDF_INPUT_FOLDER # For admin command
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Models Configuration
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT4_MODEL = "gpt-4" # or "gpt-4-turbo-preview" or "gpt-4o"
    GPT35_MODEL = "gpt-3.5-turbo"

    # Output Configuration
    OUTPUT_DIR = django_settings.AI_OUTPUT_DIR # For saving JSON results from AI
    VISUALIZATION_TEMP_DIR = django_settings.AI_VISUALIZATION_TEMP_DIR

aicfg = AIConfig()

def update_ai_config_db_directory(new_db_dir_path: str):
    """Updates the AIConfig's DB_DIRECTORY if a new one is created."""
    global aicfg
    aicfg.DB_DIRECTORY = new_db_dir_path
    logger.info(f"AIConfig.DB_DIRECTORY updated to: {aicfg.DB_DIRECTORY}")

def generate_new_db_directory_path() -> str:
    """Generates a new unique directory path for the vector database."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    new_db_dir = os.path.join(aicfg.DB_BASE_PARENT_DIR, f"db_{timestamp}_{random_str}")
    os.makedirs(new_db_dir, exist_ok=True)
    logger.info(f"Generated new DB directory path: {new_db_dir}")
    return new_db_dir

# Ensure AI directories exist (already done in settings.py, but good for service module)
os.makedirs(aicfg.PDF_INPUT_FOLDER, exist_ok=True)
os.makedirs(aicfg.OUTPUT_DIR, exist_ok=True)
os.makedirs(aicfg.DB_BASE_PARENT_DIR, exist_ok=True)
os.makedirs(aicfg.DB_DIRECTORY, exist_ok=True)
os.makedirs(aicfg.VISUALIZATION_TEMP_DIR, exist_ok=True)