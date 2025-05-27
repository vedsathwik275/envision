"""
API Routes for Knowledge Base Management.

Provides endpoints for creating, listing, retrieving,
and managing knowledge bases and their documents.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, status, Request

from ..models import (
    CreateKBRequest,
    KBInfo,
    DocumentInfo,
    ProcessKBRequest,
    ErrorResponse
)
from ..services.kb_service import KBService
from ..core.exceptions import (
    KnowledgeBaseNotFoundException,
    DocumentProcessingException,
    RAGChatbotException
)
from ..core.config import settings # For potential future use or if needed by routes directly

router = APIRouter(
    prefix="/knowledge_bases",
    tags=["Knowledge Bases"],
    responses={
        404: {"description": "Knowledge Base not found", "model": ErrorResponse},
        400: {"description": "Invalid request", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    }
)

# Updated Dependency for KBService to use app.state singleton
def get_kb_service(request: Request) -> KBService:
    """Dependency to get the singleton KBService instance from app.state."""
    return request.app.state.kb_service

@router.post(
    "/",
    response_model=KBInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Knowledge Base",
    description="Creates a new knowledge base with the given name and optional description.",
    responses={
        status.HTTP_201_CREATED: {"description": "Knowledge Base created successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input or KB already exists", "model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Failed to create Knowledge Base", "model": ErrorResponse},
    }
)
def create_knowledge_base(
    kb_data: CreateKBRequest,
    kb_service: KBService = Depends(get_kb_service)
) -> KBInfo:
    """
    Endpoint to create a new Knowledge Base.

    Args:
        kb_data: Request body containing the name and optional description for the new KB.
        kb_service: Injected KBService instance.

    Returns:
        Information about the created Knowledge Base.

    Raises:
        HTTPException: 400 if KB already exists or input is invalid.
        HTTPException: 500 if an internal error occurs.
    """
    try:
        created_kb = kb_service.create_kb(name=kb_data.name, description=kb_data.description)
        return created_kb
    except DocumentProcessingException as e: # Covers KB already exists or other creation issues
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except RAGChatbotException as e: # More generic internal errors from service
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@router.get(
    "/",
    response_model=List[KBInfo],
    summary="List all Knowledge Bases",
    description="Retrieves a list of all available knowledge bases with their summary information.",
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved list of KBs"}
    }
)
def list_knowledge_bases(
    kb_service: KBService = Depends(get_kb_service)
) -> List[KBInfo]:
    """
    Endpoint to list all available Knowledge Bases.

    Args:
        kb_service: Injected KBService instance.

    Returns:
        A list of KBInfo objects.
    """
    try:
        return kb_service.list_kbs()
    except RAGChatbotException as e: # More generic internal errors from service
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list knowledge bases.")

@router.get(
    "/{kb_id}",
    response_model=KBInfo,
    summary="Get Knowledge Base Details",
    description="Retrieves detailed information about a specific knowledge base by its ID.",
    responses={
        status.HTTP_200_OK: {"description": "Successfully retrieved KB details"},
        status.HTTP_404_NOT_FOUND: {"description": "Knowledge Base not found", "model": ErrorResponse},
    }
)
def get_knowledge_base(
    kb_id: str,
    kb_service: KBService = Depends(get_kb_service)
) -> KBInfo:
    """
    Endpoint to get details of a specific Knowledge Base.

    Args:
        kb_id: The ID of the knowledge base to retrieve.
        kb_service: Injected KBService instance.

    Returns:
        KBInfo object for the specified knowledge base.

    Raises:
        HTTPException: 404 if the KB is not found.
        HTTPException: 500 if an internal error occurs.
    """
    try:
        kb_info = kb_service.get_kb(kb_id)
        if kb_info is None:
            raise KnowledgeBaseNotFoundException(kb_id)
        return kb_info
    except KnowledgeBaseNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except RAGChatbotException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred retrieving KB '{kb_id}': {str(e)}")


@router.post(
    "/{kb_id}/documents",
    response_model=DocumentInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to a Knowledge Base",
    description="Uploads a single document file to the specified knowledge base. The document will be stored for later processing.",
    responses={
        status.HTTP_201_CREATED: {"description": "Document uploaded successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request or file error", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Knowledge Base not found", "model": ErrorResponse},
    }
)
async def upload_document_to_kb(
    kb_id: str,
    file: UploadFile = File(..., description="The document file to upload."),
    kb_service: KBService = Depends(get_kb_service)
) -> DocumentInfo:
    """
    Endpoint to upload a document to a specific Knowledge Base.

    Args:
        kb_id: The ID of the knowledge base.
        file: The document file to upload.
        kb_service: Injected KBService instance.

    Returns:
        Information about the uploaded document.

    Raises:
        HTTPException: 400 for file errors or processing issues.
        HTTPException: 404 if the KB is not found.
        HTTPException: 500 if an internal error occurs.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name cannot be empty.")

    try:
        doc_info = await kb_service.upload_document(kb_id=kb_id, file=file)
        return doc_info
    except KnowledgeBaseNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DocumentProcessingException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except RAGChatbotException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload document: {str(e)}")


@router.post(
    "/{kb_id}/process",
    response_model=KBInfo,
    summary="Process a Knowledge Base",
    description="Triggers the processing of all uploaded documents in the specified knowledge base. This includes loading, splitting, embedding, and indexing the documents.",
    responses={
        status.HTTP_200_OK: {"description": "Knowledge Base processing initiated and completed (or queued if async)"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request or processing error", "model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"description": "Knowledge Base not found", "model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Missing required configuration (e.g., OpenAI API Key)", "model": ErrorResponse}
    }
)
def process_knowledge_base(
    kb_id: str,
    process_request: ProcessKBRequest,
    kb_service: KBService = Depends(get_kb_service)
) -> KBInfo:
    """
    Endpoint to trigger processing for a Knowledge Base.

    Args:
        kb_id: The ID of the knowledge base to process.
        process_request: Request body containing processing parameters like retriever type.
        kb_service: Injected KBService instance.

    Returns:
        Updated KBInfo for the knowledge base after processing.

    Raises:
        HTTPException: 400 for processing errors or invalid requests.
        HTTPException: 404 if the KB is not found.
        HTTPException: 422 if configuration like API keys are missing.
        HTTPException: 500 if an internal error occurs.
    """
    try:
        # OPENAI_API_KEY check is now within kb_service.process_kb, raising DocumentProcessingException
        updated_kb_info = kb_service.process_kb(kb_id=kb_id, process_request=process_request)
        return updated_kb_info
    except KnowledgeBaseNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DocumentProcessingException as e:
        # Check for specific message indicating API key issue
        if "OPENAI_API_KEY not set" in e.message:
             raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except RAGChatbotException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process knowledge base: {str(e)}")

# Placeholder for future: Maybe an endpoint to get KB processing status
# @router.get("/{kb_id}/status", response_model=KBStatus)
# def get_knowledge_base_status(kb_id: str, kb_service: KBService = Depends(get_kb_service)):
#     # ... implementation ...
#     pass 