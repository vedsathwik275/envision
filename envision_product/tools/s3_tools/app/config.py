"""
Configuration settings for the Email Attachment Processing Tool.

This module uses Pydantic's BaseSettings for managing environment variables.
"""
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gmail API settings
    gmail_client_id: Optional[str] = Field(None, description="Gmail API OAuth client ID")
    gmail_client_secret: Optional[str] = Field(None, description="Gmail API OAuth client secret")
    gmail_redirect_uri: str = Field("http://localhost:8000/auth/callback", description="OAuth redirect URI")
    
    # S3 settings
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key")
    s3_bucket_name: str = Field("email-attachments", description="S3 bucket name for storing attachments")
    s3_region: str = Field("us-east-1", description="AWS region for S3 bucket")
    
    # Application settings
    app_name: str = Field("Email Attachment Processing Tool", description="Application name")
    debug: bool = Field(False, description="Debug mode")
    
    # Target attachment filenames
    target_filenames: list[str] = Field(
        default_factory=lambda: [
            "daily_metrics.csv",
            "user_data.json",
            "transaction_log.csv"
        ],
        description="List of target attachment filenames to process"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings() 