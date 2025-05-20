"""
Main application module for Email Attachment Processing Tool.

This module initializes the FastAPI application and includes all routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Email Attachment Processing Tool",
    description="API for processing email attachments and uploading to S3",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
# These will be added as we implement them

@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "message": "Email Attachment Processing Tool API",
        "version": "0.1.0",
        "docs_url": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 