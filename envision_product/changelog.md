# Changelog

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
- Created `order_volume_model.py` to implement the neural network model for predicting order volumes.
- Added data preprocessing, model training, evaluation, and prediction generation functionalities.
- Implemented model saving and loading capabilities.

- Created `test_model.py` to provide a script for testing the model with command-line arguments.
- Added options for training, evaluating, and generating predictions.

- Created `README.md` to document the usage, requirements, and architecture of the model.

- Created `requirements.txt` to list all necessary Python packages for the project.

- Added `best_model.keras` to store the best model weights from training.
- Added `future_predictions.csv` to save generated predictions for future order volumes.
- Added `order_volume_model/` directory to store saved model and preprocessing components.
- Added `prediction_evaluation.png` to visualize the model's prediction performance.

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

---

## [Unreleased] - 2025-05-12 23:15

### Added
- Created API endpoints for model management and predictions in `api/models.py` and `api/predictions.py`.
- Implemented `ModelService` for handling model loading, saving, registration, training, and deletion.
- Added `PredictionService` for managing prediction generation and storage.
- Created file upload and data preview functionalities in `api/files.py` and `api/data.py`.
- Added fallback data generation in prediction to handle cases with missing training data.
- Implemented main API router to connect all endpoint modules.

### Changed
- Enhanced `OrderVolumeModel` with improved error handling throughout prediction pipeline.
- Modified model saving to include raw training data to ensure prediction availability.
- Updated model loading to create sample data when needed for prediction.
- Reduced the number of epochs during testing for faster model training.

### Fixed
- Fixed issue with missing training data during prediction by adding sample data generation.
- Added error handling for file paths, invalid lane IDs, and date parsing in prediction workflow.
- Fixed file upload API to generate file IDs internally.
- Corrected data preview functionality to handle the proper data processor interface.
- Added fallback prediction generation when no valid predictions can be made.

### Removed
- Removed unnecessary dependencies and unused service modules.
- Eliminated the separate `model_manager` and `training_service` in favor of integrated `ModelService`.

---

Timestamp: 2025-05-24 13:37:00