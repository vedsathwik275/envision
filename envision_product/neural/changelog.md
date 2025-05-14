# Changelog

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

Timestamp: 2025-05-14 09:55:00 