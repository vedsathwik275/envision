"""
Configuration settings for the Email Attachment Processing Tool.

This module uses Pydantic Settings for managing environment variables.
"""
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Model configuration for Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Gmail API settings
    gmail_client_id: Optional[str] = Field(None, description="Gmail API OAuth client ID")
    gmail_client_secret: Optional[str] = Field(None, description="Gmail API OAuth client secret")
    gmail_redirect_uri: str = Field("http://localhost:8002/auth/callback", description="OAuth redirect URI")
    
    # S3 settings
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key")
    s3_bucket_name: str = Field("email-attachments", description="S3 bucket name for storing attachments")
    s3_region: str = Field("us-east-1", description="AWS region for S3 bucket")
    
    # Application settings
    app_name: str = Field("Email Attachment Processing Tool", description="Application name")
    debug: bool = Field(False, description="Debug mode")
    
    # Target attachment filenames
    target_filenames_str: Optional[str] = Field(None, description="Comma-separated list of target filenames", env="TARGET_FILENAMES")
    
    # Target email subjects
    target_subjects_str: Optional[str] = Field(None, description="Comma-separated list of target email subject patterns", env="TARGET_SUBJECTS")
    
    # Default target filenames if not provided in environment
    _default_target_filenames: List[str] = [
        "order_volume",
        "tender_performance",
        "carrier_performance"
    ]
    
    # Default target subjects if not provided in environment
    _default_target_subjects: List[str] = [
        "Order Volume Report",
        "Carrier Performance Report",
        "Tender Performance Report",
    ]
    
    @property
    def target_filenames(self) -> List[str]:
        """Get the list of target filenames."""
        if self.target_filenames_str:
            return [filename.strip() for filename in self.target_filenames_str.split(',')]
        return self._default_target_filenames
    
    @property
    def target_subjects(self) -> List[str]:
        """Get the list of target email subject patterns."""
        if self.target_subjects_str:
            return [subject.strip() for subject in self.target_subjects_str.split(',')]
        return self._default_target_subjects


# Create settings instance
settings = Settings() 