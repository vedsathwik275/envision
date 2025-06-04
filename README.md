# Envision Platform

## Overview
Envision is a comprehensive AI platform featuring neural network models, RAG chatbot capabilities, email processing tools, and web interfaces.

## Architecture

### Frontend Applications
| Service | Directory | Port | Command | Description |
|---------|-----------|------|---------|-------------|
| **Main Landing Page** | `envision_product/main_page/` | 5002 | `npx live-server --port=5002` | Main entry point and navigation |
| **Landing Page** | `envision_product/landing page/` | 5010 | `npm run serve` and `npm run dev` | Marketing/info landing page |
| **Neural Frontend** | `envision_product/neural/poc_frontend/` | 5001 | `npm run serve` and `npm run dev` | ML model training and predictions |
| **RAG Chatbot Frontend** | `envision_product/chat/poc_frontend/` | 5003 | `npx live-server --port=5003` | Document chat interface |

### Backend APIs
| Service | Directory | Port | Command | Description |
|---------|-----------|------|---------|-------------|
| **Neural Backend** | `envision_product/neural/backend/` | 8000 | `uvicorn main:app --reload` | ML model API and data processing |
| **RAG Chatbot Backend** | `envision_product/chat/backend/` | 8004 | `uvicorn api.main:app --reload --port 8004` | Knowledge base and chat API |
| **Gmail S3 Tools** | `envision_product/tools/gmail_s3/` | 8002 | `uvicorn app.main:app --reload --port 8002` | Email attachment processing |
| **Data Tools Backend** | `envision_product/tools/` | 8006 | `uvicorn data_tool.main:app --reload --port 8006` | Data Tools API |

## Quick Start

### Development Environment Setup
1. **Start all backend services:**
   ```bash
   # Terminal 1 - Neural API
   cd envision_product/neural/backend
   uvicorn main:app --reload

   # Terminal 2 - RAG Chatbot API  
   cd envision_product/chat/backend
   uvicorn api.main:app --reload --port 8004

   # Terminal 3 - Gmail S3 API
   cd envision_product/tools/gmail_s3
   uvicorn app.main:app --reload --port 8002
   ```

2. **Start frontend applications:**
   ```bash
   # Terminal 4 - Main Page
   cd envision_product/main_page
   npx live-server --port=5002

   # Terminal 5 - RAG Chatbot Frontend
   cd envision_product/chat/poc_frontend
   npx live-server --port=5003

   # Terminal 6 - Neural Frontend (if using npm)
   cd envision_product/neural/poc_frontend
   npm run serve
   ```

### Access Points
- **Main Platform**: http://localhost:5002
- **RAG Chatbot**: http://localhost:5003
- **Neural ML Platform**: http://localhost:5001
- **API Documentation**:
  - Neural API: http://localhost:8000/docs
  - RAG API: http://localhost:8004/docs
  - Gmail S3 API: http://localhost:8002/docs

## Component Details

### 🧠 Neural Platform
Machine learning model training and prediction platform for transportation logistics.
- **Frontend**: React/Vue application with model management interface
- **Backend**: FastAPI with ML model training, prediction, and data processing
- **Features**: CSV upload, model training, batch predictions, performance metrics

### 💬 RAG Chatbot
Retrieval-Augmented Generation chatbot for document-based Q&A.
- **Frontend**: Modern web interface with knowledge base management
- **Backend**: FastAPI with vector storage, document processing, and chat API
- **Features**: Knowledge base creation, document upload, hybrid retrieval, real-time chat

### 📧 Gmail S3 Tools
Email attachment processing and cloud storage integration.
- **Backend**: FastAPI with Gmail API integration and S3 upload capabilities
- **Features**: OAuth authentication, attachment extraction, cloud storage

### 🏠 Main Page
Central navigation hub for accessing all platform components.
- **Frontend**: Static HTML with navigation to all services
- **Purpose**: Single entry point for the entire Envision ecosystem

## Development Notes
- All backend services use FastAPI with automatic API documentation
- Frontend applications use modern web technologies (HTML5, TailwindCSS V4, JavaScript)
- Services are designed to run independently with clear API boundaries
- Port assignments prevent conflicts during concurrent development