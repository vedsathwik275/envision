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

- [ ] **API Routes for Tender Performance Predictions**
   - Create route to get predictions by model ID, lane, and carrier
   - Create route to get predictions by model ID and lane (for all carriers)
   - Implement filtering capabilities similar to order volume
   - Add pagination support for large prediction sets (do this at the very end)

## 3. Model Management API Routes

- [ ] **Latest Model Retrieval**
   - Implement route to get the latest model ID by model type
   - Add filtering options by creation date, performance metrics

- [ ] **List All Models**
   - Create route to list all models with optional filtering by type
   - Include relevant metadata (training date, performance metrics)
   - Add pagination support

## 4. Common Utilities

- [x] **File Format Conversion Utility**
   - Create a shared utility for JSON to CSV conversion
   - Ensure consistent handling of nested data structures

- [ ] **Lane Handling Utility**
   - Implement standardized functions for lane identification and matching
   - Create helper functions for lane-based filtering

## 5. Testing and Documentation

- [ ] **Integration Tests**
   - Test all new API routes with sample data
   - Verify CSV generation works correctly

- [ ] **Update API Documentation**
   - Document all new API routes in README.md
   - Add examples of API usage for different scenarios

- [ ] **Update Changelog**
   - Document all implemented changes

## Implementation Details

### File Structure Considerations

The filesystem structure for predictions should be consistent for both model types:
```
data/
  predictions/
    {prediction_id}/
      prediction_data.json
      prediction_data.csv
```

### API Route Structure

1. **Order Volume Predictions**
   - `GET /api/predictions/order-volume/{model_id}`
   - `GET /api/predictions/order-volume/{model_id}?source_city={city}&destination_city={city}&carrier={carrier}`

2. **Tender Performance Predictions**
   - `GET /api/predictions/tender-performance/{model_id}`
   - `GET /api/predictions/tender-performance/{model_id}?source_city={city}&dest_city={city}&carrier={carrier}`
   - `GET /api/predictions/tender-performance/{model_id}/by-lane?source_city={city}&dest_city={city}` (all carriers)

3. **Model Management**
   - `GET /api/models/latest?model_type={type}`
   - `GET /api/models/list?model_type={type}`

### Enhanced Functionality

Both model types will need to:
1. Generate predictions in both JSON and CSV formats
2. Support filtering by various criteria
3. Provide both individual and bulk access to predictions

## Priority Order

1. Implement JSON to CSV conversion for both model types
2. Create API route for latest model retrieval
3. Implement training data prediction for Tender Performance model
4. Create API routes for Tender Performance predictions
5. Create API routes for Order Volume predictions
6. Add filtering and pagination capabilities
7. Implement remaining model management routes
8. Update documentation and testing 