"""
Service layer for handling chat operations.

This service uses KBService to get chatbot instances and processes user queries.
"""
import logging
from typing import Any, Dict, Optional

from .kb_service import KBService
# For type hinting, we might need the actual FixedEnhancedRAGChatbot type
# but the instance is obtained via kb_service
try:
    from .poc_chatbot_scripts.enhanced_main_chatbot import FixedEnhancedRAGChatbot
except ImportError:
    FixedEnhancedRAGChatbot = type('FixedEnhancedRAGChatbot', (object,), {})

from ..models import ChatRequest, ChatResponse
from ..core.exceptions import (
    KnowledgeBaseNotFoundException,
    QueryProcessingException,
    RAGChatbotException
)

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat queries against knowledge bases."""

    def __init__(self, kb_service: KBService):
        """
        Initializes the ChatService.

        Args:
            kb_service: An instance of KBService to interact with knowledge bases
                        and loaded chatbot instances.
        """
        self.kb_service = kb_service

    async def process_chat_query(self, kb_id: str, chat_request: ChatRequest) -> ChatResponse:
        """
        Processes a user's chat query against the specified knowledge base.

        Args:
            kb_id: The ID of the knowledge base to query.
            chat_request: The chat request object containing the user's query.

        Returns:
            A ChatResponse object with the answer, confidence, and sources.

        Raises:
            KnowledgeBaseNotFoundException: If the KB or a ready chatbot instance is not found.
            QueryProcessingException: If there's an error during the query processing by the RAG chain.
            RAGChatbotException: For other generic chatbot-related errors.
        """
        logger.info(f"Processing chat query for KB '{kb_id}': '{chat_request.query}'")
        try:
            # Get the specific chatbot instance for the KB
            # get_chatbot_instance already checks if KB is processed and ready
            chatbot_instance = self.kb_service.get_chatbot_instance(kb_id)
            logger.debug(f"Retrieved chatbot instance for KB '{kb_id}'. Type: {type(chatbot_instance)}")

            if not hasattr(chatbot_instance, 'get_enhanced_response'):
                logger.error(f"Chatbot instance for KB '{kb_id}' does not have 'get_enhanced_response' method.")
                raise QueryProcessingException(
                    message=f"Chatbot for KB '{kb_id}' is not correctly configured.",
                    details={"kb_id": kb_id, "issue": "get_enhanced_response method missing"}
                )

            # Call the chatbot's get_enhanced_response method
            # Assuming get_enhanced_response is synchronous. If it were async, we'd await it.
            raw_response: Optional[Dict[str, Any]] = chatbot_instance.get_enhanced_response(chat_request.query)

            if raw_response is None or not isinstance(raw_response, dict):
                logger.warning(f"Chatbot for KB '{kb_id}' returned an empty or invalid response for query: '{chat_request.query}'. Response: {raw_response}")
                return ChatResponse(
                    kb_id=kb_id,
                    query=chat_request.query,
                    answer="Sorry, I couldn't find an answer to your question.",
                    confidence=0.0,
                    sources=[]
                )
            
            logger.info(f"Raw response from chatbot for KB '{kb_id}': {raw_response}")

            # Adapt the raw response to the ChatResponse model
            # The keys ('answer', 'confidence', 'sources') should match what FixedEnhancedRAGChatbot.get_enhanced_response returns.
            answer = raw_response.get('answer', "No answer provided.")
            confidence = raw_response.get('confidence')
            sources = raw_response.get('sources')

            return ChatResponse(
                kb_id=kb_id,
                query=chat_request.query,
                answer=str(answer),
                confidence=float(confidence) if confidence is not None else 0.0,
                sources=sources if sources is not None else [],
                debug_info=raw_response.get('debug_info')
            )

        except KnowledgeBaseNotFoundException as e:
            logger.warning(f"KnowledgeBaseNotFoundException while processing query for KB '{kb_id}': {e}")
            raise
        except QueryProcessingException as e:
            logger.error(f"QueryProcessingException for KB '{kb_id}', query '{chat_request.query}': {e}", exc_info=True)
            raise
        except RAGChatbotException as e:
            logger.error(f"RAGChatbotException for KB '{kb_id}', query '{chat_request.query}': {e}", exc_info=True)
            raise QueryProcessingException(message=f"Error during chat processing: {e.message}", details=e.details)
        except Exception as e:
            logger.error(f"Unexpected error processing chat query for KB '{kb_id}': {e}", exc_info=True)
            raise QueryProcessingException(
                message=f"An unexpected error occurred while processing your chat query for KB '{kb_id}'.",
                details={"original_error": str(e)}
            ) 