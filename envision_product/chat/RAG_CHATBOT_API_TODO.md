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
- [ ] Create `requirements.txt` with dependencies
- [ ] Set up `.env` file with OpenAI API key
- [ ] Create all directory structure and `__init__.py` files

### ✅ Core Configuration
- [ ] **Create `core/config.py`**
  - [ ] Settings class with BaseSettings
  - [ ] OpenAI API key configuration
  - [ ] Storage path configuration
  - [ ] Debug mode setting

- [ ] **Create `core/exceptions.py`**
  - [ ] Custom exception classes
  - [ ] HTTP exception handlers
  - [ ] Error response formatting

### ✅ Data Models
- [ ] **Create `models.py`**
  - [ ] `CreateKBRequest` model
  - [ ] `ProcessKBRequest` model  
  - [ ] `ChatRequest` model
  - [ ] `KBInfo` response model
  - [ ] `ChatResponse` response model
  - [ ] `DocumentInfo` response model (for file uploads)
  - [ ] Basic validation and field constraints

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
- [ ] **Create `services/kb_service.py`**
  - [ ] Import existing `KnowledgeBaseManager`
  - [ ] Import existing `FixedEnhancedRAGChatbot`
  - [ ] `KBService` class with methods:
    - [ ] `create_kb(name, description)` → wrap `create_knowledge_base()`
    - [ ] `list_kbs()` → wrap `list_knowledge_bases()`
    - [ ] `get_kb(kb_id)` → wrap existing metadata loading
    - [ ] `upload_document(kb_id, file: UploadFile)` → save file to KB's document folder, return DocumentInfo
    - [ ] `process_kb(kb_id, retriever_type)` → wrap processing logic
    - [ ] `load_chatbot(kb_id)` → create and cache chatbot instances
  - [ ] Add error handling for each method
  - [ ] Add logging for operations

### ✅ Knowledge Base Routes
- [ ] **Create `routes/knowledge_bases.py`**
  - [ ] `POST /knowledge_bases/` → create new KB
  - [ ] `GET /knowledge_bases/` → list all KBs
  - [ ] `GET /knowledge_bases/{kb_id}` → get KB details
  - [ ] `POST /knowledge_bases/{kb_id}/documents` → upload document to KB
  - [ ] `POST /knowledge_bases/{kb_id}/process` → process/reprocess documents
  - [ ] Add dependency injection for KBService
  - [ ] Add proper HTTP status codes
  - [ ] Add request/response validation

### ✅ Basic FastAPI App
- [ ] **Create `main.py`**
  - [ ] FastAPI app initialization
  - [ ] Include knowledge base routes
  - [ ] Add CORS middleware
  - [ ] Add basic error handlers
  - [ ] Add health check endpoint (`GET /health`)

### 🧪 Testing Day 2
- [ ] Test KB creation via API
- [ ] Test KB listing via API
- [ ] Test document upload to a KB via API
- [ ] Test KB processing via API
- [ ] Verify existing terminal functionality still works

---

## DAY 3: Chat Service & HTTP Endpoints

### ✅ Chat Service
- [ ] **Create `services/chat_service.py`**
  - [ ] `ChatService` class with methods:
    - [ ] `get_chatbot(kb_id)` → retrieve loaded chatbot instance from `KBService`
    - [ ] `process_query(kb_id, query)` → wrap `get_enhanced_response()`
    - [ ] `validate_kb_ready(kb_id)` → check if KB is processed and ready
  - [ ] Add response formatting from terminal output to API format
  - [ ] Add timing/performance tracking
  - [ ] Add error handling for chat operations

### ✅ Chat HTTP Route
- [ ] **Create `routes/chat.py`** (HTTP endpoint only)
  - [ ] `POST /knowledge_bases/{kb_id}/chat` → single query endpoint
  - [ ] Add request validation
  - [ ] Add response formatting
  - [ ] Add proper error responses
  - [ ] Add timeout handling for long queries

### ✅ Route Integration
- [ ] **Update `main.py`**
  - [ ] Include chat routes
  - [ ] Add service dependency injection
  - [ ] Update error handlers for chat-specific errors

### 🧪 Testing Day 3
- [ ] Test chat endpoint with existing KB (that has uploaded & processed docs)
- [ ] Test error handling (non-existent KB, empty query, etc.)
- [ ] Test response format matches expected schema
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
- [ ] Define message format for client → server:
  ```json
  {
    "query": "What is the main topic?",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```
- [ ] Define message format for server → client:
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
- [ ] **Update `services/chat_service.py`**
  - [ ] Add async support for WebSocket operations if needed (FastAPI handles sync/async well)
  - [ ] Add connection management (if maintaining state per connection)
  - [ ] Add message validation
  - [ ] Add WebSocket-specific error handling

### 🧪 Testing Day 4
- [ ] Test WebSocket connection establishment
- [ ] Test sending/receiving messages
- [ ] Test error scenarios (invalid KB, connection drops)
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
- [ ] Ensure compatibility with existing `enhanced_dp.py`
- [ ] Ensure compatibility with existing `enhanced_vs.py`
- [ ] Ensure compatibility with existing `enhanced_rc.py`
- [ ] Ensure compatibility with existing `knowledge_base_manager.py`
- [ ] Test that terminal version still works alongside API

### Environment Setup
- [ ] Verify OpenAI API key configuration
- [ ] Verify file system permissions for knowledge base storage
- [ ] Test cross-platform compatibility (Windows/Linux/Mac)

---

## SUCCESS CRITERIA

### ✅ MVP Requirements (Must Have)
- [ ] Can create knowledge bases via API
- [ ] Can list existing knowledge bases
- [ ] Can upload documents to a KB via API
- [ ] Can process documents in knowledge bases
- [ ] Can query knowledge bases via HTTP
- [ ] Can chat in real-time via WebSocket
- [ ] Basic frontend works with all features (including upload)
- [ ] Error handling provides meaningful feedback

### 🎯 Quality Requirements (Should Have)
- [ ] API responses are fast (< 2s for typical queries)
- [ ] WebSocket connections are stable
- [ ] Frontend is intuitive and responsive
- [ ] Code is well-documented and follows FastAPI best practices
- [ ] Comprehensive error handling covers edge cases

### 🚀 Future-Ready (Nice to Have)
- [ ] Code structure supports easy feature additions
- [ ] API design follows RESTful principles
- [ ] WebSocket protocol is extensible
- [ ] Configuration supports different deployment environments

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