from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Models
class CreateKBRequest(BaseModel):
    """Request model for creating a new knowledge base."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the knowledge base.")
    description: Optional[str] = Field(None, max_length=500, description="Optional description for the KB.")

class ProcessKBRequest(BaseModel):
    """Request model for processing documents in a knowledge base."""
    retriever_type: str = Field("hybrid", description="Retriever type to use (e.g., standard, hybrid, multi_query, advanced_hybrid).")
    # Add other processing options if needed, e.g., chunk_size, chunk_overlap, force_reprocess

class ChatRequest(BaseModel):
    """Request model for sending a query to the chatbot."""
    query: str = Field(..., min_length=1, description="The user's query.")
    # Add other chat options if needed, e.g., session_id, temperature

# Response Models
class KBInfo(BaseModel):
    """Response model for knowledge base information."""
    id: str = Field(..., description="Unique identifier for the knowledge base (usually the name).")
    name: str = Field(..., description="Name of the knowledge base.")
    description: Optional[str] = Field(None, description="Description of the knowledge base.")
    document_count: int = Field(0, description="Number of documents in the KB.")
    chunk_count: int = Field(0, description="Total number of chunks in the KB.")
    status: str = Field("unknown", description="Current status of the KB (e.g., new, processing, ready, error).")
    created_at: Optional[datetime] = Field(None, description="Timestamp of KB creation.")
    last_processed_at: Optional[datetime] = Field(None, description="Timestamp of last processing.")

class DocumentInfo(BaseModel):
    """Response model for uploaded document information."""
    id: str = Field(..., description="Unique identifier for the document (e.g., filename or a generated ID).")
    filename: str = Field(..., description="Original filename of the uploaded document.")
    content_type: Optional[str] = Field(None, description="MIME type of the document.")
    size: int = Field(..., description="Size of the document in bytes.")
    kb_id: str = Field(..., description="ID of the knowledge base this document belongs to.")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the document was uploaded.")
    message: str = Field("File uploaded successfully", description="Status message for the upload.")

class ChatResponse(BaseModel):
    """Response model for a chatbot query."""
    answer: str = Field(..., description="The chatbot's answer to the query.")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score of the answer.")
    sources: List[Dict[str, Any]] = Field([], description="List of source documents/chunks used for the answer.")
    processing_time: Optional[float] = Field(None, description="Time taken to process the query in seconds.")
    kb_id: Optional[str] = Field(None, description="ID of the knowledge base used for this response.")
    query: Optional[str] = Field(None, description="The original query that led to this response.")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Optional debug information.")

class HealthCheckResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str = "ok"
    name: Optional[str] = None
    version: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# General Error Response Model
class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="The type of error that occurred.")
    message: str = Field(..., description="A human-readable message describing the error.")
    details: Optional[Any] = Field(None, description="Optional details about the error, can be a dict or list.") 