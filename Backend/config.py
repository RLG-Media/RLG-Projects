"""
RLG Core Configuration Engine - Centralized Control Hub
Version: 7.0.0
Features: Multi-Environment Support, AI-Powered Dynamic Config, Region-Aware Settings
"""

import os
import json
from dotenv import load_dotenv
from datetime import timedelta
import pytz

load_dotenv()

class Config:
    """Base configuration with AI-optimized defaults"""
    
    # --------------------------
    # CORE APPLICATION SETTINGS
    # --------------------------
    RLG_VERSION = "1.0.0"
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DOMAIN = os.getenv('DOMAIN', 'rlgprojects.io')
    
    # --------------------------
    # AI & ML CONFIGURATION
    # --------------------------
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    AI_MODELS = {
        'scrum_master': 'deepseek/scrum-1.3b',
        'risk_predictor': 'deepseek/risk-2.0',
        'nlp_engine': 'deepseek/nlp-v5'
    }
    AI_REFRESH_INTERVAL = timedelta(hours=1)
    
    # --------------------------
    # DATA & ANALYTICS
    # --------------------------
    DATA_LAKE_PATH = os.getenv('DATA_PATH', './data_lake')
    MAX_TEAM_SIZE = int(os.getenv('MAX_TEAM_SIZE', 15))
    PERFORMANCE_THRESHOLDS = {
        'velocity': {'warning': 0.7, 'critical': 0.5},
        'risk': {'low': 0.3, 'medium': 0.6, 'high': 0.8}
    }
    
    # --------------------------
    # SECURITY & COMPLIANCE
    # --------------------------
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'rlg_secure_key_2024')
    GDPR_COMPLIANCE = json.loads(os.getenv('GDPR_SETTINGS', '{"enabled": true}'))
    DATA_RETENTION = {
        'projects': timedelta(days=730),
        'sprints': timedelta(days=365),
        'logs': timedelta(days=90)
    }
    
    # --------------------------
    # GLOBALIZATION & LOCALIZATION
    # --------------------------
    SUPPORTED_LANGUAGES = json.loads(os.getenv('LANGUAGES', '["en","es","fr","de","zh","ja"]'))
    TIMEZONE_MAP = pytz.all_timezones
    CURRENCY_FORMATS = json.loads(os.getenv('CURRENCY_FORMATS', 
        '{"default": "USD", "supported": ["USD","EUR","GBP","JPY","CNY"]}'))
    
    # --------------------------
    # AUTOMATION & SCHEDULING
    # --------------------------
    AUTOMATION_INTERVALS = {
        'standups': timedelta(hours=24),
        'reports': timedelta(weeks=1),
        'backlog_refinement': timedelta(days=3)
    }
    MAX_PARALLEL_SPRINTS = int(os.getenv('MAX_SPRINTS', 5))
    
    # --------------------------
    # INTEGRATIONS & SERVICES
    # --------------------------
    SLACK_CONFIG = {
        'token': os.getenv('SLACK_TOKEN'),
        'alert_channel': os.getenv('SLACK_ALERT_CHANNEL', 'general')
    }
    GITHUB_INTEGRATION = {
        'enabled': os.getenv('GITHUB_ENABLED', 'false') == 'true',
        'app_id': os.getenv('GITHUB_APP_ID'),
        'webhook_secret': os.getenv('GITHUB_WEBHOOK_SECRET')
    }
    
    # --------------------------
    # PERFORMANCE & SCALING
    # --------------------------
    DATABASE_POOL_SIZE = int(os.getenv('DB_POOL', 20))
    CACHE_CONFIG = {
        'backend': os.getenv('CACHE_BACKEND', 'redis'),
        'ttl': int(os.getenv('CACHE_TTL', 300))
    }
    LOAD_LIMITS = {
        'requests_per_minute': 1000,
        'concurrent_users': 500
    }
    
    # --------------------------
    # USER EXPERIENCE
    # --------------------------
    UI_DEFAULTS = {
        'theme': os.getenv('UI_THEME', 'dark'),
        'density': 'comfortable',
        'accessibility': {
            'high_contrast': False,
            'screen_reader': True
        }
    }
    PERSONALIZATION_WEIGHTS = {
        'historical': 0.6,
        'team_patterns': 0.3,
        'global_trends': 0.1
    }
    
    # --------------------------
    # ERROR HANDLING
    # --------------------------
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    ERROR_REPORTING = {
        'email': os.getenv('ERROR_EMAIL'),
        'slack_channel': os.getenv('ERROR_SLACK_CHANNEL')
    }
    
    # --------------------------
    # FEATURE TOGGLES
    # --------------------------
    FEATURE_FLAGS = {
        'ai_assistant': True,
        'auto_retrospectives': False,
        'predictive_scheduling': True,
        'multi_tenant': os.getenv('MULTI_TENANT', 'false') == 'true'
    }
import os

CACHE_CONFIG = {
    "host": os.getenv("CACHE_HOST", "localhost"),
    "port": int(os.getenv("CACHE_PORT", 6379)),
    "db": int(os.getenv("CACHE_DB", 0)),
    "timeout": int(os.getenv("CACHE_TIMEOUT", 300))
}

class DevelopmentConfig(Config):
    """Development-specific configurations with enhanced debugging"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DB_URI', 'sqlite:///dev.db')
    AI_MODEL_PRECISION = 'fp16'
    CACHE_CONFIG['ttl'] = 60  # Shorter cache for development

class ProductionConfig(Config):
    """Optimized production configuration with fail-safes"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DB_URI')
    AI_MODEL_PRECISION = 'fp32'
    Config.FEATURE_FLAGS['auto_retrospectives'] = True
    SECURITY_MIDDLEWARE = {
        'cors': {
            'origins': json.loads(os.getenv('CORS_ORIGINS', '["https://*.rlgprojects.io"]')),
            'methods': ['GET', 'POST', 'PUT', 'DELETE']
        },
        'rate_limiting': {
            'strategy': 'token_bucket',
            'storage': 'redis'
        }
    }

class TestingConfig(Config):
    """CI/CD testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    Config.FEATURE_FLAGS['multi_tenant'] = True
    AI_MODELS = {k: 'mock' for k in Config.AI_MODELS}

# Environment-based configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Dynamic configuration loader with fallback"""
    env = env or os.getenv('ENVIRONMENT', 'development')
    return config.get(env.lower(), config['default'])

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
AI_MODELS = {
    'risk_predictor': 'deepseek/risk-3.0',
    'scrum_master': 'deepseek/scrum-2.1'
}
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'zh', 'ja']
DEFAULT_LOCALE = 'en_US'

ERROR_LOGGING = {
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 2
}
TIMEZONE_FALLBACK = 'UTC'
CULTURAL_DATA_PATH = './cultural_time_patterns.json'

DATA_LAKE_PATH = './data_lake'
PASSWORD_POLICY = {
    'min_length': 12,
    'complexity': {'upper': True, 'special': True}
}
SMTP_SERVER = 'smtp.rlgprojects.com'

REDIS_URL = 'redis://localhost:6379'
RATE_LIMITS = {
    'api': {'limit': 300, 'window': 3600},
    'auth': {'limit': 20, 'window': 300}
}
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'zh', 'ja']