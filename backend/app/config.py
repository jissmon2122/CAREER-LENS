import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _parse_allowed_origins():
    default_origins = [
        'https://careerlens-iota.vercel.app',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    origins = []

    # Parse FRONTEND_URL
    raw_frontend = (os.getenv('FRONTEND_URL') or '').strip()
    if raw_frontend and raw_frontend != '*':
        clean_front = raw_frontend.rstrip('/')
        if clean_front and clean_front not in origins:
            origins.append(clean_front)

    # Parse CORS_ORIGINS (supports comma, semicolon, whitespace, newlines)
    raw_origins = (os.getenv('CORS_ORIGINS') or '').strip()
    if raw_origins and raw_origins != '*':
        items = re.split(r'[,;\s]+', raw_origins)
        for item in items:
            clean_item = item.strip().rstrip('/')
            if clean_item and clean_item not in origins:
                origins.append(clean_item)

    # Always include required production origins and dev origins
    for default_orig in default_origins:
        if default_orig not in origins:
            origins.append(default_orig)

    return origins

class Config:
    """Base application configuration class."""
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_change_me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key_change_me')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Production CORS Configuration (Strict allowed origins for credential/cookie/JWT security)
    DEFAULT_CORS_ORIGINS = [
        'https://careerlens-iota.vercel.app',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    CORS_ORIGINS = _parse_allowed_origins()
    FRONTEND_URL = (os.getenv('FRONTEND_URL') or 'https://careerlens-iota.vercel.app').strip().rstrip('/')
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your_google_oauth_client_id.apps.googleusercontent.com')
    
    # Database Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/career_intelligence')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'career_intelligence')
    
    # Upload Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'uploads/resumes'))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '5242880'))  # 5 MB in bytes
    ALLOWED_EXTENSIONS = {'pdf'}

    # AI / NLP Semantic Intelligence Configuration
    AI_ENABLED = os.getenv('AI_ENABLED', 'true').lower() == 'true'
    AI_MODEL_NAME = os.getenv('AI_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
    AI_SEMANTIC_WEIGHT = float(os.getenv('AI_SEMANTIC_WEIGHT', '0.40'))
    EXISTING_MATCH_WEIGHT = float(os.getenv('EXISTING_MATCH_WEIGHT', '0.60'))

    # Live Job Search API & Provider Configuration
    JOB_API_PROVIDERS = [p.strip().lower() for p in os.getenv('JOB_API_PROVIDERS', 'adzuna,jooble,indianapi').split(',') if p.strip()]
    JOB_CACHE_TTL = int(os.getenv('LIVE_JOB_CACHE_TTL', os.getenv('JOB_CACHE_TTL', '21600')))  # 6 hours TTL
    LIVE_JOB_MAX_AGE_DAYS = int(os.getenv('LIVE_JOB_MAX_AGE_DAYS', '30'))
    JOB_API_TIMEOUT = int(os.getenv('JOB_API_TIMEOUT', '10'))
    JOB_API_DEFAULT_RESULTS = int(os.getenv('JOB_API_DEFAULT_RESULTS', '50'))

    # Adzuna API Configuration
    ADZUNA_ENABLED = os.getenv('ADZUNA_ENABLED', 'true').lower() == 'true'
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID') or os.getenv('JOB_API_APP_ID', '')
    ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY') or os.getenv('JOB_API_KEY', '')
    ADZUNA_COUNTRY = (os.getenv('ADZUNA_COUNTRY') or os.getenv('JOB_API_COUNTRY', 'in')).lower()
    ADZUNA_BASE_URL = os.getenv('ADZUNA_BASE_URL') or os.getenv('JOB_API_BASE_URL', 'https://api.adzuna.com/v1/api/jobs')
    ADZUNA_RESULTS_PER_PAGE = int(os.getenv('ADZUNA_RESULTS_PER_PAGE') or '50')
    ADZUNA_MAX_PAGES = int(os.getenv('ADZUNA_MAX_PAGES', '2'))
    ADZUNA_TIMEOUT = int(os.getenv('ADZUNA_TIMEOUT') or '10')

    # Jooble REST API Configuration
    JOOBLE_ENABLED = os.getenv('JOOBLE_ENABLED', 'true').lower() == 'true'
    JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY', '')
    JOOBLE_BASE_URL = os.getenv('JOOBLE_BASE_URL', 'https://in.jooble.org/api/')
    JOOBLE_RESULTS_PER_PAGE = int(os.getenv('JOOBLE_RESULTS_PER_PAGE', '50'))
    JOOBLE_MAX_PAGES = int(os.getenv('JOOBLE_MAX_PAGES', '2'))
    JOOBLE_TIMEOUT = int(os.getenv('JOOBLE_TIMEOUT', '10'))

    # IndianAPI Jobs API Configuration
    INDIANAPI_ENABLED = os.getenv('INDIANAPI_ENABLED', 'true').lower() == 'true'
    INDIANAPI_API_KEY = os.getenv('INDIANAPI_API_KEY', '')
    INDIANAPI_BASE_URL = os.getenv('INDIANAPI_BASE_URL', 'https://jobs.indianapi.in')
    INDIANAPI_RESULTS_LIMIT = int(os.getenv('INDIANAPI_RESULTS_LIMIT', '50'))
    INDIANAPI_TIMEOUT = int(os.getenv('INDIANAPI_TIMEOUT', '10'))

    @classmethod
    def validate_production_env(cls):
        """Validate critical configuration variables safely without leaking secret values."""
        warnings = []
        is_production = cls.ENV == 'production' or os.getenv('RENDER') == 'true'
        if is_production:
            if not cls.SECRET_KEY or cls.SECRET_KEY == 'default_secret_key_change_me':
                warnings.append("SECRET_KEY is using default placeholder in production.")
            if not cls.JWT_SECRET_KEY or cls.JWT_SECRET_KEY == 'default_jwt_secret_key_change_me':
                warnings.append("JWT_SECRET_KEY is using default placeholder in production.")
            if not cls.MONGO_URI or 'localhost' in cls.MONGO_URI:
                warnings.append("MONGO_URI appears to target a local database instead of production cluster.")
        return warnings


