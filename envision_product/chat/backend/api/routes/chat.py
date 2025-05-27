"""
API Routes for Chat Operations.

Provides HTTP and WebSocket endpoints for interacting with the RAG chatbot.
"""
import json
import logging

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    WebSocket, 
    WebSocketDisconnect,
    Path,
    status,
    Request
)

from ..models import ChatRequest, ChatResponse, ErrorResponse
from ..services.kb_service import KBService # Still needed for type hint if ChatService takes it directly
from ..services.chat_service import ChatService
from ..core.exceptions import (
    KnowledgeBaseNotFoundException,
    QueryProcessingException,
    RAGChatbotException
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Chat"],
    responses={
        404: {"description": "Knowledge Base not found for chat", "model": ErrorResponse},
        400: {"description": "Invalid chat request", "model": ErrorResponse},
        500: {"description": "Internal server error during chat", "model": ErrorResponse},
    }
)

# Updated Dependency for ChatService to use app.state singleton
def get_chat_service(request: Request) -> ChatService:
    """Dependency to get the singleton ChatService instance from app.state."""
    # ChatService itself is initialized with KBService in main.py's lifespan
    return request.app.state.chat_service

@router.post(
    "/knowledge_bases/{kb_id}/chat",
    response_model=ChatResponse,
    summary="Chat with a Knowledge Base (HTTP)",
    description="Send a query to the specified knowledge base and receive a response. This is a standard HTTP request/response."
)
async def http_chat_with_kb(
    chat_request: ChatRequest,
    kb_id: str = Path(..., description="The ID of the knowledge base to chat with."),
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    HTTP endpoint for sending a query to a Knowledge Base.

    Args:
        chat_request: The user's query.
        kb_id: The ID of the Knowledge Base.
        chat_service: Injected ChatService instance.

    Returns:
        The chatbot's response.
    """
    try:
        response = await chat_service.process_chat_query(kb_id=kb_id, chat_request=chat_request)
        return response
    except KnowledgeBaseNotFoundException as e:
        logger.warning(f"HTTP Chat: KB '{kb_id}' not found. Error: {e.message}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except QueryProcessingException as e:
        logger.error(f"HTTP Chat: Error processing query for KB '{kb_id}'. Error: {e.message}", exc_info=e.details.get('original_error'))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except RAGChatbotException as e:
        logger.error(f"HTTP Chat: RAG backend error for KB '{kb_id}'. Error: {e.message}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        logger.error(f"HTTP Chat: Unexpected error for KB '{kb_id}'. Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")


@router.websocket("/knowledge_bases/{kb_id}/ws")
async def websocket_chat_with_kb(
    websocket: WebSocket,
    kb_id: str = Path(..., description="The ID of the knowledge base to chat with via WebSocket."),
    chat_service: ChatService = Depends(get_chat_service) # This now correctly uses the app.state.chat_service
):
    """
    WebSocket endpoint for interactive chat with a Knowledge Base.

    Connects via WebSocket, accepts JSON messages conforming to ChatRequest,
    and sends back JSON messages conforming to ChatResponse.

    Args:
        websocket: The WebSocket connection instance.
        kb_id: The ID of the Knowledge Base.
        chat_service: Injected ChatService instance.
    """
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for KB '{kb_id}' from {websocket.client}")

    try:
        # Initial check if KB exists and chatbot can be loaded. 
        # This provides immediate feedback if the KB_ID is invalid.
        # Accessing kb_service via the already injected chat_service
        _ = chat_service.kb_service.get_chatbot_instance(kb_id) # Will raise KnowledgeBaseNotFoundException if not ready
        await websocket.send_json({"status": "connected", "kb_id": kb_id, "message": "Successfully connected to chat."})

        while True:
            try:
                raw_data = await websocket.receive_text()
                logger.debug(f"WebSocket KB '{kb_id}': Received raw data: {raw_data}")
                try:
                    data = json.loads(raw_data)
                    chat_request = ChatRequest(**data) # Validate incoming data against ChatRequest model
                except json.JSONDecodeError:
                    logger.warning(f"WebSocket KB '{kb_id}': Invalid JSON received: {raw_data}")
                    await websocket.send_json(ErrorResponse(message="Invalid JSON format.", details={"received_data": raw_data}).model_dump(), mode="text")
                    continue
                except Exception as pydantic_exc: # Catch Pydantic validation errors
                    logger.warning(f"WebSocket KB '{kb_id}': Invalid ChatRequest structure: {pydantic_exc}")
                    await websocket.send_json(ErrorResponse(message="Invalid request structure.", details=str(pydantic_exc)).model_dump(), mode="text")
                    continue

                logger.info(f"WebSocket KB '{kb_id}': Processing query: '{chat_request.query}'")
                response = await chat_service.process_chat_query(kb_id=kb_id, chat_request=chat_request)
                await websocket.send_json(response.model_dump(), mode="text")
                logger.debug(f"WebSocket KB '{kb_id}': Sent response for query '{chat_request.query}'")

            except WebSocketDisconnect:
                logger.info(f"WebSocket KB '{kb_id}': Client {websocket.client} disconnected.")
                break # Exit the loop on disconnect
            except KnowledgeBaseNotFoundException as e:
                logger.warning(f"WebSocket KB '{kb_id}': KB not found during ongoing session. Error: {e.message}")
                await websocket.send_json(ErrorResponse(message=e.message, details=e.details).model_dump(), mode="text")
            except QueryProcessingException as e:
                logger.error(f"WebSocket KB '{kb_id}': Error processing query. Error: {e.message}", exc_info=e.details.get('original_error'))
                await websocket.send_json(ErrorResponse(message=e.message, details=e.details).model_dump(), mode="text")
            except RAGChatbotException as e:
                logger.error(f"WebSocket KB '{kb_id}': RAG backend error. Error: {e.message}", exc_info=True)
                await websocket.send_json(ErrorResponse(message=e.message, details=e.details).model_dump(), mode="text")
            except Exception as e: # Catch-all for other unexpected errors within the loop
                logger.error(f"WebSocket KB '{kb_id}': Unexpected error in loop. Error: {str(e)}", exc_info=True)
                try:
                    await websocket.send_json(ErrorResponse(message="An unexpected server error occurred.", details=str(e)).model_dump(), mode="text")
                except Exception as send_err:
                    logger.error(f"WebSocket KB '{kb_id}': Failed to send error to client {websocket.client}. Error: {send_err}")
                break
                
    except KnowledgeBaseNotFoundException as e: # Initial KB check failed
        logger.warning(f"WebSocket KB '{kb_id}': Initial KB check failed, KB not found. Error: {e.message}")
        try:
            await websocket.send_json(ErrorResponse(message=e.message, details=e.details).model_dump(), mode="text")
        except Exception as send_err:
             logger.error(f"WebSocket KB '{kb_id}': Failed to send initial KB not found error to client. Error: {send_err}")

    except Exception as e: # Catch-all for errors during WebSocket setup
        logger.error(f"WebSocket KB '{kb_id}': Major error during WebSocket setup or initial connection for {websocket.client}. Error: {str(e)}", exc_info=True)
        if websocket.client_state == websocket.client_state.CONNECTED:
            try:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            except Exception as close_err:
                logger.error(f"WebSocket KB '{kb_id}': Error trying to close WebSocket after setup failure: {close_err}")
    finally:
        logger.info(f"WebSocket KB '{kb_id}': Connection closed for client {websocket.client}.") 