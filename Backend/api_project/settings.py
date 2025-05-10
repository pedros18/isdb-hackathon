import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # Should point to KARIMDATA/Backend/
PROJECT_ROOT = BASE_DIR.parent # Points to KARIMDATA/

# Load .env file from KARIMDATA/Backend/ or KARIMDATA/
dotenv_path = BASE_DIR / '.env'
if not dotenv_path.exists():
    dotenv_path = PROJECT_ROOT / '.env'
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev') # Use a strong key for production
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*'] # Adjust for production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders', # For CORS
    'standards_analysis', # Your app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    # ... (default validators)
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles' # For production collectstatic

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Stores uploaded PDFs in Backend/media/

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer', # Optional for dev
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    # Add authentication and permission classes as needed
    # 'DEFAULT_AUTHENTICATION_CLASSES': [],
    # 'DEFAULT_PERMISSION_CLASSES': [],
}

# CORS Settings (adjust as needed)
CORS_ALLOW_ALL_ORIGINS = True # For development
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000", # Example for React frontend
# ]

# Custom AI System Settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# These paths should be absolute or relative to a known base (like BASE_DIR or PROJECT_ROOT)
# Using PROJECT_ROOT to place these outside the app/project dir, directly in KARIMDATA/
AI_PDF_INPUT_FOLDER = PROJECT_ROOT / "pdf_eng_django"  # For PDFs processed by admin command
AI_OUTPUT_DIR = PROJECT_ROOT / "results_django"
AI_DB_BASE_PARENT_DIR = PROJECT_ROOT / "aaoifi_vector_db_versions_django"
AI_DEFAULT_DB_DIR = AI_DB_BASE_PARENT_DIR / "default_db"
AI_VISUALIZATION_TEMP_DIR = AI_OUTPUT_DIR / "temp_visuals"

# Ensure these directories exist
os.makedirs(AI_PDF_INPUT_FOLDER, exist_ok=True)
os.makedirs(AI_OUTPUT_DIR, exist_ok=True)
os.makedirs(AI_DB_BASE_PARENT_DIR, exist_ok=True)
os.makedirs(AI_DEFAULT_DB_DIR, exist_ok=True)
os.makedirs(AI_VISUALIZATION_TEMP_DIR, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'pdfs'), exist_ok=True)


# Logging (can be more detailed)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Set to DEBUG for more verbose output
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'standards_analysis': { # Your app's logger
            'handlers': ['console'],
            'level': 'DEBUG', # Or INFO
            'propagate': False,
        },
        # Add loggers for AI components if they use specific names
    }
}