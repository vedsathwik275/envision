import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import UploadFile

# Direct imports: if these fail, it's a configuration or path problem that needs to be addressed directly.
from .poc_chatbot_scripts.knowledge_base_manager import KnowledgeBaseManager
from .poc_chatbot_scripts.enhanced_main_chatbot import FixedEnhancedRAGChatbot
# EnhancedDocumentProcessor might be needed if we want to get doc counts before full processing
# from .poc_chatbot_scripts.enhanced_dp import EnhancedDocumentProcessor 

from ..core.config import settings
from ..core.exceptions import KnowledgeBaseNotFoundException, DocumentProcessingException, QueryProcessingException, RAGChatbotException
from ..models import KBInfo, DocumentInfo, ProcessKBRequest

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KBService:
    """Service for managing Knowledge Bases and their documents."""
    def __init__(self):
        # Ensure the base storage path exists
        # The storage_path from settings is relative to the `api` directory where main.py will run.
        # So if settings.storage_path is '../knowledge_bases', it's one level above 'api'.
        # If KnowledgeBaseManager expects an absolute path or a path relative to its own location,
        # this needs to be handled carefully.
        # For now, assume KnowledgeBaseManager can handle the path as given by settings.
        absolute_storage_path = (Path(__file__).parent.parent / settings.storage_path).resolve()
        absolute_storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"KBService: Resolved storage path to: {absolute_storage_path}")
        self.kb_manager = KnowledgeBaseManager(base_directory=str(absolute_storage_path))
        self.loaded_chatbots: Dict[str, FixedEnhancedRAGChatbot] = {}
        logger.info(f"KBService initialized. Using storage path: {self.kb_manager.base_directory}")

    def create_kb(self, name: str, description: Optional[str] = None) -> KBInfo:
        """Creates a new knowledge base."""
        try:
            # Initialize with a 'creating' or 'pending_creation' status
            # The actual creation happens in kb_manager.create_knowledge_base
            # which sets initial metadata (doc count 0, chunk count 0, no explicit status)
            self.kb_manager.create_knowledge_base(name, description or "")
            logger.info(f"Successfully created knowledge base folder for: {name}")
            
            # After creation, immediately set status to 'new' in metadata
            self.kb_manager.update_metadata(name, status="new")
            
            kb_metadata_list = self.kb_manager.list_knowledge_bases()
            created_kb_meta = next((kb for kb in kb_metadata_list if kb.get('name') == name), None)

            if not created_kb_meta:
                logger.error(f"Failed to retrieve metadata for newly created KB: {name}")
                raise DocumentProcessingException(f"Failed to retrieve metadata for KB: {name}")

            # The status should now be 'new' from the metadata itself
            return KBInfo(
                id=created_kb_meta.get('name', name),
                name=created_kb_meta.get('name', name),
                description=created_kb_meta.get('description'),
                document_count=created_kb_meta.get('document_count', 0),
                chunk_count=created_kb_meta.get('chunk_count', 0),
                status=created_kb_meta.get('status', 'error_retrieving_status'), # Should pick up 'new'
                created_at=created_kb_meta.get('created_at')
            )
        except ValueError as e: # Handles if KB already exists from kb_manager
            logger.warning(f"Attempted to create already existing KB '{name}'. Error: {e}")
            # Try to fetch existing KB info if it already exists
            existing_kb = self.get_kb(name)
            if existing_kb:
                logger.info(f"KB '{name}' already existed. Returning its current info.")
                # We might want to raise a specific "already exists" exception with KBInfo
                # For now, let's re-raise to indicate creation failure but log it clearly
                raise DocumentProcessingException(message=f"Knowledge base '{name}' already exists.", details={"kb_name": name, "existing_kb_id": existing_kb.id})
            raise DocumentProcessingException(message=str(e), details={"kb_name": name})
        except Exception as e:
            logger.error(f"Error creating knowledge base '{name}': {e}", exc_info=True)
            raise DocumentProcessingException(f"Could not create knowledge base '{name}'. Error: {e}")

    def list_kbs(self) -> List[KBInfo]:
        """Lists all available knowledge bases."""
        try:
            kbs_metadata = self.kb_manager.list_knowledge_bases()
            infos = []
            for kb_meta in kbs_metadata:
                kb_id = kb_meta.get('name', 'unknown_id')
                status = kb_meta.get('status') # Get status directly
                if not status: # If status is None or empty string from metadata
                    # Use a simplified heuristic if explicit status is missing
                    status = self.get_kb_status_heuristic_simplified(kb_id, kb_meta)
                
                infos.append(KBInfo(
                    id=kb_id,
                    name=kb_meta.get('name', 'Unknown KB'),
                    description=kb_meta.get('description'),
                    document_count=kb_meta.get('document_count', 0),
                    chunk_count=kb_meta.get('chunk_count', 0),
                    status=status,
                    created_at=kb_meta.get('created_at'),
                    last_processed_at=kb_meta.get('last_updated') # 'last_updated' from KBM maps to this
                ))
            return infos
        except Exception as e:
            logger.error(f"Error listing knowledge bases: {e}", exc_info=True)
            return []

    def get_kb(self, kb_id: str) -> Optional[KBInfo]:
        """Retrieves details for a specific knowledge base."""
        try:
            # This will raise ValueError if path doesn't exist, caught below
            self.kb_manager.get_knowledge_base_path(kb_id) 
            
            kbs_metadata = self.kb_manager.list_knowledge_bases() # Reads all KBs metadata
            kb_meta = next((kb for kb in kbs_metadata if kb.get('name') == kb_id), None)
            
            if kb_meta:
                status = kb_meta.get('status') # Get status directly
                if not status: # If status is None or empty string from metadata
                    status = self.get_kb_status_heuristic_simplified(kb_id, kb_meta)
                
                return KBInfo(
                    id=kb_meta.get('name', kb_id),
                    name=kb_meta.get('name', kb_id),
                    description=kb_meta.get('description'),
                    document_count=kb_meta.get('document_count', 0),
                    chunk_count=kb_meta.get('chunk_count', 0),
                    status=status,
                    created_at=kb_meta.get('created_at'),
                    last_processed_at=kb_meta.get('last_updated')
                )
            logger.warning(f"Metadata for KB '{kb_id}' not found in list_knowledge_bases result, though path check might have passed or failed silently if not specific enough.")
            return None # Or raise KnowledgeBaseNotFoundException here?
        except ValueError: # Raised by kb_manager.get_knowledge_base_path if folder doesn't exist
            logger.warning(f"Knowledge base with ID '{kb_id}' not found (ValueError from kb_manager, likely path missing).")
            return None
        except Exception as e:
            logger.error(f"Error retrieving knowledge base '{kb_id}': {e}", exc_info=True)
            # Potentially wrap this in a more specific API exception
            raise RAGChatbotException(f"Could not retrieve KB '{kb_id}'. Error: {e}")

    async def upload_document(self, kb_id: str, file: UploadFile) -> DocumentInfo:
        """Uploads a document to the specified knowledge base's documents folder."""
        try:
            # Ensure KB exists before trying to get its document path
            kb_info_check = self.get_kb(kb_id)
            if not kb_info_check:
                raise KnowledgeBaseNotFoundException(kb_id=kb_id)

            kb_doc_path_str = self.kb_manager.get_documents_path(kb_id) 
            kb_doc_path = Path(kb_doc_path_str)

            file_path = kb_doc_path / file.filename
            
            # Consider adding a check for file type / extension if desired

            if file_path.exists():
                logger.warning(f"File '{file.filename}' already exists in KB '{kb_id}'. Overwriting.")
            
            written_bytes = 0
            try:
                with open(file_path, "wb+") as file_object:
                    content = await file.read() 
                    file_object.write(content)
                    written_bytes = len(content)
            except Exception as e_io:
                logger.error(f"IOError writing file '{file.filename}' to '{file_path}': {e_io}", exc_info=True)
                raise DocumentProcessingException(f"Failed to write file '{file.filename}'.", details={"kb_id": kb_id, "filename": file.filename})

            logger.info(f"Successfully uploaded '{file.filename}' ({written_bytes} bytes) to KB '{kb_id}'.")
            
            try:
                # Update document count and set status to 'needs_processing' or similar
                docs_in_kb = [f for f in kb_doc_path.iterdir() if f.is_file()]
                self.kb_manager.update_metadata(kb_id, document_count=len(docs_in_kb), status="needs_processing")
            except Exception as e_meta:
                logger.error(f"Failed to update metadata for KB '{kb_id}' after upload: {e_meta}", exc_info=True)
                # Even if metadata update fails, the upload was successful, so don't necessarily error out the request
                # but log it seriously. The status might become inconsistent.

            return DocumentInfo(
                id=file.filename, 
                filename=file.filename,
                content_type=file.content_type, # Be mindful of security with content_type
                size=written_bytes, 
                kb_id=kb_id
            )
        except KnowledgeBaseNotFoundException: # Re-raise if caught from get_kb
            raise
        except ValueError: # Should be caught by get_kb or if kb_manager.get_documents_path fails
            logger.error(f"Knowledge base '{kb_id}' not found for document upload (ValueError).")
            raise KnowledgeBaseNotFoundException(kb_id=kb_id)
        except DocumentProcessingException: # Re-raise if caught from IO error
            raise
        except Exception as e:
            logger.error(f"Error uploading document '{file.filename}' to KB '{kb_id}': {e}", exc_info=True)
            raise DocumentProcessingException(f"Could not upload document. Error: {str(e)}")

    def process_kb(self, kb_id: str, process_request: ProcessKBRequest) -> KBInfo:
        """Processes the documents in a knowledge base."""
        logger.info(f"Starting processing for KB '{kb_id}' with retriever: {process_request.retriever_type}")
        try:
            kb_info_pre_process = self.get_kb(kb_id)
            if not kb_info_pre_process:
                 raise KnowledgeBaseNotFoundException(kb_id=kb_id)

            # Pass the KBService's knowledge base manager path to the chatbot instance
            temp_chatbot_for_processing = FixedEnhancedRAGChatbot(base_kb_manager_directory=self.kb_manager.base_directory)
            
            if not os.getenv("OPENAI_API_KEY"):
                self.kb_manager.update_metadata(kb_id, status="error_config_missing_api_key")
                raise DocumentProcessingException("OPENAI_API_KEY not set, cannot process knowledge base.")

            logger.info(f"Calling FixedEnhancedRAGChatbot.setup_enhanced_knowledge_base for KB: {kb_id} (KBM base: {temp_chatbot_for_processing.kb_manager.base_directory})")
            
            # Update status to 'processing' before starting the potentially long operation
            self.kb_manager.update_metadata(kb_id, status="processing")

            success = temp_chatbot_for_processing.setup_enhanced_knowledge_base(
                kb_name=kb_id,
                retriever_type=process_request.retriever_type
            )

            if not success:
                logger.error(f"Processing failed for KB '{kb_id}' as reported by FixedEnhancedRAGChatbot script.")
                self.kb_manager.update_metadata(kb_id, status="error_processing_script")
                raise DocumentProcessingException(f"Processing failed for KB '{kb_id}'. Check server logs for chatbot script errors.")

            # If processing was successful, FixedEnhancedRAGChatbot updated its own metadata 
            # (doc_count, chunk_count, etc., but NOT status).
            # Now, KBService updates the status to "ready".
            self.kb_manager.update_metadata(kb_id, status="ready", retriever_type=process_request.retriever_type)
            
            # Invalidate cached chatbot instance if it exists, as KB has been reprocessed
            if kb_id in self.loaded_chatbots:
                del self.loaded_chatbots[kb_id] 
                logger.info(f"Invalidated cached chatbot for KB '{kb_id}' after reprocessing.")
            
            # Fetch the final KB info which should now reflect status="ready"
            final_kb_info = self.get_kb(kb_id) 
            if not final_kb_info or final_kb_info.status != "ready":
                logger.error(f"KB '{kb_id}' processed, but final status is '{final_kb_info.status if final_kb_info else 'None'}' instead of 'ready'. Metadata sync issue?")
                # This is a critical state - processing seemed to finish, but status isn't right.
                # Avoid setting another error status that might mask the "ready" if it just didn't propagate to get_kb fast enough.
                # Rely on the logged error for diagnosis. If final_kb_info is None, it means get_kb failed entirely.
                if not final_kb_info:
                     raise DocumentProcessingException(f"KB '{kb_id}' processed but failed to retrieve its metadata subsequently.")
                 # If status is not ready, it's still an issue
                raise DocumentProcessingException(f"KB '{kb_id}' processed but status is '{final_kb_info.status}', not 'ready'.")


            logger.info(f"Successfully processed KB '{kb_id}'. Status: {final_kb_info.status}")
            return final_kb_info

        except KnowledgeBaseNotFoundException: 
             raise
        except DocumentProcessingException as e: 
            logger.error(f"DocumentProcessingException for KB '{kb_id}': {e.message}", exc_info=True)
            # Ensure status reflects an error if not already set to a specific error by the block above
            try:
                current_meta = self.kb_manager.list_knowledge_bases()
                kb_m = next((k for k in current_meta if k.get("name") == kb_id), None)
                if kb_m and kb_m.get("status") not in ["error_processing_script", "error_config_missing_api_key"]:
                    self.kb_manager.update_metadata(kb_id, status="error_processing_service")
            except Exception as e_meta_update:
                logger.error(f"Failed to update KB '{kb_id}' status to error_processing_service: {e_meta_update}")
            raise
        except Exception as e:
            logger.error(f"Generic error processing KB '{kb_id}': {e}", exc_info=True)
            try:
                self.kb_manager.update_metadata(kb_id, status="error_processing_generic")
            except Exception as e_meta_update:
                 logger.error(f"Failed to update KB '{kb_id}' status to error_processing_generic: {e_meta_update}")
            raise DocumentProcessingException(f"Could not process KB '{kb_id}'. Error: {str(e)}")

    def get_chatbot_instance(self, kb_id: str) -> FixedEnhancedRAGChatbot:
        """Loads or retrieves a cached chatbot instance for a given KB."""
        if kb_id not in self.loaded_chatbots:
            logger.info(f"Attempting to load chatbot instance for KB '{kb_id}'...")
            kb_info = self.get_kb(kb_id) # This now uses the simplified heuristic if status is missing
            if not kb_info:
                logger.warning(f"get_chatbot_instance: KBInfo for '{kb_id}' not found by self.get_kb.")
                raise KnowledgeBaseNotFoundException(kb_id=kb_id)
            
            logger.info(f"get_chatbot_instance: KB '{kb_id}' status is '{kb_info.status}'.")
            if kb_info.status != "ready":
                 logger.warning(f"Cannot load chatbot for KB '{kb_id}': status is '{kb_info.status}', not 'ready'.")
                 # Provide a more specific message if it needs processing vs. an error state
                 if kb_info.status in ["new", "needs_processing", "processing"]:
                     msg = f"KB '{kb_id}' is currently '{kb_info.status}'. It needs to be processed successfully before chatting."
                 elif "error" in kb_info.status:
                     msg = f"KB '{kb_id}' is in an error state: '{kb_info.status}'. Cannot load chatbot."
                 else: # unknown, metadata_status_missing etc.
                     msg = f"KB '{kb_id}' is not in a 'ready' state (current: '{kb_info.status}'). Ensure it has been processed."
                 raise QueryProcessingException( # Changed to QueryProcessingException as this is a chat-time issue
                    message=msg, 
                    details={"kb_id": kb_id, "current_status": kb_info.status}
                )

            # Pass the KBService's knowledge base manager path to the chatbot instance
            chatbot = FixedEnhancedRAGChatbot(base_kb_manager_directory=self.kb_manager.base_directory)
            
            if not os.getenv("OPENAI_API_KEY"):
                 # This check is also in process_kb, but good to have here too for direct load attempts
                 raise QueryProcessingException("OPENAI_API_KEY not set, cannot initialize chatbot for querying.")
            
            logger.info(f"Calling chatbot.load_existing_enhanced_kb for KB: {kb_id} (KBM base: {chatbot.kb_manager.base_directory})")
            success = chatbot.load_existing_enhanced_kb(kb_name=kb_id) # This method in chatbot script loads the QA chain
            
            if not success:
                logger.error(f"Failed to load existing enhanced KB for '{kb_id}' via chatbot.load_existing_enhanced_kb. It might not be processed, path issue, or internal chatbot script error.")
                # This indicates a problem with loading a supposedly "ready" KB.
                # Could be that vector store is missing, or some other inconsistency.
                self.kb_manager.update_metadata(kb_id, status="error_loading_chatbot") # Mark it as having a loading error
                raise QueryProcessingException(
                    message=f"KB '{kb_id}' is marked 'ready' but failed to load into the chatbot. Check logs.", 
                    details={"kb_id": kb_id, "current_status": "ready_load_failed"}
                )
            self.loaded_chatbots[kb_id] = chatbot
            logger.info(f"Successfully loaded and cached chatbot for KB '{kb_id}'.")
        else:
            logger.debug(f"Returning cached chatbot instance for KB '{kb_id}'.")
        
        return self.loaded_chatbots[kb_id]

    def get_kb_status_heuristic_simplified(self, kb_id: str, kb_meta: Optional[Dict] = None) -> str:
        """Simplified heuristic if status is genuinely missing from metadata."""
        # This heuristic is ONLY called if kb_meta.get('status') was None or empty.
        # It should NOT be the primary source for "ready" status. "ready" MUST come from explicit metadata.
        
        if kb_id in self.loaded_chatbots and getattr(self.loaded_chatbots[kb_id], 'qa_chain', None) is not None:
            # This implies it was successfully loaded at some point, so it *should* be "ready".
            # However, metadata should ideally reflect this. If metadata is missing status, log a warning.
            logger.warning(f"Heuristic: KB '{kb_id}' is loaded in cache but metadata is missing 'status'. Assuming 'ready'.")
            return "ready" 
        
        if kb_meta:
            # If metadata exists but status field is missing
            doc_count = kb_meta.get('document_count', 0)
            chunk_count = kb_meta.get('chunk_count', 0)

            if chunk_count > 0 and doc_count > 0:
                # This was "processed_needs_load" before. Now, if status is missing, it means processing
                # *should* have set it. If it didn't, it's an anomaly.
                logger.warning(f"Heuristic: KB '{kb_id}' has chunks/docs but 'status' is missing in metadata. Defaulting to 'unknown_needs_verify'.")
                return "unknown_needs_verify" # Indicates data is there, but status wasn't properly set
            elif doc_count > 0 and chunk_count == 0:
                logger.warning(f"Heuristic: KB '{kb_id}' has docs but no chunks and 'status' is missing. Defaulting to 'needs_processing'.")
                return "needs_processing" 
            elif doc_count == 0:
                 logger.warning(f"Heuristic: KB '{kb_id}' has no docs and 'status' is missing. Defaulting to 'new_meta_incomplete'.")
                 return "new_meta_incomplete" # Like 'new', but status was missing.

        # Fallback if no metadata or clues
        logger.warning(f"Heuristic: KB '{kb_id}' has no status in metadata and insufficient info for heuristic. Defaulting to 'unknown'.")
        return "unknown"

    def list_documents(self, kb_id: str) -> List[DocumentInfo]:
        """Lists all documents in the specified knowledge base."""
        try:
            kb_doc_path_str = self.kb_manager.get_documents_path(kb_id)
            kb_doc_path = Path(kb_doc_path_str)
            if not kb_doc_path.exists() or not kb_doc_path.is_dir():
                raise KnowledgeBaseNotFoundException(kb_id=kb_id, details={"message": "Document directory not found."})

            documents = []
            for item in kb_doc_path.iterdir():
                if item.is_file(): # Add more checks here if needed (e.g., file extensions)
                    try:
                        stat_info = item.stat()
                        documents.append(DocumentInfo(
                            id=item.name,
                            filename=item.name,
                            size=stat_info.st_size,
                            # content_type would require mimetypes or similar, skip for now for listing
                            kb_id=kb_id,
                            # last_modified=datetime.fromtimestamp(stat_info.st_mtime).isoformat() # Optional
                        ))
                    except Exception as e_stat:
                        logger.warning(f"Could not stat file {item.name} in KB {kb_id}: {e_stat}")
            return documents
        except ValueError: # From get_documents_path if KB itself not found
            raise KnowledgeBaseNotFoundException(kb_id=kb_id)
        except Exception as e:
            logger.error(f"Error listing documents for KB '{kb_id}': {e}", exc_info=True)
            raise DocumentProcessingException(f"Could not list documents for KB '{kb_id}'.")

    def get_document_details(self, kb_id: str, document_id: str) -> Optional[DocumentInfo]:
        """Retrieves details for a specific document in a knowledge base."""
        try:
            kb_doc_path_str = self.kb_manager.get_documents_path(kb_id)
            doc_path = Path(kb_doc_path_str) / document_id
            
            if not doc_path.exists() or not doc_path.is_file():
                return None

            stat_info = doc_path.stat()
            return DocumentInfo(
                id=document_id,
                filename=document_id,
                size=stat_info.st_size,
                kb_id=kb_id
            )
        except ValueError: # From get_documents_path if KB not found
             return None # Or raise specific exception
        except Exception as e:
            logger.error(f"Error getting document details for '{document_id}' in KB '{kb_id}': {e}", exc_info=True)
            return None # Or raise

    async def delete_document(self, kb_id: str, document_id: str) -> bool:
        """Deletes a specific document from a knowledge base."""
        try:
            kb_doc_path_str = self.kb_manager.get_documents_path(kb_id)
            doc_path = Path(kb_doc_path_str) / document_id

            if not doc_path.exists() or not doc_path.is_file():
                logger.warning(f"Document '{document_id}' not found in KB '{kb_id}' for deletion.")
                return False # Or raise custom DocumentNotFoundException

            doc_path.unlink() # Delete the file
            logger.info(f"Successfully deleted document '{document_id}' from KB '{kb_id}'.")

            # Update KB metadata (doc count, status to needs_reprocessing)
            docs_in_kb = [f for f in Path(kb_doc_path_str).iterdir() if f.is_file()]
            self.kb_manager.update_metadata(kb_id, document_count=len(docs_in_kb), status="needs_processing")
            
            # If this KB was loaded, invalidate its cache as its content changed
            if kb_id in self.loaded_chatbots:
                del self.loaded_chatbots[kb_id]
                logger.info(f"Invalidated cached chatbot for KB '{kb_id}' after document deletion.")

            return True
        except ValueError: # From get_documents_path
            raise KnowledgeBaseNotFoundException(kb_id=kb_id)
        except Exception as e:
            logger.error(f"Error deleting document '{document_id}' from KB '{kb_id}': {e}", exc_info=True)
            raise DocumentProcessingException(f"Could not delete document '{document_id}'.")

    def delete_kb(self, kb_id: str) -> bool:
        """Deletes an entire knowledge base."""
        try:
            kb_path_str = self.kb_manager.get_knowledge_base_path(kb_id)
            kb_path = Path(kb_path_str)

            if not kb_path.exists() or not kb_path.is_dir():
                logger.warning(f"Knowledge base directory '{kb_path_str}' for KB '{kb_id}' not found for deletion.")
                return False # Or raise custom KnowledgeBaseNotFoundException

            shutil.rmtree(kb_path) # Deletes the directory and all its contents
            logger.info(f"Successfully deleted knowledge base '{kb_id}' from '{kb_path_str}'.")

            if kb_id in self.loaded_chatbots:
                del self.loaded_chatbots[kb_id]
                logger.info(f"Removed cached chatbot for deleted KB '{kb_id}'.")
            
            return True
        except ValueError: # From get_knowledge_base_path
            logger.warning(f"Knowledge base '{kb_id}' not found by KBM for deletion (ValueError).")
            # This likely means it was already gone or name was incorrect.
            # Consider KBM to return a boolean or specific exception for this case.
            return False # Or raise KnowledgeBaseNotFoundException
        except Exception as e:
            logger.error(f"Error deleting knowledge base '{kb_id}': {e}", exc_info=True)
            raise DocumentProcessingException(f"Could not delete knowledge base '{kb_id}'. Error: {str(e)}") 