"""
Pydantic models for API requests and responses.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EmailInfo(BaseModel):
    """Model representing email information."""
    
    id: str = Field(..., description="Email ID")
    subject: str = Field(..., description="Email subject")
    has_target_attachments: bool = Field(
        ..., description="Whether the email has target attachments"
    )


class AttachmentInfo(BaseModel):
    """Model representing attachment information."""
    
    id: str = Field(..., description="Attachment ID")
    filename: str = Field(..., description="Attachment filename")
    mime_type: str = Field(..., description="Attachment MIME type")
    size: int = Field(..., description="Attachment size in bytes")
    is_target_file: bool = Field(
        ..., description="Whether the attachment is a target file"
    )


class UploadResponse(BaseModel):
    """Model representing an S3 upload response."""
    
    success: bool = Field(..., description="Whether the upload was successful")
    filename: str = Field(..., description="Filename of the uploaded file")
    s3_location: str = Field(..., description="S3 location of the uploaded file")
    metadata: Dict[str, str] = Field(..., description="Metadata of the uploaded file")


class ProcessingStatistics(BaseModel):
    """Model representing processing statistics."""
    
    total_emails_processed: int = Field(..., description="Total number of emails processed")
    total_attachments_found: int = Field(..., description="Total number of attachments found")
    target_attachments_processed: int = Field(
        ..., description="Number of target attachments processed"
    )
    successful_uploads: int = Field(..., description="Number of successful uploads")
    failed_uploads: int = Field(..., description="Number of failed uploads")
    processing_time_seconds: float = Field(..., description="Processing time in seconds")


class ProcessingResponse(BaseModel):
    """Model representing a batch processing response."""
    
    success: bool = Field(..., description="Whether the processing was successful")
    statistics: ProcessingStatistics = Field(..., description="Processing statistics")
    uploads: List[UploadResponse] = Field(..., description="List of upload responses")
    errors: Optional[List[Dict[str, str]]] = Field(
        None, description="List of errors encountered during processing"
    ) 