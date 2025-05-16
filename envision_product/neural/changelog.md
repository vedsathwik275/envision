# Changelog

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

Timestamp: 2025-05-15 15:20:00