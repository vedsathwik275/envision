# Carrier Performance Model Migration Guide

## Overview

The Carrier Performance Model has been significantly updated to support a new data format with expanded features while maintaining backward compatibility with the existing format.

## Data Format Changes

### Legacy Format (Still Supported)
```csv
QTR,CARRIER,SOURCE_CITY,DEST_CITY,ORDER_COUNT,AVG_TRANSIT_DAYS,ACTUAL_TRANSIT_DAYS,ONTIME_PERFORMANCE
2025 2,HOSD,GRAND RAPIDS,ELWOOD,114,4,2,61
```

### New Format (Primary)
```csv
TRACKING_MONTH,CARRIER,SOURCE_CITY,SOURCE_STATE,SOURCE_COUNTRY,DEST_CITY,DEST_STATE,DEST_COUNTRY,ORDER_COUNT,AVG_TRANSIT_DAYS,ACTUAL_TRANSIT_DAYS,ONTIME_PERFORMANCE
2025 05,ODFL,RICHMOND,VA,US,WINDSOR,CT,US,73,2,4,16
```

## Key Changes

### 1. Enhanced Time Dimension
- **Legacy**: `QTR` (Quarter format: "2025 2")
- **New**: `TRACKING_MONTH` (Month format: "2025 05")
- Provides more granular time-based analysis

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
    dest_city='OMAHA',
    quarter='2025 2',
    order_count=8,
    avg_transit_days=1,
    actual_transit_days=4
)
```

**New Format Usage:**
```python
prediction = model.predict(
    carrier='ODFL',
    source_city='RICHMOND',
    source_state='VA',
    source_country='US',
    dest_city='WINDSOR',
    dest_state='CT', 
    dest_country='US',
    tracking_month='2025 05',
    order_count=73,
    avg_transit_days=2,
    actual_transit_days=4
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
- `TRACKING_MONTH` encoding (vs. `QTR` encoding)
- Separate encoders for:
  - Source city, state, country
  - Destination city, state, country
- Comprehensive lane identifiers including full geographic hierarchy

**Legacy Format Features:**
- Maintains original `QTR` encoding
- City-only source and destination encoding
- Backward compatible with existing models

### Feature Engineering Improvements

1. **Geographic Granularity**: State and country features enable better regional pattern recognition
2. **Temporal Granularity**: Month-level tracking provides finer time-based insights
3. **Enhanced Lane Definitions**: Full geographic lane identifiers improve specificity

## Migration Steps

### For New Implementations
1. Use the new data format with `TRACKING_MONTH` and expanded location fields
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
python test_new_format.py
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
- **Temporal Precision**: Monthly tracking enables more precise seasonal analysis
- **Enhanced Scalability**: More granular features support better scaling to larger datasets

### Backward Compatibility
- **Zero Breaking Changes**: Existing legacy implementations continue to work
- **Automatic Detection**: No manual configuration needed
- **Consistent API**: Same prediction interface for both formats

## Model Persistence

### Enhanced Model Saving
- Automatically saves all encoders for both formats
- Preserves data format information
- Maintains backward compatibility with legacy saved models

### Model Loading
- Automatically detects saved model format
- Loads appropriate encoders based on training data format
- Handles missing encoders gracefully for legacy models

## Best Practices

### For New Projects
1. Use the new format with expanded geographic and temporal features
2. Leverage state and country information for regional analysis
3. Use monthly tracking for precise time-based patterns

### For Existing Projects
1. Continue using legacy format if sufficient for current needs
2. Consider migrating to new format for enhanced capabilities
3. Test thoroughly when switching between formats

### Data Quality
1. Ensure consistent state/country codes in new format
2. Validate location data hierarchy (city-state-country relationships)
3. Maintain data quality standards for both time formats

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
- Check that feature information files are present

### Debug Information
Enable detailed logging to see:
- Data format detection results
- Preprocessing steps and feature counts
- Model architecture and training progress
- Prediction input validation

## Future Enhancements

### Planned Improvements
1. **Enhanced Geographic Features**: Support for additional location hierarchies
2. **Temporal Extensions**: Support for daily or weekly tracking periods
3. **Advanced Feature Engineering**: Automated geographic and temporal feature creation
4. **Performance Optimizations**: Further improvements for large-scale datasets

### Migration Path
- The current implementation provides a solid foundation for future enhancements
- Backward compatibility will be maintained in future versions
- Additional features will be additive rather than breaking

## Enhanced Simplified Format

### Complete Location Information in Simplified Mode
The simplified prediction format now includes complete location information for the new data format:

**Legacy Simplified Format:**
```json
{
  "carrier": "ODFL",
  "source_city": "ELWOOD", 
  "dest_city": "OMAHA",
  "quarter": "2025 2",
  "predicted_ontime_performance": 89.7
}
```

**New Simplified Format (Enhanced):**
```json
{
  "carrier": "ODFL",
  "source_city": "RICHMOND",
  "source_state": "VA",
  "source_country": "US", 
  "dest_city": "WINDSOR",
  "dest_state": "CT",
  "dest_country": "US",
  "predicted_ontime_performance": 85.5
}
```

### Benefits
- **Complete Geographic Context**: State and country information preserved in simplified mode
- **Consistent Lane Identification**: Full location hierarchy maintained for better integration
- **Optimal Field Ordering**: Predicted performance always appears as the final column for clarity
- **Backward Compatibility**: Legacy format simplified predictions unchanged

## Future Enhancements 