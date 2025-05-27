# RAG Chatbot FastAPI Architecture - Simple POC

## Overview

This is a **simple, bare-bones API** architecture that mirrors the existing terminal-based RAG chatbot functionality. No complex features, just the essentials for proof of concept.

## Current Functionality Analysis

Based on your terminal chatbot, the core features are:
1. **Create new knowledge base**
2. **Load existing knowledge base** 
3. **Process/reprocess documents** (with different retriever types)
4. **Ask questions** (simple chat)

## Simple API Structure

```
/api/v1/
├── knowledge_bases/     # Basic KB management & document uploads
├── chat/               # Simple chat endpoint + WebSocket
└── health/             # Health check
```

## Endpoints (Keep It Simple)

### Knowledge Base Management
```http
POST   /api/v1/knowledge_bases/           # Create new KB
GET    /api/v1/knowledge_bases/           # List all KBs
GET    /api/v1/knowledge_bases/{kb_id}    # Get KB details
POST   /api/v1/knowledge_bases/{kb_id}/documents # Upload document to KB
POST   /api/v1/knowledge_bases/{kb_id}/process  # Process documents in KB
```

### Chat
```http
POST   /api/v1/knowledge_bases/{kb_id}/chat     # Simple query
WebSocket /api/v1/knowledge_bases/{kb_id}/ws   # Real-time chat
```

### Health
```http
GET    /api/v1/health                          # Health check
```

## Simple Data Models

### Requests
```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi import UploadFile # Though UploadFile is used directly in route, not usually in request models

class CreateKBRequest(BaseModel):
    name: str
    description: Optional[str] = None

class ProcessKBRequest(BaseModel):
    retriever_type: str = "hybrid"  # e.g., standard, hybrid, multi_query, advanced_hybrid

class ChatRequest(BaseModel):
    query: str
```

### Responses
```python
class KBInfo(BaseModel):
    id: str
    name: str
    description: Optional[str]
    document_count: int
    chunk_count: int
    status: str  # e.g., "new", "processing", "ready", "error"

class DocumentInfo(BaseModel):
    id: str # Or filename, or a generated ID for the doc
    filename: str
    content_type: Optional[str]
    size: int # in bytes
    kb_id: str
    message: str = "File uploaded successfully"

class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    sources: List[Dict[str, Any]] # Simplified source info
    processing_time: float
```

## File Structure (Simple)

```
api/
├── main.py                    # FastAPI app
├── models.py                  # Pydantic models (as defined above)
├── services/
│   ├── kb_service.py         # Knowledge base & document operations
│   └── chat_service.py       # Chat operations
├── routes/
│   ├── knowledge_bases.py    # KB & document endpoints
│   └── chat.py              # Chat endpoints + WebSocket
└── core/
    ├── config.py             # Settings
    └── exceptions.py         # Basic error handling
```

## WebSocket Implementation (Simple)

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
# Assume chat_service and kb_service are properly set up and accessible
# from ..services.chat_service import ChatService
# from ..services.kb_service import KBService

router = APIRouter()
# kb_service_instance = KBService() # This would be typically injected
# chat_service_instance = ChatService(kb_service_instance) # Or similar dependency setup

@router.websocket("/knowledge_bases/{kb_id}/ws")
async def websocket_chat(websocket: WebSocket, kb_id: str):
    await websocket.accept()
    
    # Example: Load chatbot instance (simplified)
    # chatbot = kb_service_instance.load_chatbot(kb_id)
    # if not chatbot:
    #     await websocket.send_json({"error": f"Knowledge base {kb_id} not found or not loaded."})
    #     await websocket.close()
    #     return

    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("query", "")
            
            if not query:
                await websocket.send_json({"error": "Query cannot be empty"})
                continue

            # Placeholder for actual chatbot interaction
            # response_data = chatbot.get_enhanced_response(query) # This is from your existing code
            
            # Mocked response for architecture example
            mock_response = {
                "answer": f"Answer to '{query}' from KB {kb_id}",
                "confidence_score": 0.95,
                "sources": [{"source_file": "doc1.pdf", "preview": "..."}],
                "processing_time": 0.5
            }
            
            await websocket.send_json({
                "response": mock_response, # Replace with actual response_data
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for KB {kb_id}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
```

## Integration Strategy

**Reuse your existing classes directly:**
- Use `KnowledgeBaseManager` as-is for KB creation, listing etc.
- Use `FixedEnhancedRAGChatbot` as-is for chat and processing.
- The new `kb_service.py` will wrap these and handle file saving logic.

```python
# services/kb_service.py (Conceptual - details in TODO)
from fastapi import UploadFile
import os # For path operations
import shutil # For saving file
# from ..models import DocumentInfo # If defined in models.py
# from your_project.tools.rag_chatbot.knowledge_base_manager import KnowledgeBaseManager
# from your_project.tools.rag_chatbot.enhanced_main_chatbot import FixedEnhancedRAGChatbot

class KBService:
    def __init__(self):
        # self.kb_manager = KnowledgeBaseManager() # Initialize your existing manager
        # self.chatbots = {}  # kb_id -> chatbot instance
        # self.base_storage_path = "./knowledge_bases" # Should come from config
        pass

    def create_kb(self, name: str, description: str = ""):
        # return self.kb_manager.create_knowledge_base(name, description)
        pass
    
    def list_kbs(self):
        # return self.kb_manager.list_knowledge_bases()
        pass

    async def upload_document_to_kb(self, kb_id: str, file: UploadFile) -> DocumentInfo:
        # kb_doc_path = os.path.join(self.base_storage_path, kb_id, "documents")
        # os.makedirs(kb_doc_path, exist_ok=True)
        # file_location = os.path.join(kb_doc_path, file.filename)
        # with open(file_location, "wb+") as file_object:
        #     shutil.copyfileobj(file.file, file_object)
        # return DocumentInfo(
        #     id=file.filename, # Or generate a unique ID
        #     filename=file.filename,
        #     content_type=file.content_type,
        #     size=file.size, # This might need to be properly calculated after saving
        #     kb_id=kb_id
        # )
        pass

    def load_chatbot(self, kb_id: str):
        # if kb_id not in self.chatbots:
        #     chatbot = FixedEnhancedRAGChatbot()
        #     # Ensure your chatbot loading logic correctly points to the KB path
        #     success = chatbot.load_existing_enhanced_kb(kb_id)
        #     if success:
        #         self.chatbots[kb_id] = chatbot
        # return self.chatbots.get(kb_id)
        pass
```

## Configuration (Minimal)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    storage_path: str = "./knowledge_bases"
    debug: bool = False
    
    class Config:
        env_file = ".env"
```

## Implementation Plan (1 Week)

### Day 1-2: Basic Structure
- FastAPI setup
- Basic endpoints for KB management (including document upload)
- Integrate existing `KnowledgeBaseManager`

### Day 3-4: Chat Integration
- Simple chat endpoint
- WebSocket for real-time chat
- Integrate existing `FixedEnhancedRAGChatbot`

### Day 5: Polish
- Error handling
- Basic frontend for testing (including file upload)
- Documentation

## That's It!

No complex features, no database, no authentication, no sessions, no analytics. Just a simple API wrapper around your existing chatbot code.

The goal is to get a working API in **one week** that does exactly what your terminal version does (plus file upload via API), but over HTTP/WebSocket. 