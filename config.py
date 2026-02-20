"""
Enterprise Configuration Module
Centralized configuration for the Multi-AI Voice Assistant
"""

import os
import warnings
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask Configuration
    _secret_key = os.getenv('SECRET_KEY')
    if not _secret_key:
        if os.getenv('FLASK_ENV') == 'production':
            raise ValueError("SECRET_KEY environment variable must be set in production")
        _secret_key = 'dev-secret-key-NOT-FOR-PRODUCTION'
        warnings.warn("Using development SECRET_KEY. Set SECRET_KEY env var for production.", UserWarning)
    
    SECRET_KEY = _secret_key
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Session Configuration - Enhanced Security
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # AI Services Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', 30))
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    GEMINI_TIMEOUT = int(os.getenv('GEMINI_TIMEOUT', 30))
    
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_TIMEOUT = int(os.getenv('DEEPSEEK_TIMEOUT', 30))
    
    # Voice Configuration
    VOICE_ENGINE = os.getenv('VOICE_ENGINE', 'pyttsx3')  # pyttsx3 or edge-tts
    VOICE_RATE = int(os.getenv('VOICE_RATE', 150))
    VOICE_VOLUME = float(os.getenv('VOICE_VOLUME', 1.0))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # Fusion Engine Configuration
    FUSION_ENABLE_DEDUPLICATION = os.getenv('FUSION_ENABLE_DEDUPLICATION', 'true').lower() == 'true'
    FUSION_MAX_LENGTH = int(os.getenv('FUSION_MAX_LENGTH', 2000))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # In production, validate required API keys are set
    @classmethod
    def validate_production(cls):
        """Validate all required keys are configured in production"""
        required_keys = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'DEEPSEEK_API_KEY', 'SECRET_KEY']
        missing = []
        for key in required_keys:
            if not getattr(cls, key):
                missing.append(key)
        if missing:
            raise ValueError(f"Production mode requires these environment variables: {', '.join(missing)}")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        config = ProductionConfig
        config.validate_production()
        return config
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig