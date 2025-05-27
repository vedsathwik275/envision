# RAG Chatbot FastAPI Implementation - TODO List

## Overview
Simple FastAPI wrapper around existing RAG chatbot code. Goal: Working API in **1 week** that mirrors terminal functionality.

## Project Structure to Create
```
envision_product/tools/rag_chatbot/api/
├── main.py                           # FastAPI app entry point
├── models.py                         # Pydantic request/response models
├── core/
│   ├── __init__.py
│   ├── config.py                     # Application settings
│   └── exceptions.py                 # Custom exceptions
├── services/
│   ├── __init__.py
│   ├── kb_service.py                 # Knowledge base operations
│   └── chat_service.py               # Chat operations
├── routes/
│   ├── __init__.py
│   ├── knowledge_bases.py            # KB CRUD & document endpoints
│   └── chat.py                       # Chat endpoints + WebSocket
├── static/                           # Simple frontend files
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt                  # Dependencies
├── .env.example                      # Environment variables template
└── README.md                         # API documentation
```

---

## DAY 1: Project Setup & Core Structure

### ✅ Environment Setup
- [x] Create `requirements.txt` with dependencies
- [x] Set up `.env` file with OpenAI API key
- [x] Create all directory structure and `__init__.py` files

### ✅ Core Configuration
- [x] **Create `core/config.py`**
  - [x] Settings class with BaseSettings
  - [x] OpenAI API key configuration
  - [x] Storage path configuration
  - [x] Debug mode setting

- [x] **Create `core/exceptions.py`**
  - [x] Custom exception classes
  - [x] HTTP exception handlers
  - [x] Error response formatting

### ✅ Data Models
- [x] **Create `models.py`**
  - [x] `CreateKBRequest` model
  - [x] `ProcessKBRequest` model  
  - [x] `ChatRequest` model
  - [x] `KBInfo` response model
  - [x] `ChatResponse` response model
  - [x] `DocumentInfo` response model (for file uploads)
  - [x] Basic validation and field constraints

### 📋 Dependencies (`requirements.txt`)
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
python-multipart>=0.0.6  # For file uploads
python-dotenv>=1.0.0
pydantic>=2.5.0
# Existing dependencies from your current system
langchain
langchain-community
chromadb
openai
# Add other dependencies from your current requirements
```

---

## DAY 2: Knowledge Base Service & Routes (including File Upload)

### ✅ Knowledge Base Service
- [x] **Create `services/kb_service.py`**
  - [x] Import existing `KnowledgeBaseManager`
  - [x] Import existing `FixedEnhancedRAGChatbot`
  - [x] `KBService` class with methods:
    - [x] `create_kb(name, description)` → wrap `create_knowledge_base()`
    - [x] `list_kbs()` → wrap `list_knowledge_bases()`
    - [x] `get_kb(kb_id)` → wrap existing metadata loading
    - [x] `upload_document(kb_id, file: UploadFile)` → save file to KB's document folder, return DocumentInfo
    - [x] `process_kb(kb_id, retriever_type)` → wrap processing logic
    - [x] `load_chatbot(kb_id)` → create and cache chatbot instances
  - [x] Add error handling for each method
  - [x] Add logging for operations

### ✅ Knowledge Base Routes
- [x] **Create `routes/knowledge_bases.py`**
  - [x] `POST /knowledge_bases/` → create new KB
  - [x] `GET /knowledge_bases/` → list all KBs
  - [x] `GET /knowledge_bases/{kb_id}` → get KB details
  - [x] `POST /knowledge_bases/{kb_id}/documents` → upload document to KB
  - [x] `POST /knowledge_bases/{kb_id}/process` → process/reprocess documents
  - [x] Add dependency injection for KBService
  - [x] Add proper HTTP status codes
  - [x] Add request/response validation

### ✅ Basic FastAPI App
- [x] **Create `main.py`**
  - [x] FastAPI app initialization
  - [x] Include knowledge base routes
  - [x] Add CORS middleware
  - [x] Add basic error handlers
  - [x] Add health check endpoint (`GET /health`)

### 🧪 Testing Day 2
- [x] Test KB creation via API
- [x] Test KB listing via API
- [x] Test document upload to a KB via API
- [x] Test KB processing via API
- [x] Verify existing terminal functionality still works

---

## DAY 3: Chat Service & HTTP Endpoints

### ✅ Chat Service
- [x] **Create `services/chat_service.py`**
  - [x] `ChatService` class with methods:
    - [x] `get_chatbot(kb_id)` → retrieve loaded chatbot instance from `KBService`
    - [x] `process_query(kb_id, query)` → wrap `get_enhanced_response()`
    - [x] `validate_kb_ready(kb_id)` → check if KB is processed and ready
  - [x] Add response formatting from terminal output to API format
  - [ ] Add timing/performance tracking
  - [x] Add error handling for chat operations

### ✅ Chat HTTP Route
- [x] **Create `routes/chat.py`** (HTTP endpoint only)
  - [x] `POST /knowledge_bases/{kb_id}/chat` → single query endpoint
  - [x] Add request validation
  - [x] Add response formatting
  - [x] Add proper error responses
  - [ ] Add timeout handling for long queries

### ✅ Route Integration
- [x] **Update `main.py`**
  - [x] Include chat routes
  - [x] Add service dependency injection
  - [x] Update error handlers for chat-specific errors

### 🧪 Testing Day 3
- [x] Test chat endpoint with existing KB (that has uploaded & processed docs)
- [x] Test error handling (non-existent KB, empty query, etc.)
- [x] Test response format matches expected schema
- [ ] Performance test with various query lengths

---

## DAY 4: WebSocket Implementation

### ✅ WebSocket Chat Implementation
- [ ] **Update `routes/chat.py`** (add WebSocket)
  - [ ] `WebSocket /knowledge_bases/{kb_id}/ws` → real-time chat
  - [ ] Handle WebSocket connection lifecycle
  - [ ] Handle incoming query messages
  - [ ] Send formatted responses
  - [ ] Add connection error handling
  - [ ] Add graceful disconnection

### ✅ WebSocket Message Protocol
- [x] Define message format for client → server:
  ```json
  {
    "query": "What is the main topic?",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```
- [x] Define message format for server → client:
  ```json
  {
    "answer": "The main topic is...",
    "confidence_score": 0.85,
    "sources": [...],
    "processing_time": 2.5,
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```

### ✅ Enhanced Chat Service for WebSocket
- [x] **Update `services/chat_service.py`**
  - [x] Add async support for WebSocket operations if needed (FastAPI handles sync/async well)
  - [ ] Add connection management (if maintaining state per connection)
  - [ ] Add message validation
  - [ ] Add WebSocket-specific error handling

### 🧪 Testing Day 4
- [x] Test WebSocket connection establishment
- [x] Test sending/receiving messages
- [x] Test error scenarios (invalid KB, connection drops)
- [ ] Test multiple simultaneous connections

---

## DAY 5: Frontend & Polish

### ✅ Simple Frontend
- [ ] **Create `static/index.html`**
  - [ ] Basic HTML structure
  - [ ] Knowledge base management section (create, list, process)
  - [ ] Document upload section (per KB)
  - [ ] Chat interface with WebSocket connection

- [ ] **Create `static/style.css`**
  - [ ] Clean, modern styling
  - [ ] Responsive design
  - [ ] Chat message styling
  - [ ] Loading states

- [ ] **Create `static/app.js`**
  - [ ] WebSocket connection management
  - [ ] KB management functions (create, list, process)
  - [ ] Document upload function
  - [ ] Chat functionality
  - [ ] Error handling and user feedback

### ✅ Static File Serving
- [ ] **Update `main.py`**
  - [ ] Add static file mounting
  - [ ] Add root route to serve frontend
  - [ ] Add proper MIME types

### ✅ API Documentation
- [ ] **Create `README.md`**
  - [ ] API endpoint documentation (including file upload)
  - [ ] Setup instructions
  - [ ] Usage examples
  - [ ] WebSocket protocol documentation

### ✅ Final Polish
- [ ] Add comprehensive logging throughout the application
- [ ] Add input validation and sanitization
- [ ] Add rate limiting (basic)
- [ ] Add proper CORS configuration
- [ ] Add API versioning in routes
- [ ] Clean up any TODO comments in code

### 🧪 Final Testing
- [ ] End-to-end testing with frontend (including file upload)
- [ ] Test all API endpoints with different scenarios
- [ ] Test WebSocket under various conditions
- [ ] Test error handling and edge cases
- [ ] Performance testing with larger knowledge bases

---

## BONUS TASKS (If Time Permits)

### 🎯 Enhanced Features
- [ ] Add progress tracking for document processing (could use WebSockets)
- [ ] Add batch operations for multiple KBs or documents
- [ ] Add simple authentication (API keys)
- [ ] Add request/response logging
- [ ] Add metrics collection (basic)

### 🚀 Deployment Preparation
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Add environment variable validation
- [ ] Add health check improvements
- [ ] Create deployment documentation

### 📊 Monitoring
- [ ] Add basic metrics endpoint
- [ ] Add application logs
- [ ] Add error tracking
- [ ] Add performance monitoring

---

## TESTING CHECKLIST

### Unit Tests
- [ ] Test KB service methods (including document upload)
- [ ] Test chat service methods
- [ ] Test data model validation
- [ ] Test configuration loading

### Integration Tests  
- [ ] Test full KB creation → doc upload → processing → chat flow
- [ ] Test WebSocket connection lifecycle
- [ ] Test error propagation
- [ ] Test concurrent operations

### Manual Testing
- [ ] Test with multiple file types (PDF, DOCX, TXT, CSV)
- [ ] Test with large documents
- [ ] Test with multiple knowledge bases
- [ ] Test various query types and lengths
- [ ] Test WebSocket with multiple clients

---

## DEPENDENCIES & INTEGRATION

### Existing Code Integration Points
- [x] Ensure compatibility with existing `enhanced_dp.py`
- [x] Ensure compatibility with existing `enhanced_vs.py`
- [x] Ensure compatibility with existing `enhanced_rc.py`
- [x] Ensure compatibility with existing `knowledge_base_manager.py`
- [x] Test that terminal version still works alongside API

### Environment Setup
- [x] Verify OpenAI API key configuration
- [x] Verify file system permissions for knowledge base storage
- [ ] Test cross-platform compatibility (Windows/Linux/Mac)

---

## SUCCESS CRITERIA

### ✅ MVP Requirements (Must Have)
- [x] Can create knowledge bases via API
- [x] Can list existing knowledge bases
- [x] Can upload documents to a KB via API
- [x] Can process documents in knowledge bases
- [x] Can query knowledge bases via HTTP
- [x] Can chat in real-time via WebSocket
- [ ] Basic frontend works with all features (including upload)
- [x] Error handling provides meaningful feedback

### 🎯 Quality Requirements (Should Have)
- [ ] API responses are fast (< 2s for typical queries)
- [ ] WebSocket connections are stable
- [ ] Frontend is intuitive and responsive
- [x] Code is well-documented and follows FastAPI best practices (Applied as per rules)
- [x] Comprehensive error handling covers edge cases

### 🚀 Future-Ready (Nice to Have)
- [x] Code structure supports easy feature additions
- [x] API design follows RESTful principles
- [x] WebSocket protocol is extensible
- [x] Configuration supports different deployment environments

---

## ESTIMATED TIME BREAKDOWN

- **Day 1**: 6-8 hours (Setup, config, models)
- **Day 2**: 7-9 hours (KB service with doc upload, routes, basic testing)
- **Day 3**: 4-6 hours (Chat service, HTTP endpoint)
- **Day 4**: 4-6 hours (WebSocket implementation)
- **Day 5**: 5-7 hours (Frontend with upload, documentation, polish)

**Total**: ~26-36 hours over 5 days

---

## NOTES & REMINDERS

### Important Considerations
- **Reuse existing code** - don't rewrite, just wrap
- **Keep it simple** - resist feature creep
- **Test frequently** - verify each component works
- **Document as you go** - don't leave it for the end

### Potential Blockers
- File upload handling with FastAPI (async, large files)
- WebSocket implementation complexity
- Async/sync integration between FastAPI and existing sync code
- Frontend JavaScript WebSocket handling & file upload
- Cross-platform file path issues

### Success Tips
- Start with the simplest possible implementation
- Test each endpoint immediately after creation
- Use existing terminal app for reference behavior
- Keep the scope minimal but functional 