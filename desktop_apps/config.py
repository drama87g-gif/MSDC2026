import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    
    # UI Configuration
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    APP_TITLE = "MSDC Hospital Management"
    
    # Database (for local caching)
    CACHE_DB = os.getenv('CACHE_DB', 'app_cache.db')
    
    # Printing Configuration
    PRINTER_NAME = os.getenv('PRINTER_NAME', 'default')
    PAPER_SIZE_A4 = (210, 297)  # mm
    PAPER_SIZE_A5 = (148, 210)  # mm
    
    # Barcode Configuration
    BARCODE_WIDTH = 150  # pixels
    BARCODE_HEIGHT = 80  # pixels
    
    # File Upload
    MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_PHOTO_FORMATS = ['jpg', 'jpeg', 'png', 'gif']
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Features
    ENABLE_BARCODE_SCANNER = os.getenv('ENABLE_BARCODE_SCANNER', 'true').lower() == 'true'
    ENABLE_PRINTER = os.getenv('ENABLE_PRINTER', 'true').lower() == 'true'
    OFFLINE_MODE = os.getenv('OFFLINE_MODE', 'false').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    API_BASE_URL = 'http://localhost:5000'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://api.msdc.local')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'development')
    return config.get(env, config['default'])
