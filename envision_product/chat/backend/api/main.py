"""
Main application file for the RAG Chatbot FastAPI backend.

This file initializes the FastAPI application, includes routers,
sets up exception handlers, and manages application lifespan events
(like initializing shared services).
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    rag_chatbot_exception_handler,
    generic_exception_handler,
    RAGChatbotException # Generic base for our custom exceptions
)
from .routes import knowledge_bases as kb_routes
from .routes import chat as chat_routes
from .routes import historical_data as historical_routes
from .routes import spot_rate as spot_rate_routes
from .routes import recommendations as recommendation_routes
from .services.kb_service import KBService
from .services.chat_service import ChatService
from .models import HealthCheckResponse, ErrorResponse

# Configure basic logging
logging.basicConfig(level=settings.log_level.upper(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    Initializes and cleans up resources like service instances.
    """
    logger.info("Application startup: Initializing services...")
    # Initialize KBService as a singleton and store in app.state
    app.state.kb_service = KBService()
    logger.info(f"KBService initialized. Storage path: {app.state.kb_service.kb_manager.base_directory}")
    
    # Initialize ChatService with the singleton KBService and store in app.state
    app.state.chat_service = ChatService(kb_service=app.state.kb_service)
    logger.info("ChatService initialized.")
    
    yield
    
    logger.info("Application shutdown: Cleaning up resources...")
    # Add any cleanup logic here if needed (e.g., closing DB connections)
    # For KBService, loaded_chatbots are in memory, Python's GC will handle them.
    # If KBService managed persistent connections, they would be closed here.
    if hasattr(app.state, 'kb_service') and app.state.kb_service:
        logger.info("KBService shutting down. Loaded chatbots will be cleared from memory.")
        app.state.kb_service.loaded_chatbots.clear() # Explicitly clear if desired
    logger.info("Shutdown complete.")

# Initialize FastAPI app with lifespan manager
app = FastAPI(
    title=settings.app_name,
    description="API for managing and interacting with a Retrieval Augmented Generation (RAG) chatbot.",
    version="0.1.0",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"], # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register custom exception handlers
# These are defined in core.exceptions.py
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(FastAPIHTTPException, http_exception_handler) # Handles FastAPI's own HTTPException
app.add_exception_handler(RAGChatbotException, rag_chatbot_exception_handler) # Corrected handler
app.add_exception_handler(Exception, generic_exception_handler) # Generic fallback


# Include routers
app.include_router(kb_routes.router, prefix=settings.api_v1_prefix)
app.include_router(chat_routes.router, prefix=settings.api_v1_prefix) # chat routes are already prefixed with /knowledge_bases/{kb_id}
app.include_router(historical_routes.router, prefix=settings.api_v1_prefix)
app.include_router(spot_rate_routes.router, prefix=settings.api_v1_prefix)
app.include_router(recommendation_routes.router, prefix=settings.api_v1_prefix)


@app.get(
    f"{settings.api_v1_prefix}/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Perform a Health Check",
    description="Returns the status of the API, indicating if it is running correctly."
)
def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    """
    logger.debug("Health check endpoint called.")
    return HealthCheckResponse(status="ok", name=settings.app_name, version=app.version)

# Root path (optional)
@app.get("/", include_in_schema=False)
async def root():
    return {"message": f"Welcome to {settings.app_name}! API docs at {settings.api_v1_prefix}/docs"}


# The following is for local development with Uvicorn if this file is run directly.
# In production, you'd use a process manager like Gunicorn with Uvicorn workers.
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Uvicorn server for {settings.app_name} on http://{settings.server_host}:{settings.server_port}")
    uvicorn.run(
        "main:app", 
        host=settings.server_host, 
        port=settings.server_port, 
        reload=settings.debug, # Enable reload only in debug mode
        log_level=settings.log_level.lower()
    ) 