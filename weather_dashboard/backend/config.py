"""Configuration settings for Weather Dashboard."""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # API Keys
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    
    # Flask Settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///weather_dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Settings
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    OPENWEATHER_GEO_URL = 'https://api.openweathermap.org/geo/1.0'
    
    # Cache Settings (in seconds)
    CACHE_CURRENT_WEATHER = 600  # 10 minutes
    CACHE_FORECAST = 1800  # 30 minutes
    CACHE_ALERTS = 300  # 5 minutes
    CACHE_LOCATION_SEARCH = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 100  # Requests per minute
    
    # Weather Units
    SUPPORTED_UNITS = ['metric', 'imperial', 'standard']
    DEFAULT_UNITS = 'metric'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']
    

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return configs.get(env, DevelopmentConfig)
