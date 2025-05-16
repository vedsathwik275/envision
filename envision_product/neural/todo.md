# Envision Neural API Enhancement To-Do List

## 1. Order Volume Model Enhancements

- [x] **JSON to CSV Conversion**
   - Implement functionality to convert order volume prediction JSON files to CSV format
   - Save both formats when predictions are generated
   - Ensure CSV headers match the expected format

- [x] **API Routes for Order Volume Predictions**
   - Create route to get predictions by model ID, lane, and carrier
   - Create route to get all predictions for a specific model ID
   - Implement filtering capabilities (by source city, destination city, carrier)
   - Add pagination support for large prediction sets (do this at the very end)

## 2. Tender Performance Model Enhancements

- [x] **Training Data Prediction**
   - Implement functionality to predict on the training data itself
   - Create a prediction file with input features and predicted output
   - Save both JSON and CSV versions of the predictions

- [x] **API Routes for Tender Performance Predictions**
   - Create route to get predictions by model ID, lane, and carrier
   - Create route to get predictions by model ID and lane (for all carriers)
   - Implement filtering capabilities similar to order volume
   - Add pagination support for large prediction sets (do this at the very end)

## 3. Model Management API Routes

- [x] **Latest Model Retrieval**
   - Implement route to get the latest model ID by model type
   - Add filtering options by creation date, performance metrics

- [x] **List All Models**
   - Create route to list all models with optional filtering by type
   - Include relevant metadata (training date, performance metrics)
   - Add pagination support

## 4. Common Utilities

- [x] **File Format Conversion Utility**
   - Create a shared utility for JSON to CSV conversion
   - Ensure consistent handling of nested data structures

- [x] **Lane Handling Utility**
   - Implement standardized functions for lane identification and matching
   - Create helper functions for lane-based filtering

## 5. Testing and Documentation

- [ ] **Integration Tests**
   - Test all new API routes with sample data
   - Verify CSV generation works correctly

- [ ] **Update API Documentation**
   - Document all new API routes in README.md
   - Add examples of API usage for different scenarios

- [x] **Update Changelog**
   - Document all implemented changes

## 6. Carrier Performance Data Analysis and Model

- [x] **Data Collection and Analysis**
   - Perform exploratory data analysis to identify key performance indicators and patterns
   - Generate statistical insights and correlations between different performance metrics
   - Create standardized performance score methodology

- [x] **Carrier Performance Model Development**
   - Design a neural network architecture for carrier performance prediction
   - Create `carrier_performance_model.py` with appropriate model classes and methods
   - Implement evaluation metrics specific to carrier performance (reliability score, cost-efficiency)
   - Create model saving/loading functionality that preserves preprocessing components

- [ ] **API Integration**
   - Add carrier performance model type to the model service
   - Create endpoints for carrier performance predictions:
     - `GET /api/predictions/carrier-performance/{model_id}`
     - `GET /api/predictions/carrier-performance/{model_id}/by-lane`
     - `GET /api/predictions/carrier-performance/{model_id}/by-carrier`
     - `GET /api/predictions/carrier-performance/{model_id}/download`
   - Add carrier comparison endpoints to allow ranking and benchmarking
   - Extend existing CSV conversion utilities to support carrier performance data formats

- [ ] **Front-End Visualization**
   - Design dashboards for carrier performance visualization
   - Create components for carrier comparison charts
   - Implement performance trend analysis views
   - Develop carrier scorecard generation functionality

- [ ] **Testing and Validation**
   - Create comprehensive test suite for the carrier performance model
   - Add integration tests for API endpoints
   - Perform cross-validation against historical carrier selections
   - Test compatibility with existing lane handling utilities
   - Validate performance against industry benchmarks
   - Stress test with large carrier datasets

- [ ] **Documentation and Training**
   - Update API documentation to include all carrier performance endpoints
   - Create specific documentation for carrier performance model methodology
   - Add detailed examples of carrier performance API usage
   - Document integration with existing workflows
   - Create user guide for interpreting carrier performance predictions

### Implementation Details

The model should generate both:
- Overall carrier performance scores (0-100)
- Specific performance predictions for lane-carrier combinations
- Comparative rankings between carriers
- Confidence intervals for performance predictions

### API Route Structure

1. **Carrier Performance Predictions**
   - `GET /api/predictions/carrier-performance/{model_id}`
   - `GET /api/predictions/carrier-performance/{model_id}/by-lane?source_city={city}&destination_city={city}`
   - `GET /api/predictions/carrier-performance/{model_id}/by-carrier?carrier={carrier}`
   - `GET /api/predictions/carrier-performance/{model_id}/compare?carriers={carrier1},{carrier2}&lane={lane_id}`

2. **Model Management Extensions**
   - Extend existing model management endpoints to handle carrier performance models
   - Add specialized filtering options for carrier performance models

### Integration with Existing Systems

The carrier performance model should integrate with:
1. Existing Lane Handling Utility
2. Order Volume predictions to provide capacity-aware recommendations
3. Tender Performance predictions to create comprehensive carrier selection strategies