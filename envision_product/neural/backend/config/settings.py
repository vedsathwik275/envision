#!/usr/bin/env python3
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # File storage settings
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Training settings
    MAX_TRAINING_TIME: int = 3600  # 1 hour in seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Create directory structure
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "files"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "models"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "predictions"), exist_ok=True) 