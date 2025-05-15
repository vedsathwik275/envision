# Changelog

## [Unreleased] - 2025-05-15

### Added
- Added feature column information saving and loading to `TenderPerformanceModel` 
- Implemented fallback mechanisms for prediction when model is loaded without training data
- Added enhanced logging throughout the prediction pipeline for better debugging
- Created a dummy X_train initialization process when feature columns are available but sample data is missing
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

### Changed
- Enhanced `TenderPerformanceModel.predict()` to handle cases where model is loaded without going through training
- Improved `PredictionService.predict_tender_performance()` to use consistent directory structure for saved predictions
- Updated model loading to utilize feature_info.json for initializing necessary preprocessing components
- Enhanced API response validation to ensure all required fields are properly included
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

### Fixed
- Fixed "NoneType has no attribute columns" error during prediction when model loaded from saved state
- Fixed API validation errors with missing prediction_id in responses
- Resolved inconsistency in prediction file storage between different prediction types
- Fixed issues with prediction retrieval when predictions are saved in the wrong location
- Added missing prediction_id to metadata in prediction responses
- Fixed issues with missing CSV files in Order Volume API endpoints
- Resolved inconsistency in file format handling between different API routes
- Added fallback mechanisms to ensure proper content delivery regardless of file availability

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

Timestamp: 2025-05-14 09:55:00 