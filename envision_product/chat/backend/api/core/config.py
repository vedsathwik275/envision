from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load .env file from the current directory (api/)
# This is good, but pydantic-settings can also load it directly via Config.env_file
load_dotenv() 

class Settings(BaseSettings):
    """Application settings."""
    # API and Services Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here_if_not_set")
    storage_path: str = os.getenv("STORAGE_PATH", "../knowledge_bases") # Relative to the api folder
    
    # Application Behavior
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    app_name: str = os.getenv("APP_NAME", "RAG Chatbot API")
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")

    # Server Configuration
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8004")) # Ensure port is int

    # CORS Configuration
    # Expects a comma-separated string in .env, e.g., CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
    cors_origins_str: str = os.getenv("CORS_ORIGINS", "*")
    
    @property
    def cors_origins(self) -> list[str]:
        if self.cors_origins_str == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins_str.split(",")]

    class Config:
        env_file = ".env" # Specifies the .env file to load (pydantic-settings will look for it)
        env_file_encoding = "utf-8"
        extra = "ignore" # Ignore extra fields from .env if any

settings = Settings() 