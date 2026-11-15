import os

class BaseConfig:
    DEBUG = False
    PORT = 5001
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL if DATABASE_URL else "sqlite:///temp.db"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET", "default")
    JWT_LIFETIME_SECONDS = int(os.environ.get("JWT_LIFETIME_SECONDS", 3600))

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    PORT = 5001
    

class ProductionConfig(BaseConfig):
    DEBUG = False
    PORT = int(os.environ.get("PORT", 5001))
    

class TestingConfig(BaseConfig):
    DEBUG = True
    PORT = 5001
    TESTING = True
   

    
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}