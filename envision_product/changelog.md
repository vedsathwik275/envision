# Changelog

## [Unreleased] - 2025-06-02
### Added
- **Enhanced Tender Performance Model Geographic Information**: Major improvements to tender performance prediction model
  - **Complete Geographic Data Support**: Enhanced model to consistently include `source_state`, `source_country`, `dest_state`, and `dest_country` in all prediction outputs
  - **API Geographic Enhancement**: Updated all tender performance API endpoints to include geographic information in simplified format
    - Modified main predictions endpoint (`/api/predictions/tender-performance/{model_id}`) to include state/country data
    - Enhanced by-lane filtering endpoint to maintain geographic information consistency
    - Updated download functionality to include geographic fields in simplified CSV exports
  - **Consistent Prediction Structure**: Ensured geographic information is always present in predictions regardless of data format
    - Legacy format predictions now include geographic fields with `null` values for consistency
    - New format predictions populate all geographic fields with actual state/country data
    - API responses maintain uniform structure across both legacy and new data formats
  - **Enhanced Model Persistence**: Improved model saving/loading to support full training data predictions
    - Modified `save_model()` to save complete training data (`training_data.csv`) instead of just sample data
    - Updated `load_model()` to prioritize full training data for comprehensive predictions
    - Maintains backward compatibility with existing models through fallback to sample data
  - **Fixed Prediction Count Issues**: Resolved limitation where only 10 predictions were generated instead of full dataset
    - Root cause: Model was loading only sample data (10 rows) instead of complete training data
    - Solution: Enhanced model persistence to save and load full training datasets
    - Result: Predictions now generate for all 400+ lanes in training data

### Changed
- **Simplified Format Enhancement**: Updated simplified prediction format across all components
  - **API Response Structure**: Standardized field order with geographic information positioned between location and performance data
  - **File Converter Updates**: Modified `convert_tender_performance_simplified()` function to use consistent field naming
  - **CSV Export Format**: Enhanced CSV exports to include complete geographic information for better analysis capabilities
- **Improved Model Training Data Management**: Enhanced data handling for better prediction capabilities
  - **Full Dataset Preservation**: Models now preserve complete training datasets for comprehensive prediction generation
  - **Sample Data Backup**: Maintains sample data files for quick reference and legacy compatibility
  - **Metadata Enhancement**: Added comprehensive model metadata including training data shape and feature counts

### Fixed
- **Geographic Information Missing in API Responses**: Resolved issue where simplified API responses were missing state/country fields
  - Fixed hardcoded simplified format in main predictions endpoint
  - Updated by-lane endpoint to include geographic information
  - Corrected download functionality to export complete geographic data
- **Prediction Count Limitation**: Fixed critical issue where only 10 predictions were generated instead of full dataset
  - Problem: `predict_on_training_data()` was using sample data (10 rows) instead of complete training data
  - Solution: Enhanced model saving to preserve full training data and loading to prioritize complete datasets
  - Impact: Users now get predictions for all training data lanes (400+ predictions vs previous 10)
- **Inconsistent Field Naming**: Standardized prediction field names across all components
  - Fixed `convert_tender_performance_simplified()` to use `predicted_performance` instead of `predicted_ontime_performance`
  - Ensured consistent field naming between API responses, CSV exports, and JSON outputs
- **"Using OTHER" Warnings**: Clarified model behavior when destination cities aren't found in training data
  - These warnings are expected behavior when predicting on cities not seen during training
  - Model appropriately falls back to "OTHER" category for unknown destinations
  - No action required - this is proper handling of out-of-vocabulary destinations

## [Unreleased] - 2025-05-30
### Added
- **Enhanced RIQ and Spot API Integration Cards**: Added dedicated API parameter cards for both Rate Inquiry (RIQ) and Spot API workflows
- **Structured Data Parsing**: Implemented robust parsing system that extracts lane information, carrier performance data, order weight, and order volume from chatbot responses
- **Interactive Date Pickers**: Added date selection functionality for shipment planning in both RIQ and Spot API cards
- **Action-Oriented Button Cards**: Introduced "Retrieve Rate Inquiry Details" and "Perform Spot Analysis" button cards for direct API integration
- **Real-time Parameter Display**: Dynamic cards that populate with parsed data from user queries including origin/destination cities, preferred/avoid carriers, equipment types, and service levels
- **Enhanced Prompt Template**: Updated backend prompt to include structured data section with ORDER_WEIGHT and ORDER_VOLUME fields for comprehensive data extraction

### Changed
- **Simplified Card Structure**: Consolidated multiple information sections into single comprehensive parameter cards for better user experience
- **Improved Data Extraction**: Enhanced parsing logic to handle both structured data format and fallback regex patterns for reliable information extraction
- **Streamlined UI**: Removed redundant "Original Query" and "API Integration Status" sections in favor of actionable button interfaces
- **Carrier Labeling**: Updated carrier references to use more intuitive labels ("Preferred Carrier" vs "Avoid Carrier" for RIQ, "Best Performer" vs "Worst Performer" for Spot API)
- **Date Input Optimization**: Modified RIQ to use single date input (today's date default) while Spot API maintains date range functionality

### Fixed
- **Structured Data Visibility**: Resolved issue where structured data section was being displayed to users by implementing proper content filtering in `formatRAGResponse`
- **Parsing Reliability**: Improved fallback parsing mechanisms to ensure consistent data extraction even when structured format is unavailable
- **UI Consistency**: Standardized card layouts and color schemes across both RIQ (blue theme) and Spot API (green/purple theme) sections

## [Unreleased] - 2025-05-29
### Added
- **Neural Network Prediction Integration with RAG Chatbot System**: Complete integration allowing users to upload neural network prediction results to RAG chatbot knowledge bases
  - **"Upload to Knowledge Base" Button**: Added new action button to prediction results page enabling users to upload prediction CSV data to RAG chatbot knowledge bases
  - **Knowledge Base Modal Interface**: Created comprehensive modal system for knowledge base management:
    - **Main Upload Modal**: Central interface with options to create new KB, upload to existing KB, or view KB frontend
    - **Create KB Modal**: Form interface for creating new knowledge bases with name and description fields
    - **Select KB Modal**: Interactive interface for browsing and selecting existing knowledge bases
  - **Automated Knowledge Base Workflow**: Streamlined process for uploading predictions:
    - Automatic conversion of prediction data to simplified CSV format
    - Knowledge base creation with user-provided metadata
    - Document upload to knowledge base via FastAPI backend
    - Automated processing with hybrid retriever configuration
    - Status feedback throughout the entire workflow
  - **Smart Button State Management**: Dynamic button behavior based on upload status:
    - Initial state shows "Upload to Knowledge Base" with database icon
    - After successful upload, button transforms to "Chat" with comments icon and green styling
    - Button remembers uploaded KB ID and opens chat interface directly on subsequent clicks
  - **Modal Management System**: Comprehensive modal handling with:
    - Proper event listener setup and cleanup
    - Status indicators for loading, success, and error states
    - Form validation and error handling
    - Modal backdrop click handling for better UX

### Changed
- **Enhanced User Experience Flow**: Streamlined the workflow from prediction generation to chat interaction
  - **Removed Confirmation Popups**: Eliminated confirmation dialogs that interrupted the user workflow
  - **Automatic Button Transformation**: Upload button automatically becomes a chat button after successful upload
  - **Direct Chat Access**: Users can now access the chat interface directly without additional confirmation steps
- **Improved Knowledge Base Integration**: Enhanced the integration between neural frontend and RAG chatbot system
  - **Simplified CSV Upload**: Predictions are automatically converted to simplified CSV format optimized for RAG processing
  - **Consistent API Integration**: Unified API calls to RAG chatbot backend for seamless data transfer
  - **Enhanced Status Feedback**: Improved user feedback with detailed status messages throughout the upload and processing pipeline

### Fixed
- **Button Event Listener Management**: Resolved issues with upload button event listeners not being properly attached
  - Fixed timing issues with DOM element availability using setTimeout approach
  - Added proper event listener cleanup and reattachment for dynamic button states
  - Ensured consistent button behavior across different prediction result scenarios
- **Knowledge Base Modal State Management**: Fixed modal state persistence and proper cleanup
  - Resolved form reset issues when modals are closed and reopened
  - Fixed status message display and hiding logic
  - Ensured proper modal backdrop click handling
- **Global Variable Initialization**: Fixed initialization issues with `currentUploadedKBId` tracking
  - Added proper variable declaration and initialization
  - Ensured consistent tracking of uploaded knowledge base IDs
  - Fixed button state management based on current upload status

## [Unreleased] - 2025-05-28
### Added
- **Enhanced RAG Chatbot UI with Lane Information Parsing**: Major UI enhancement inspired by rate inquiry interface
  - **Reduced Chat Window Height**: Optimized chat interface to use only 50% of viewport height to make room for information cards
  - **Lane Information Cards**: Added two interactive cards below the chat interface:
    - **Rate Inquiry Details Card**: Displays parsed lane information for rate-related queries with blue color scheme
    - **Spot API Analysis Card**: Shows analysis parameters for performance and spot market queries with green color scheme
  - **Intelligent Prompt Parsing**: Comprehensive natural language processing for transportation queries:
    - **Lane Detection**: Supports multiple formats ("from X to Y", "X-Y", "between X and Y", "Elwood to Miami")
    - **Shipment Details**: Automatically extracts weight (lbs, kg, tons), volume (cuft, cbm), zip codes, and states
    - **Equipment Types**: Recognizes dry van, flatbed, refrigerated, tanker, LTL, FTL, container, and specialized equipment
    - **Service Types**: Identifies expedited, standard, economy, same day, next day, and ground services
    - **Carrier Information**: Advanced carrier name detection with multiple pattern matching
  - **Smart Card Population**: Automatic categorization of queries:
    - Rate inquiry keywords trigger Rate Inquiry card (rate, price, cost, quote, freight, shipping)
    - Spot API keywords trigger Spot API card (performance, analytics, market, capacity, utilization)
    - Ambiguous queries with clear lane info populate both cards
  - **Enhanced Card Design**: Professional layout with:
    - Color-coded status indicators and sections
    - Organized parameter grids for easy scanning
    - Original query preservation for reference
    - Next steps guidance for API integration
    - Visual hierarchy with icons and color-coded backgrounds
  - **Improved UX Features**:
    - Cards automatically clear when chat is cleared
    - Enter key support for message sending
    - Robust error handling for edge cases
    - Default examples and help text when no data is available
  - **Future-Ready Architecture**: Prepared for API integration with parsed parameters ready for:
    - RIQ rate quote API calls with structured lane data
    - Spot market analysis API integration
    - Carrier performance prediction system
- **RIQ Rate Quote Integration**: Complete FastAPI backend integration with Oracle Transportation Management RIQ system
  - New FastAPI application in `tools/data_tool/` with two endpoints:
    - `/rate-quote` - Full rate quote with detailed location and item specifications
    - `/quick-quote` - Simplified rate quote with basic shipment parameters
  - Comprehensive Pydantic models for request/response validation
  - CORS middleware configuration for frontend integration
  - Proper error handling and logging throughout the API
- **RIQ Rate Quote Frontend Page**: New interactive page in the poc_frontend application
  - Toggle between Quick Quote and Full Quote modes
  - Dynamic item management (add/remove items with specifications)
  - Country selection dropdowns for international shipping
  - Advanced options including service provider and request type selection
  - Pre-configured default values (Lancaster, TX to Owasso, OK example)
- **Enhanced Rate Quote Display**: Beautiful, collapsible rate option cards
  - Summary view showing key metrics (cost, transit time, provider, distance)
  - Expandable detailed view with comprehensive cost breakdown
  - Service details including equipment, timing, and itinerary information
  - Shipment specifications display with weight and volume
  - Interactive collapse/expand functionality with smooth animations
- **Updated Navigation**: Added RIQ Rate Quote section to sidebar navigation with calculator icon
- **Comprehensive Documentation**: Added detailed README.md with API usage examples and configuration instructions
- **Enhanced RAG Chatbot Backend Performance**: Major backend optimization for transportation lane queries
  - **Enhanced Prompt Template**: Modified to focus on transportation/logistics documents and always start with best performance metric
  - **Performance Extraction Methods**: Added `extract_performance_metrics()`, `find_best_performance()`, and `enhance_answer_with_performance()` methods
  - **Enhanced Carrier and Lane Extraction**: Improved extraction from CSV content with support for tender performance metrics
  - **Professional Response Formatting**: Implemented Claude-like formatting with clean typography and proper structure
  - **Constraint System**: Added focused constraints to prevent unwanted lane comparisons and hallucination
  - **Enhanced Retriever Implementation**: Created `EnhancedRetriever` class for improved document retrieval:
    - Multiple query format attempts for better CSV matching
    - Support for "source city X and destination city Y" pattern recognition
    - CSV-like format queries (`REDLANDS,SHELBY`)
    - Carrier-specific queries (`ODFL REDLANDS SHELBY`)
    - Performance context queries (`predicted_ontime_performance REDLANDS SHELBY`)
    - Smart deduplication and up to 8 document returns
    - Increased search scope (k=6, fetch_k=20) for more diverse results

### Changed
- **Enhanced API Response Handling**: Improved frontend to parse and display complex RIQ API response structures
- **Improved Cost Display**: Added support for multiple cost types (total, per-unit, weighted costs)
- **Better Date Formatting**: Enhanced date/time display for pickup and delivery schedules
- **Responsive Design**: Ensured all new components work across desktop and mobile devices
- **Code Organization**: Moved global functions outside document ready scope for better accessibility
- **Enhanced Response Formatting**: Fixed duplicate confidence headers and improved markdown parsing in frontend
- **Backend Retrieval Enhancement**: Implemented multiple query format attempts to address vector search limitations for specific lane combinations

### Fixed
- **Collapsible Card Functionality**: Resolved click handler issues by moving functions to global scope and using event listeners
- **API Integration**: Fixed CORS and port configuration for seamless backend-frontend communication
- **Form Validation**: Added proper input validation and error handling for quote requests
- **Button Styling**: Corrected gradient button styling for consistent appearance
- **Duplicate Confidence Headers Issue**: LLM was generating proper format but post-processing added another header - improved detection logic
- **Formatting Problems**: Raw responses showing ugly markdown - implemented professional formatting with clean typography
- **Carrier Information Missing**: Enhanced prompt to always identify carrier associated with highest performance
- **Hallucination and Unwanted Comparisons**: Added focused constraints to prevent mentions of irrelevant lanes

### Issues to Address
- **Critical Retrieval Problem**: Vector search fails to find specific lane data despite CSV containing target information
  - **Symptom**: Query "for the source city redlands and the destination city shelby, give me the details" fails to retrieve `ODFL,REDLANDS,SHELBY,82.8957290649414` from CSV
  - **Root Cause**: Vector search retrieves 9 documents but none contain REDLANDS to SHELBY combination (finds REDLANDS to SALEM, REDLANDS to RICHMOND, but not SHELBY)
  - **Attempted Solution**: Enhanced Retriever with multiple query formats, but still experiencing retrieval failures
  - **Next Steps**: 
    - Consider improving document chunking strategy for CSV data
    - Investigate embedding model performance on transportation data
    - Potentially implement keyword-based search fallback
    - Review CSV document preprocessing and indexing

## [Unreleased] - 2025-05-27
### Added
- **RAG Chatbot API Architecture**: Comprehensive analysis and documentation of existing RAG chatbot codebase
  - Analyzed `EnhancedDocumentProcessor`, `AdvancedVectorStoreManager`, `EnhancedRAGChain`, `KnowledgeBaseManager`, and `FixedEnhancedRAGChatbot` components
  - Created simplified FastAPI architecture document with 7 core endpoints
  - Designed bare-bones API structure mirroring terminal functionality
  - Added file upload endpoint for document management (`POST /knowledge_bases/{kb_id}/documents`)
  - Defined Pydantic data models: `CreateKBRequest`, `ProcessKBRequest`, `ChatRequest`, `KBInfo`, `DocumentInfo`, `ChatResponse`
  - Specified WebSocket protocol for real-time chat functionality
  - Outlined integration strategy to reuse existing codebase without rewriting

- **Added Main Page**: Main page for to redirect to chat or neural
  - HTML and TailwindCSS

- **RAG Chatbot API Implementation Plan**: Detailed 5-day TODO list for FastAPI development
  - Day 1: Project setup, core configuration, and data models (6-8 hours)
  - Day 2: Knowledge base service, routes, and file upload functionality (7-9 hours) 
  - Day 3: Chat service and HTTP endpoints (4-6 hours)
  - Day 4: WebSocket implementation for real-time chat (4-6 hours)
  - Day 5: Frontend, documentation, and polish (5-7 hours)
  - Comprehensive testing checklist and success criteria
  - File structure specification and dependency management
  - Estimated total: 26-36 hours implementation time

- **RAG Chatbot API Backend (FastAPI)**:
  - Implemented initial FastAPI application structure for the RAG chatbot.
  - Created `api/main.py` with FastAPI app initialization, CORS, `/health` endpoint, and Uvicorn runner.
  - Defined core Pydantic models in `api/models.py` for requests and responses (e.g., `CreateKBRequest`, `ChatRequest`, `KBInfo`, `ErrorResponse`).
  - Set up configuration management using `pydantic-settings` in `api/core/config.py`.
  - Implemented custom exception classes and handlers in `api/core/exceptions.py`.
  - Developed `KBService` (`api/services/kb_service.py`) to wrap and manage `KnowledgeBaseManager` and `FixedEnhancedRAGChatbot` operations:
    - Handles creation, listing, and retrieval of knowledge bases.
    - Manages document uploads and processing for KBs.
    - Includes logic for managing and persisting KB status in `metadata.json`.
    - Instantiates `FixedEnhancedRAGChatbot` with appropriate configurations.
  - Developed `ChatService` (`api/services/chat_service.py`) to handle chat interactions:
    - Retrieves chatbot instances from `KBService`.
    - Implements logic for both HTTP and WebSocket chat.
  - Implemented API routes for knowledge base management in `api/routes/knowledge_bases.py`:
    - `POST /knowledge_bases/`: Create a new knowledge base.
    - `GET /knowledge_bases/`: List all knowledge bases.
    - `GET /knowledge_bases/{kb_id}`: Get details of a specific knowledge base.
    - `POST /knowledge_bases/{kb_id}/documents`: Upload documents to a knowledge base.
    - `POST /knowledge_bases/{kb_id}/process`: Process documents in a knowledge base.
  - Implemented API routes for chat functionalities in `api/routes/chat.py`:
    - `POST /knowledge_bases/{kb_id}/chat`: Send a question via HTTP.
    - `WebSocket /knowledge_bases/{kb_id}/ws`: Real-time chat via WebSocket.
  - Implemented application lifespan management in `api/main.py` to create singleton instances of `KBService` and `ChatService`.
  - Added `__init__.py` to `envision_product/chat/backend/api/services/poc_chatbot_scripts/` to make it a package.
  - Updated `requirements.txt` with necessary FastAPI and related dependencies (`fastapi`, `uvicorn`, `websockets`, `python-multipart`, `pydantic`, `python-dotenv`).

- **RAG Chatbot Frontend (Web Interface)**:
  - Created comprehensive web frontend for the RAG chatbot matching Envision Neural design philosophy.
  - Implemented responsive HTML interface using Tailwind CSS with neural frontend color scheme and design patterns.
  - **Design System Integration**:
    - Applied exact gradient background from neural frontend (`linear-gradient(135deg, #1e293b 0%, #334155 100%)`)
    - Used consistent neutral color palette with primary/accent color schemes
    - Implemented collapsible sidebar navigation with expanded/collapsed states
    - Applied proper typography hierarchy with `text-neutral-900` for headings and `text-neutral-600` for descriptions
    - Used `rounded-xl` for cards, `shadow-sm` for subtle shadows, and consistent spacing (`p-6`, `p-8`)
  - **Navigation & Layout**:
    - Fixed header with dynamic title and subtitle based on current section
    - Collapsible sidebar with smooth animations and state management
    - Three main sections: Dashboard, Knowledge Bases, and Chat
    - Proper z-index layering and responsive design
  - **Dashboard Features**:
    - Statistics cards showing knowledge base count, document count, and active chats
    - Quick action buttons for creating knowledge bases, uploading documents, and starting chats
    - Modern card-based layout with proper visual hierarchy
  - **Knowledge Base Management**:
    - List view of all knowledge bases with status indicators
    - Create, upload, and process functionality with modal interfaces
    - Status-based action buttons (upload, process, chat) with proper disabled states
    - Empty state with call-to-action for first-time users
  - **Chat Interface**:
    - Two-panel layout with knowledge base selector and chat interface
    - Real-time status indicators and connection monitoring
    - Message history with user/assistant distinction and timestamps
    - Source citation display for RAG responses
    - HTTP-based chat implementation with loading states
  - **Interactive Components**:
    - Modal dialogs for knowledge base creation and document upload
    - File upload with proper validation (PDF, DOCX, TXT, MD, CSV)
    - Loading overlays with modern spinner animations
    - Toast notifications for user feedback
    - Form validation and error handling
  - **JavaScript Architecture**:
    - Modular event handling and navigation management
    - API integration with comprehensive error handling
    - Sidebar collapse/expand functionality matching neural frontend
    - Dynamic content loading and state management
    - Proper cleanup and modal management

### Changed
- **API Scope**: Moved file upload endpoint from bonus tasks to core Day 2 functionality
- **Architecture Focus**: Simplified from complex production-ready system to minimal POC approach
- **Implementation Strategy**: Emphasized wrapping existing code rather than rewriting components
- **RAG Chatbot Frontend Design Alignment**: Updated frontend to match neural frontend design philosophy:
  - Migrated from custom neural color scheme to standard neutral/primary/accent palette
  - Updated gradient background to exact neural frontend colors (`#1e293b` to `#334155`)
  - Replaced all `gray-*` classes with `neutral-*` for consistency
  - Applied `primary-*` colors instead of custom `neural-blue` throughout interface
  - Enhanced button styles with `font-medium` and proper focus states
  - Improved modal styling with `shadow-2xl` and better spacing
  - Updated chat interface with enhanced color contrast and status indicators
  - Refined navigation patterns to match neural frontend exactly
- **RAG Chatbot API Architecture**: Shifted from an initial over-engineered plan to a simplified Proof of Concept (POC) API, mirroring the existing terminal chatbot's core functionality.
- **Integration Strategy**: Focused on directly wrapping the user's existing Python scripts (`poc_chatbot_scripts`) within the FastAPI services, minimizing code rewrites.
- **`FixedEnhancedRAGChatbot`**:
  - Modified constructor to accept `base_kb_manager_directory` to ensure consistency with `KBService`.
  - Updated `setup_enhanced_knowledge_base` to correctly derive document counts and types using `EnhancedDocumentProcessor.get_document_files()` and `collections.Counter` instead of a non-existent `get_knowledge_base_info` method.
  - Adjusted to correctly manage the `persist_bm25_if_creating` flag for `AdvancedVectorStoreManager`.
  - Ensured it does not overwrite the "ready" status set by `KBService` after processing.
- **`AdvancedVectorStoreManager`**:
  - Modified `create_hybrid_retriever` to persist the `BM25Retriever` to a pickle file (`bm25_retriever.pkl`) during initial KB setup and load it from this file when an existing KB is loaded. This resolved issues with BM25Retriever creation on subsequent loads.
  - Corrected `create_hybrid_retriever` to remove `fetch_k` from `search_kwargs` for the Chroma vector retriever component of the `EnsembleRetriever` when not using MMR search type, resolving `TypeError: Collection.query() got an unexpected keyword argument 'fetch_k'`.
- **`KBService`**:
  - Refined path handling for `settings.storage_path` to use absolute paths.
  - Ensured `KBService.process_kb` explicitly sets `status="ready"` in `metadata.json` after successful processing.
  - Simplified `get_kb_status_heuristic` to be a fallback, prioritizing explicit status from `metadata.json`.
- **`ChatService`**:
  - Updated to call `get_enhanced_response` on the chatbot instance instead of the old `ask_question` method.
- **Imports in `poc_chatbot_scripts`**: Changed direct imports (e.g., `from knowledge_base_manager import ...`) to relative imports (e.g., `from .knowledge_base_manager import ...`) to ensure they work correctly as part of a package.
- **API Configuration**: User updated API port to `8004` in `.env` (reflected in `api/core/config.py`).
- **Frontend File Upload Support**: Added CSV format to supported file types for document upload:
  - Updated file input `accept` attribute to include `.csv` extension
  - Added CSV to supported formats help text in upload modal
  - Enhanced RAG system to handle CSV files for knowledge base processing
- **Frontend Layout Optimizations**:
  - Adjusted chat interface height from `calc(100vh - 12rem)` to `calc(100vh - 16rem)` for better page fit
  - Improved responsive design and proper content scaling

### Fixed
- **FastAPI Application Startup & Runtime Errors**:
  - Fixed issue with missing training data during prediction by adding sample data generation.
  - Added error handling for file paths, invalid lane IDs, and date parsing in prediction workflow.
  - Fixed file upload API to generate file IDs internally.
  - Corrected data preview functionality to handle the proper data processor interface.
  - Added fallback prediction generation when no valid predictions can be made.

## [Unreleased] - 2025-05-24
### Added
- Persistent collapsible sidebar navigation with two states:
  - Expanded state (w-64): Shows full branding, navigation text, and footer
  - Collapsed state (w-16): Shows only icons and expand button
- Smooth sidebar animations and transitions (300ms duration)
- Dedicated toggle buttons for expand/collapse functionality
- Icon-only navigation with tooltips when sidebar is collapsed
- Responsive layout that adjusts main content and header margins based on sidebar state

- Added proof of concept preliminary RAG Chatbot tool
- Enhanced the proof of concept rag chatbot tool with hybrid semantic + keyword matching

### Changed
- **BREAKING**: Completely redesigned navigation from top horizontal tabs to persistent sidebar
- Moved header to top-left corner with compact design
- Relocated footer content to sidebar bottom area
- Updated color scheme implementation to use pure Tailwind CSS classes
- Improved navigation active states with better visual feedback
- Enhanced sidebar spacing and icon alignment for better UX

### Fixed
- Navigation tabs not working due to CSS class conflicts between custom styles and Tailwind
- Sidebar header button positioning - expand button now properly appears in header area when collapsed
- Logo centering issues in collapsed sidebar state
- Footer positioning problems across different pages
- Removed brain logo from collapsed state as requested (only expand button visible)

### Removed
- Custom CSS navigation styles in favor of Tailwind implementation
- Color scheme demo component and modal
- Page-level footers (consolidated into sidebar)
- Complex footer positioning logic (simplified with sidebar integration)

## [Unreleased] - 2025-05-22
### Added
- **Neural Vision POC Frontend - Gmail to S3 Integration (Phase 1, 2, 3, 4 & 6)**:
  - Integrated Gmail to S3 API into the existing Neural Vision POC frontend:
    - Added "Fetch Attachment from Email" button to the file upload section
    - Created email attachment modal for email selection and attachment viewing
    - Implemented Gmail authentication status checking functionality
    - Added Gmail logout functionality
  - Created comprehensive file structure for Gmail integration:
    - Added `gmail_login.html` for handling Gmail OAuth authentication flow
    - Created `gmails3_todo.md` tracking document for implementation progress
  - **Authentication Flow Implementation (Phase 1)**:
    - Added `checkGmailAuthStatus()` function to verify user's Gmail authentication
    - Implemented OAuth flow that opens authentication in a new tab
    - Added status indicators for authentication state
    - Created proper error handling for authentication failures
  - **Modal UI Implementation (Phase 2)**:
    - Added email attachment modal with sections for emails list and attachments
    - Implemented modal management functions (`resetEmailModal()`, `openEmailSelectionModal()`)
    - Created UI utility functions for displaying status messages in the modal
    - Added event listeners for modal interaction (open, close, cancel)
  - **Email & Attachment Listing Implementation (Phase 3)**:
    - Implemented `listGmailEmails()` function to fetch and display emails from the API
    - Added `displayEmailsList()` function to render emails with subject, date, sender, and attachment count
    - Implemented `selectEmail()` function to handle email selection and fetch attachments
    - Added `displayAttachmentsList()` function to render attachments with filename, size, and MIME type
    - Implemented `selectAttachment()` function to handle attachment selection
    - Added `formatFileSize()` utility function to display file sizes in human-readable format
    - Implemented highlighting for selected email and attachment items
    - Added comprehensive error handling for API requests and responses
  - **Attachment Download & Upload Implementation (Phase 4)**:
    - Implemented `handleFetchAttachment()` function to process the selected attachment
    - Added functionality to download attachment data as a Blob from the Gmail API
    - Implemented conversion from Blob to File object with proper metadata
    - Integrated with existing file upload logic to send attachments to the Neural backend
    - Added automatic file preview for CSV attachments
    - Implemented UI feedback throughout the download and upload process
    - Added automatic refresh of file list after successful upload
  - **S3 Upload Feature Implementation (Phase 6)**:
    - Added option to upload selected attachments to S3 alongside the Neural backend
    - Implemented "Also upload to S3" checkbox in the email attachment modal
    - Added S3 upload status area to display upload progress and results
    - Enhanced `handleFetchAttachment()` function to check for S3 upload requests
    - Implemented direct integration with the Gmail to S3 API's upload endpoint
    - Added display of S3 upload results including S3 URL when available
    - Created dedicated UI status functions for S3 upload feedback
    - Implemented error handling specific to S3 upload operations
    - Added CSS styling for S3 upload option and status display
    - Updated `resetEmailModal()` function to reset S3 upload status

### Planned

### Changes
- **Frontend API Configuration**:
  - Updated API base URL constants to support both main API and Gmail to S3 API
  - Set Gmail S3 API base URL to `http://localhost:8002` to match backend configuration
- **Enhanced Error Handling**:
  - Added comprehensive error handling for CORS issues in API requests
  - Implemented detailed console logging for debugging authentication flow
  - Added fallback UI states for API failures
- **Improved UI Feedback**:
  - Added loading indicators during API requests
  - Implemented status messages for successful and failed operations
  - Added visual highlighting for selected emails and attachments
  - Enhanced modal status display with separate areas for Neural and S3 upload feedback

### Fixed
- Fixed CORS issue in Gmail authentication status check by removing `credentials: 'include'` option from fetch requests
- Fixed event listener attachment for the "Fetch Attachment from Email" button
- Resolved modal styling conflicts by preserving original modal styles while adding new styles for email attachment modal
- **Fixed Email and Attachment Display Issue**:
  - Updated `listGmailEmails()` function to correctly handle direct array response format from the API
  - Updated `selectEmail()` function to handle both array and object-wrapped response formats
  - Added compatibility code to support both `message_id` and `id` field names in email objects
  - Added compatibility code to support both `attachment_id` and `id` field names in attachment objects
  - Enhanced attachment count display to show "Yes" when `has_target_attachments` is true but no specific count is available
  - Improved error handling for different API response formats
- **Fixed S3 Upload Filename and MIME Type Issue**:
  - Modified the S3 upload request in `handleFetchAttachment()` function to pass expected filename and MIME type as query parameters instead of in the request body
  - Updated request headers to use `Accept: application/json` instead of `Content-Type: application/json`
  - Removed JSON body from the request to match the API's expected format
  - Ensured consistent parameter passing between download and upload endpoints for proper filename and MIME type handling

## [Unreleased] - 2025-05-21
### Added
- **S3 Integration for Email Attachments**:
  - Implemented functionality to upload email attachments directly to an AWS S3 bucket.
  - Added S3 configuration options to `app.config.settings` (utilizing existing `aws_access_key_id`, `aws_secret_access_key`, `s3_bucket_name`, `s3_region`).
  - Created `S3Service` (`app/services/s3_service.py`) with an `upload_to_s3` method:
    - Uses `boto3` to interact with AWS S3.
    - Takes file data, filename (S3 object key), and content type as input.
    - Uploads files to the configured S3 bucket.
    - Returns the S3 object URL and object key.
    - Includes robust error handling for AWS credentials and S3 client operations.
  - Implemented a new API endpoint `POST /api/emails/{message_id}/attachments/{attachment_id}/upload` in `app/routers/emails.py`:
    - Fetches attachment data (filename, MIME type, content) from Gmail using `GmailService`.
    - Uploads the attachment to S3 using the new `S3Service`.
    - Constructs the S3 object key using a pattern like `attachments/{message_id}/{original_filename}`.
    - Returns an `UploadResponse` (from `app/models/schemas.py`) detailing the upload status, S3 location, and metadata (object key, content type, size, original attachment ID, email message ID).
    - Includes comprehensive error handling for the entire process.
  - Enhanced the `POST /api/emails/{message_id}/attachments/{attachment_id}/upload` endpoint to accept optional `expected_filename` and `expected_mime_type` query parameters.
    - These parameters are passed to `GmailService.get_attachment_data` to ensure that the filename and MIME type used for the S3 object key and `ContentType` metadata are as accurate as possible, consistent with the direct attachment download endpoint.
- **Proof of Concept (PoC) Frontend for Gmail S3 Tool**:
  - Created a simple HTML, CSS, and JavaScript frontend in `envision_product/tools/gmail_s3/poc_frontend/`.
  - **Features**:
    - User authentication via Gmail OAuth2 (initiates login flow, handles status).
    - Lists emails with attachments from the backend API.
    - Allows selection of an email to view its attachments.
    - Allows selection of a specific attachment.
    - Provides options to either directly download the selected attachment or upload it to S3.
    - Utilizes `expected_filename` and `expected_mime_type` query parameters when calling backend download/upload endpoints, using metadata obtained from the list attachments call to ensure accuracy.
    - Displays status messages and API responses.
  - **Authentication Flow Update**: Modified the login process to open the Google authorization URL in a new tab (`window.open(..., '_blank')`) for a smoother user experience with fewer popup blocker issues, while keeping the original tab for the PoC UI.

### Changed
- **API Port Configuration**: 
  - Default Uvicorn serving port in `app/main.py` (within `if __name__ == "__main__":`) changed from 8000 to 8002.
  - Gmail OAuth `redirect_uri` in `app/config.py` updated from `http://localhost:8000/auth/callback` to `http://localhost:8002/auth/callback` to match the new default serving port.
  - Clarified in documentation (README) that Uvicorn CLI needs `--port 8002` for command-line execution on the new port.

### Fixed

## [Unreleased] - 2025-05-20
### Added
- **Email Attachment Processing Tool**: Initiated development of a new tool for processing email attachments:
  - Created project directory structure with modular organization
  - Set up FastAPI application with CORS middleware and basic configuration
  - Implemented Pydantic models for API requests and responses
  - Created utility functions for attachment identification and content type detection
  - Added configuration management with environment variables support
  - Created comprehensive documentation including README and setup instructions
  - Added template .env file for credential management
  - Implemented initial project structure with proper Python packaging
- **Enhanced Email Attachment Processing Tool**:
  - Implemented Gmail API integration for retrieving emails with attachments
  - Added authentication service with OAuth2 token management
  - Created API endpoints for listing emails with attachments
  - Added support for filtering emails by subject patterns
  - Implemented configuration for target email subjects via environment variables
  - Added recursive attachment search to find attachments regardless of nesting level
  - Created endpoint for downloading email attachments
  - Added utility functions for identifying target attachments
  - Improved attachment identification to support filenames with or without extensions

### Changed
- **Updated Pydantic Models**:
  - Migrated from Pydantic v1 to v2 configuration format
  - Replaced `Config` class with `model_config` dictionary
  - Updated `allow_population_by_field_name` to `populate_by_name` for v2 compatibility
- **Enhanced Attachment Detection**:
  - Improved attachment identification logic to handle partial matches
  - Made attachment detection case-insensitive for better matching

### Fixed
- **Attachment Handling**:
  - Fixed issue with deeply nested attachments not being found in Gmail messages
  - Implemented recursive search for attachments in complex message structures
  - Added fallback mechanism for attachment retrieval when metadata is not available
  - Fixed case sensitivity issues in target filename matching
  - Enhanced target attachment detection to work with filenames without extensions
  - Resolved issue with `from` field showing as null in email listings
- **Attachment Download Format**:
    - Resolved issue where attachments were downloaded with incorrect or missing file extensions (e.g., receiving ".bin" or ".txt" for CSV files).
    - Enhanced the attachment download API endpoint (`GET /api/emails/{message_id}/attachments/{attachment_id}`) to accept optional `expected_filename` and `expected_mime_type` query parameters. This allows clients (which can obtain correct metadata from the `list_attachments` endpoint) to guide the download process.
    - Updated the backend Gmail service method `get_attachment_data` to:
        - Prioritize client-provided `expected_filename` and `expected_mime_type` if available.
        - Normalize common shorthand MIME type inputs from the client (e.g., "csv" to "text/csv", "json" to "application/json") to ensure accurate processing and correct `Content-Type` headers in the HTTP response.
        - Intelligently derive file extensions from MIME types using an improved `get_extension_from_mime_type` utility, particularly when original filenames from email parts are generic, lack extensions, or have incorrect ones.
    - Improved the `get_extension_from_mime_type` utility in `attachment_utils.py` for more robust MIME type to extension mapping, especially ensuring "text/csv" and its variations correctly yield a ".csv" extension.
    - These changes ensure that downloaded files now consistently have appropriate names and extensions based on the most reliable metadata available (client hints, email part details, or MIME type derivation).

### Issues to Address

## [Unreleased] - 2025-05-19
### Added
- **Proof of Concept Frontend**: Developed a simple web interface to demonstrate backend API capabilities:
  - Created responsive HTML/CSS/JavaScript frontend with modern UI design
  - Implemented file upload functionality with integrated file preview
  - Added model training interface with real-time training status updates
  - Developed model listing and filtering capabilities
  - Created prediction generation workflow with visualization
  - Added model details view with performance metrics
  - Implemented polling mechanism to track model training progress
  - Added file sorting by upload time with most recent files prioritized
  - Created visual indicators for newly trained models
  - Implemented error handling and loading states throughout the interface
  - Added two-step prediction workflow with metadata and actual prediction data
  - Implemented dynamic prediction table generation with proper data formatting
  - Added download links for CSV and JSON format prediction results
  - Created model type selection with filtered model loading
  - Enhanced model dropdowns to show only the three most recent models per type
  - Added robust error handling for DOM manipulation and API response processing
  - Designed comprehensive color scheme with transportation/logistics-themed variables
  - Created color scheme demo panel accessible via footer toggle for developers
  - Added visual hierarchy with color-coded UI elements for better user experience
  - Implemented animated icons and visual feedback elements in the interface

### Changed
- **Streamlined API Surface**: Simplified the API by maintaining only essential routes:
  - Preserved core file upload functionality while removing non-essential file management endpoints
  - Retained data preview capabilities for uploaded CSV files
  - Maintained critical model management routes including listing, retrieval, and training endpoints
  - Kept all prediction generation and retrieval endpoints for order volume, tender performance, and carrier performance
  - Removed redundant and legacy endpoints to improve API maintainability and reduce attack surface
- **Enhanced Focus on Core Prediction Workflows**: Optimized API for primary use cases:
  - Specialized model-specific prediction routes are now the recommended way to interact with the API
  - Improved documentation to highlight the preferred endpoints for each model type
  - Simplified routing structure for more intuitive API navigation
- **Improved Frontend UI**: Enhanced visual design for better user experience:
  - Implemented transportation/logistics-themed color scheme using CSS variables
  - Enhanced navigation with improved visual feedback (light grey for inactive, white for active/hover)
  - Improved header styling with white text for better contrast and readability
  - Added subtle animations for interactive elements to enhance user engagement

### Fixed
- Fixed issue with prediction data display in frontend where DOM elements were being removed unintentionally
- Fixed model selection dropdown to properly display model types and load models based on selection
- Resolved API URL formatting inconsistencies with hyphens vs underscores in endpoint paths
- Fixed frontend data handling for nested API response structures
- Improved error reporting and recovery when API requests fail or return unexpected data
- Corrected model filtering and sorting to ensure consistent display of model options
- Fixed navigation styling to ensure proper color contrast between active and inactive states
- Resolved header text contrast issues for better readability against gradient backgrounds
- Fixed inconsistent styling of navigation elements by explicitly setting colors for all states

## [Unreleased] - 2025-05-16
### Added
- **Carrier Performance Model**: Implemented a neural network model for predicting carrier on-time performance:
  - Created `carrier_performance_model.py` with comprehensive data preprocessing, model training, and evaluation capabilities
  - Implemented one-hot encoding for categorical features (carrier, source city, destination city, quarter)
  - Added high-cardinality handling for destination cities, grouping less frequent cities as 'OTHER'
  - Designed neural network architecture with dense layers, batch normalization, and dropout for regularization
  - Added early stopping and learning rate reduction functionality to prevent overfitting
  - Implemented comprehensive evaluation metrics including MAE, MSE, RMSE, and R²
- **Advanced Prediction Capabilities** for the Carrier Performance Model:
  - Single prediction method for specific carrier-lane combinations
  - Batch prediction for multiple carrier-lane combinations simultaneously
  - Training data prediction with detailed performance metrics
  - JSON and CSV output formats for prediction results
- **Carrier Performance Model Testing**: Created test script `test_carrier_performance_model.py`:
  - Comprehensive testing workflow for model training and evaluation
  - Visualization of training history and model performance
  - Random sampling for prediction validation
  - Detailed logging of performance metrics
- **Enhanced Model Registry**: Updated model package `__init__.py` to include the new `CarrierPerformanceModel`
- **Task Management**: Updated `todo.md` to reflect completed carrier performance analysis and model development tasks
- **Carrier Performance API Endpoints**: Implemented API routes for carrier performance predictions:
  - `POST /api/predictions/carrier-performance` - Create new carrier performance predictions
  - `GET /api/predictions/carrier-performance/{model_id}` - Get all predictions for a model
  - `GET /api/predictions/carrier-performance/{model_id}/by-lane` - Filter predictions by lane and carrier
  - `GET /api/predictions/carrier-performance/{model_id}/download` - Download predictions in CSV or JSON format
- **CSV Conversion Utilities**: Added carrier performance converters:
  - `convert_carrier_performance_training_predictions` - Convert complete prediction data to CSV
  - `convert_carrier_performance_simplified` - Convert simplified prediction data to CSV
- **Model Service Extensions**: Added carrier performance model support in ModelService:
  - `load_carrier_performance_model` - Load saved carrier performance models
  - `train_carrier_performance_model` - Train new carrier performance models
  - `predict_carrier_performance_on_training_data` - Generate predictions using carrier performance models
- **Model API Routes**: Added carrier performance routes to the models API:
  - `POST /api/models/train/carrier-performance` - Train a new carrier performance model
  - `POST /api/models/predict/carrier-performance` - Generate specific predictions for carrier-lane combinations
- **Lane Handling Utility for filtering predictions by lane criteria**: Implemented in `utils/lane_utils.py`
- **Comprehensive API documentation in `docs/api_reference.md`**: Added to document API endpoints and their usage
- **Prediction caching functionality to prevent unnecessary regeneration of predictions**: Implemented in `PredictionService`
- **Multiple Data Loading Fallback Mechanisms** for Carrier Performance Model:
  - Systematic approach to locate and load training data from multiple possible locations
  - Automatic copy of training data to model directory when found in default location
  - Detailed logging of data loading attempts for better debugging

### Changed
- **Improved error handling for Order Volume predictions by lane**: Enhanced in `_filter_order_volume_predictions_advanced` function
- **Enhanced performance of prediction generation with caching mechanism**: Implemented in `PredictionService`
- **Optimized tender performance model prediction workflow**: Updated in `PredictionService`
- **Enhanced Carrier Performance Model Error Handling**: 
  - Added comprehensive error checking in `predict_on_training_data` method
  - Improved data existence verification before prediction generation
  - Added detailed logging throughout the prediction pipeline

### Fixed
- **Fixed model existence check in order volume by lane endpoint**: Resolved in `order_volume_by_lane` function
- **Corrected model checking and error handling in API routes**: Updated validation in carrier performance endpoints
- **Enhanced error resilience in carrier performance model**: Improved in `predict_on_training_data` method
- **Improved training data handling in carrier performance prediction generation**: Added robust data loading in `predict_carrier_performance_on_training_data`
- **Added multiple fallback mechanisms for loading carrier performance training data**: Implemented in `predict_carrier_performance_on_training_data` function
- **Fixed carrier performance model prediction issues**: Resolved by ensuring training data is available before generating predictions
- **Fixed 500 Internal Server Error in carrier performance by lane endpoint**: Corrected parameter passing to `filter_by_lane` function to avoid type error with dictionary values

## [Unreleased] - 2025-05-15
### Added
- Added JSON to CSV conversion for prediction results
- Created utility functions for file format conversions
- Implemented automatic CSV file generation for both order volume and tender performance predictions
- Added API routes for retrieving order volume predictions with filtering capabilities
- Created dedicated endpoints for order volume predictions by lane
- Added CSV download capability for order volume predictions
- Enhanced Order Volume API with format selection options for file downloads
- Added dynamic CSV generation capability for Order Volume predictions
- Implemented fallback to JSON when CSV is unavailable with clear notification headers
- Added support for explicitly requesting JSON format in download endpoints
- Added training data prediction capability for the Tender Performance Model
- Created utility for converting training data predictions to CSV format
- Added API endpoints for generating and downloading training data predictions
- Implemented metrics calculation on training data predictions including MAE and MAPE
- Added comparison of actual vs predicted values in training data predictions
- Created dedicated API routes for Tender Performance predictions using the training data approach
- Added by-lane filtering for Tender Performance predictions
- Implemented enhanced filtering options (source city, destination city, carrier) for Tender Performance predictions
- Added lane-specific metrics calculation for Tender Performance predictions
- Redesigned the POST endpoint for Tender Performance predictions to use the training data approach
- Added simplified CSV format option for tender performance predictions with only essential fields (carrier, source/destination cities, and predicted performance)
- Implemented a new `simplified` parameter (defaults to True) in tender performance API endpoints to control response format
- Added Latest Model Retrieval API endpoint (`GET /api/models/latest`) to get the most recent model of a specific type
- Implemented filtering options for latest model retrieval by creation date, accuracy, and error metrics
- Created test script for the Latest Model Retrieval API endpoint
- Enhanced Model List API endpoint with pagination support, filtering by creation date and performance metrics
- Added new `/models/list` endpoint for backward compatibility with API specifications
- Created comprehensive test script for testing model listing functionality with various filters and pagination
- **Lane Handling Utility** (`utils/lane_utils.py`): Implemented standardized functions for lane identification and matching, including:
  - Normalization of city names for consistent matching
  - Standardized field name handling with multiple variations
  - Lane component extraction and lane ID generation
  - Lane matching and filtering functions
  - Batch standardization of lane-related fields
- **Simplified CSV format** for Tender Performance predictions, excluding actual performance, absolute error, and percent error
- **Simplified parameter** in Tender Performance API endpoints for returning simplified prediction data
- API route for retrieving the latest model by type (`GET /api/models/latest`) with filtering options:
  - Filter by minimum creation date
  - Filter by minimum accuracy
  - Filter by maximum error
- **Lane Handling Utility** (`utils/lane_utils.py`): Comprehensive solution for standardized lane data handling:
  - Robust city name normalization for consistent matching regardless of case or formatting
  - Field name standardization with support for multiple naming conventions (SOURCE CITY, source_city, etc.)
  - Lane component extraction and standardized lane ID generation
  - Advanced filtering functions for lane-based data
  - Batch standardization of lane fields in prediction results
  - Error handling with fallback mechanisms to maintain backward compatibility
- **Enhanced Documentation** for the Lane Handling Utility in `docs/lane_handling_utility.md`
- **Improved Order Volume API**: Enhanced error handling and response format standardization
- **Prediction Caching**: Added optimization to reuse existing tender performance predictions:
  - Check if prediction files already exist before regenerating
  - Only regenerate predictions if necessary
  - Auto-repair missing CSV files if JSON exists
  - Significant performance improvement for repeated API calls

### Changed
- Modified prediction saving to generate both JSON and CSV formats
- Extended PredictionService with advanced filtering for order volume predictions
- Improved error handling and logging in prediction retrieval routes
- Improved CSV conversion to handle missing fields and empty datasets
- Enhanced test suite to gracefully handle both CSV and JSON responses
- Modified file handling to attempt on-demand CSV generation when files are missing
- Added more robust error handling for file conversions
- Changed Tender Performance predictions to use the training data approach as the primary prediction method
- Enhanced file naming for filtered prediction downloads to indicate when filters are applied
- Updated test scripts to match the new API structure and provide better testing coverage
- Improved documentation of API endpoints to clarify their purpose and relationship to industry standards
- Simplified Tender Performance prediction API by removing the need to specify individual lanes and carriers
- Modified Tender Performance API responses to return simplified data by default (without error metrics and actual values)
- Updated model service to generate both complete and simplified CSVs when predictions are created
- Updated test script to support testing both simplified and complete formats
- Enhanced the existing model listing endpoint to support advanced filtering by performance metrics and creation date
- Added standardized pagination structure with metadata for all listing endpoints
- **Enhanced Order Volume By Lane endpoint** with improved error handling:
  - Robust error handling for missing models and prediction files
  - Case-insensitive matching for lane components
  - Improved logging for debugging purposes
  - Structured error responses instead of HTTP exceptions
  - Returns 200 status code with empty results instead of 404 errors
- **Improved lane filtering logic** in `_filter_order_volume_predictions_advanced` function to use the new Lane Handling Utility
- **Updated API documentation** with examples for the new endpoints
- Tender Performance predictions now use a training data approach for more accurate results
- **Updated Order Volume by Lane endpoint**: Significantly improved robustness:
  - Case-insensitive matching for lane components (source city, destination city)
  - Consistent error responses with detailed information
  - Returns 200 status with empty results instead of 404 errors for better API consistency
  - Added fallback path for environments where Lane Handling Utility may not be available
  - Enhanced logging for better debugging and traceability
- **Improved prediction filtering**: Updated `_filter_order_volume_predictions_advanced` function to use the Lane Handling Utility
- **Enhanced API response format**: Standardized response structure for lane predictions
- **Improved Tender Performance API Endpoints**:
  - Updated to check for and use existing predictions when available
  - Better error handling and logging
  - More descriptive API responses

### Fixed
- Fixed issues with missing CSV files in Order Volume API endpoints
- Resolved inconsistency in file format handling between different API routes
- Added fallback mechanisms to ensure proper content delivery regardless of file availability
- Fixed routing issue with Latest Model Retrieval API endpoint by reordering route definitions to ensure `/latest` is recognized as a separate endpoint and not interpreted as a model ID
- Resolved 404 errors when accessing the Latest Model API endpoint by ensuring proper route precedence in FastAPI
- Missing prediction files now return structured error responses instead of failing silently
- Case sensitivity issues in lane matching for Order Volume predictions
- Fixed inconsistent field naming in predictions (SOURCE CITY vs Source City)
- Added fallback mechanisms for Lane Handling Utility to maintain backward compatibility
- Fixed 500 Internal Server Error in Order Volume by Lane endpoint caused by case-sensitive matching and field naming inconsistencies
- Resolved issues with inconsistent field names in predictions (SOURCE CITY vs source_city)
- Fixed error handling in prediction service to return structured error responses instead of failing silently
- Added consistent fallback mechanisms to maintain backward compatibility
- Fixed route path issue in Order Volume by Lane endpoint causing 404 errors due to duplicate `/predictions` prefix
- Fixed model existence check in Order Volume by Lane endpoint that incorrectly compared model ID with model dictionaries
- Eliminated redundant prediction generation when predictions already exist
- Updated API documentation to reflect optimized behavior
- Better error handling for prediction file access issues

## [Unreleased] - 2025-05-14

### Added
- Added feature column information saving and loading to `TenderPerformanceModel` 
- Implemented fallback mechanisms for prediction when model is loaded without training data
- Added enhanced logging throughout the prediction pipeline for better debugging
- Created a dummy X_train initialization process when feature columns are available but sample data is missing

### Changed
- Enhanced `TenderPerformanceModel.predict()` to handle cases where model is loaded without going through training
- Improved `PredictionService.predict_tender_performance()` to use consistent directory structure for saved predictions
- Updated model loading to utilize feature_info.json for initializing necessary preprocessing components
- Enhanced API response validation to ensure all required fields are properly included

### Fixed
- Fixed "NoneType has no attribute columns" error during prediction when model loaded from saved state
- Fixed API validation errors with missing prediction_id in responses
- Resolved inconsistency in prediction file storage between different prediction types
- Fixed issues with prediction retrieval when predictions are saved in the wrong location
- Added missing prediction_id to metadata in prediction responses

## [Unreleased] - 2025-05-12

### Added
- Created `order_volume_model.py`



Timestamp: 2025-06-02 09:12:00