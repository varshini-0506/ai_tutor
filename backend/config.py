import os
from typing import Optional

class Config:
    """Configuration class for the AI Tutor application"""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    NEON_DB_URL = os.getenv('NEON_DB_URL')  # Alternative environment variable name
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours in seconds
    
    # API Configuration   
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY','AIzaSyBY7gxBxXmamsKvuGg0MO2PWiR4ka21JT0')
    GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    # File Storage Configuration
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
    
    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the database URL, preferring Neon DB URL"""
        return cls.NEON_DB_URL or cls.DATABASE_URL
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.get_database_url():
            print("Warning: DATABASE_URL or NEON_DB_URL not set")
            return False
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("=== AI Tutor Configuration ===")
        print(f"Database URL: {'Set' if cls.get_database_url() else 'Not Set'}")
        print(f"JWT Secret: {'Set' if cls.JWT_SECRET_KEY != 'your-secret-key' else 'Using Default'}")
        print(f"Gemini API Key: {'Set' if cls.GEMINI_API_KEY != 'AIzaSyAW0sxYjOyJF7rHf8PjD80ZPseWtvOXzTQ' else 'Using Default'}")
        print(f"Debug Mode: {cls.DEBUG}")
        print(f"Host: {cls.HOST}")
        print(f"Port: {cls.PORT}")
        print(f"Reports Directory: {cls.REPORTS_DIR}")
        print("=============================")

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', '*']

class ProductionConfig(Config):
    DEBUG = False
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://yourdomain.com').split(',')

class TestingConfig(Config):
    DEBUG = True
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config(environment: str = None) -> Config:
    """Get configuration for the specified environment"""
    env = environment or os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig) 