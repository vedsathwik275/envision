from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional

class RAGChatbotException(Exception):
    """Base exception for the RAG Chatbot API."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

class KnowledgeBaseNotFoundException(RAGChatbotException):
    """Raised when a knowledge base is not found."""
    def __init__(self, kb_id: str, details: Optional[dict] = None):
        super().__init__(message=f"Knowledge base with ID '{kb_id}' not found.", 
                         status_code=status.HTTP_404_NOT_FOUND, 
                         details=details)

class DocumentProcessingException(RAGChatbotException):
    """Raised during errors in document processing or upload."""
    def __init__(self, message: str = "Error processing document.", details: Optional[dict] = None):
        super().__init__(message=message, 
                         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                         details=details)

class QueryProcessingException(RAGChatbotException):
    """Raised during errors in query processing or chat generation."""
    def __init__(self, message: str = "Error processing query.", details: Optional[dict] = None):
        super().__init__(message=message, 
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                         details=details)

# Exception Handlers

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic RequestValidationError."""
    # You can customize the error response structure as needed
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "RequestValidationError",
            "message": "Request validation failed. Please check your input.",
            "details": errors
        }
    )

async def rag_chatbot_exception_handler(request: Request, exc: RAGChatbotException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details or {}
        },
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail, # FastAPI's HTTPException uses 'detail'
            "details": exc.headers or {}
        },
    )

async def generic_exception_handler(request: Request, exc: Exception):
    # Log the exception here if you have a logger configured
    # logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred on the server.",
            "details": {"exception_type": exc.__class__.__name__}
        },
    )

# You would register these handlers in main.py 