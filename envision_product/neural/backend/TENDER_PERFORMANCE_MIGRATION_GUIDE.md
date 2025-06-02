# Tender Performance Model Migration Guide

## Overview

The Tender Performance Model has been significantly updated to support a new data format with expanded geographic features while maintaining backward compatibility with the existing format.

## Data Format Changes

### Legacy Format (Still Supported)
```csv
TENDER_PERF_PERCENTAGE,CARRIER,SOURCE_CITY,DEST_CITY
97,LRGR,REDLANDS,BUCKEYE
```

### New Format (Primary)
```csv
TENDER_PERFORMANCE,CARRIER,SOURCE_CITY,SOURCE_STATE,SOURCE_COUNTRY,DEST_CITY,DEST_STATE,DEST_COUNTRY
95,AFXN,RICHMOND,VA,US,CLEAR BROOK,VA,US
```

## Key Changes

### 1. Enhanced Target Column
- **Legacy**: `TENDER_PERF_PERCENTAGE` (Performance percentage)
- **New**: `TENDER_PERFORMANCE` (Performance percentage - cleaner naming)
- Both formats represent the same metric but with improved column naming

### 2. Expanded Geographic Features
- **Legacy**: City-only (`SOURCE_CITY`, `DEST_CITY`)
- **New**: Full location hierarchy (`SOURCE_CITY`, `SOURCE_STATE`, `SOURCE_COUNTRY`, `DEST_CITY`, `DEST_STATE`, `DEST_COUNTRY`)
- Enables state and country-level analysis and better geographic feature engineering

### 3. Automatic Format Detection
- The model automatically detects whether data is in legacy or new format
- No manual configuration required

## API Changes

### Updated Predict Method

**Legacy Format Usage:**
```python
prediction = model.predict(
    carrier='ODFL',
    source_city='ELWOOD',
    dest_city='REDLANDS'
)
```

**New Format Usage:**
```python
prediction = model.predict(
    carrier='AFXN',
    source_city='RICHMOND',
    source_state='VA',
    source_country='US',
    dest_city='CLEAR BROOK',
    dest_state='VA', 
    dest_country='US'
)
```

### Unified Prediction Interface
The `predict()` method now supports both formats through parameter detection:
- If state/country parameters are provided → uses new format
- If only city parameters are provided → uses legacy format
- Model format detection overrides parameter-based detection

## Model Architecture Changes

### Enhanced Preprocessing Pipeline

**New Format Features:**
- Separate encoders for:
  - Source city, state, country
  - Destination city, state, country
- Comprehensive lane identifiers including full geographic hierarchy

**Legacy Format Features:**
- Maintains original city-only encoding
- Backward compatible with existing models

### Feature Engineering Improvements

1. **Geographic Granularity**: State and country features enable better regional pattern recognition
2. **Enhanced Lane Definitions**: Full geographic lane identifiers improve specificity
3. **Improved Scalability**: More granular features support better scaling to larger datasets

## Migration Steps

### For New Implementations
1. Use the new data format with expanded location fields
2. The model will automatically detect and handle the new format
3. No code changes required beyond providing the new data structure

### For Existing Legacy Data
1. Existing models continue to work without changes
2. Legacy data format is fully supported
3. No migration required for existing implementations

### For Mixed Environments
1. The model can handle both formats simultaneously
2. Format detection is automatic based on column structure
3. Predictions work with both legacy and new format parameters

## Testing

### Validation Script
Run the comprehensive test suite:
```bash
python test_tender_performance_migration.py
```

This validates:
- New format data processing
- Model training and prediction
- Model saving/loading
- Backward compatibility
- Performance metrics

### Example Data Generation
The test script includes utilities to generate sample data in both formats for testing purposes.

## Performance Considerations

### New Format Benefits
- **Better Geographic Insights**: State/country features improve prediction accuracy for regional patterns
- **Enhanced Scalability**: More granular features support better scaling to larger datasets
- **Improved Targeting**: Better identification of specific lanes and regional patterns

### Backward Compatibility
- **Zero Breaking Changes**: Existing legacy implementations continue to work
- **Automatic Detection**: No manual configuration needed
- **Consistent API**: Same prediction interface for both formats

## Model Persistence

### Enhanced Model Saving
- Automatically saves all encoders for both formats
- Preserves data format information
- Maintains backward compatibility with legacy saved models
- Stores feature columns for prediction compatibility

### Model Loading
- Automatically detects saved model format
- Loads appropriate encoders based on training data format
- Handles missing encoders gracefully for legacy models
- Maintains feature column order for predictions

## Best Practices

### For New Projects
1. Use the new format with expanded geographic features
2. Leverage state and country information for regional analysis
3. Take advantage of improved lane identification

### For Existing Projects
1. Continue using legacy format if sufficient for current needs
2. Consider migrating to new format for enhanced capabilities
3. Test thoroughly when switching between formats

### Data Quality
1. Ensure consistent state/country codes in new format
2. Validate location data hierarchy (city-state-country relationships)
3. Maintain data quality standards for both formats

## Troubleshooting

### Common Issues

**Format Detection Problems:**
- Ensure new format data includes all required columns
- Verify column naming matches expected format exactly

**Prediction Errors:**
- Check that prediction parameters match the model's training format
- Verify all required location parameters are provided for new format

**Model Loading Issues:**
- Ensure saved models include all necessary encoder files
- Check that feature information is present in model metadata

### Debug Information
Enable detailed logging to see:
- Data format detection results
- Preprocessing steps and feature counts
- Model architecture and training progress
- Prediction input validation

## API Endpoint Updates

### Enhanced Simplified Format

The simplified prediction format now includes complete location information for the new data format:

**Legacy Simplified Format:**
```json
{
  "carrier": "ODFL",
  "source_city": "ELWOOD", 
  "source_state": null,
  "source_country": null,
  "dest_city": "REDLANDS",
  "dest_state": null,
  "dest_country": null,
  "predicted_performance": 94.17
}
```

**New Simplified Format (Enhanced):**
```json
{
  "carrier": "AFXN",
  "source_city": "RICHMOND",
  "source_state": "VA",
  "source_country": "US", 
  "dest_city": "CLEAR BROOK",
  "dest_state": "VA",
  "dest_country": "US",
  "predicted_performance": 95.2
}
```

### Benefits
- **Complete Geographic Context**: State and country information preserved in simplified mode
- **Consistent Lane Identification**: Full location hierarchy maintained for better integration
- **Uniform Data Structure**: Both legacy and new format predictions include the same fields for consistency
- **Optimal Field Ordering**: Predicted performance always appears as the final column for clarity
- **Backward Compatibility**: Legacy format predictions now include geographic placeholders for easier data processing

### API Compatibility
- All existing API endpoints continue to work
- New format data automatically provides enhanced location context
- Legacy format maintains consistent column structure with null geographic values
- Backward compatibility maintained for all prediction endpoints

## Future Enhancements

### Planned Improvements
1. **Enhanced Geographic Features**: Support for additional location hierarchies
2. **Advanced Feature Engineering**: Automated geographic feature creation
3. **Performance Optimizations**: Further improvements for large-scale datasets
4. **Integration Enhancements**: Better integration with other transport models

### Migration Path
- The current implementation provides a solid foundation for future enhancements
- Backward compatibility will be maintained in future versions
- Additional features will be additive rather than breaking

## Example Usage

### Training with New Format
```python
from models.tender_performance_model import TenderPerformanceModel

# Initialize model with new format data
model = TenderPerformanceModel(data_path="TenderPerformance_v2.csv")

# Train the model (format detected automatically)
model.train(epochs=100)

# Save the model
model.save_model("tender_performance_new_format")
```

### Making Predictions
```python
# Load the model
model = TenderPerformanceModel(model_path="tender_performance_new_format")

# Predict with new format
prediction = model.predict(
    carrier='AFXN',
    source_city='RICHMOND',
    source_state='VA',
    source_country='US',
    dest_city='CLEAR BROOK',
    dest_state='VA',
    dest_country='US'
)

print(f"Predicted Performance: {prediction['predicted_performance']:.2f}%")
```

### Batch Predictions
```python
# Predict multiple lanes at once
results = model.predict_batch(
    carriers=['AFXN', 'RBTW'],
    source_cities=['RICHMOND', 'CHICAGO'],
    dest_cities=['CLEAR BROOK', 'BROWNSTOWN'],
    source_states=['VA', 'IL'],
    source_countries=['US', 'US'],
    dest_states=['VA', 'MI'],
    dest_countries=['US', 'US']
)
```

## Benefits Summary

1. **Enhanced Accuracy**: State and country information improves prediction precision
2. **Better Scalability**: More granular features support larger datasets
3. **Improved Analysis**: Regional patterns and trends more easily identified
4. **Zero Downtime**: Seamless migration with full backward compatibility
5. **Future-Proof**: Architecture supports additional enhancements 

### Enhanced Data Processing Benefits
- **Consistent Column Structure**: Simplifies data processing pipelines across format types
- **Better Integration**: Uniform prediction structure improves system integration
- **Future-Proof Design**: Consistent schema supports easy migration from legacy to new format
- **Analytics Friendly**: Standardized structure enables better reporting and analysis tools 