# Spot Rate Matrix Implementation Plan

## Overview
Implement a spot rate matrix feature that provides carriers and their spot rates for the next 7 days from a shipment date for a given lane. Since we only have one day of actual data, we'll generate the other 6 days using ±5% variance with numpy.

## Current Architecture Analysis

### Existing Pattern (Historical Data)
- **Route**: `api/routes/historical_data.py` - Handles HTTP endpoints
- **Service**: `api/services/historical_data_service.py` - Business logic and data processing
- **Models**: `api/models.py` - Pydantic models for request/response
- **Data**: `data/HistoricalData_v2.csv` - Source data file
- **Registration**: Routes registered in `main.py`

### Spot Rate Data Structure
- **File**: `data/SPOT_RATE_V1.csv`
- **Columns**: SOURCE_CITY, SOURCE_STATE, SOURCE_COUNTRY, DEST_CITY, DEST_STATE, DEST_COUNTRY, TMODE, CARRIER, SPOT_RATE, DISTANCE, COST_PER_MILE

## Implementation Plan

### Phase 1: Data Models (models.py)
1. **SpotRateRequest Model**
   - source_city: Optional[str]
   - source_state: Optional[str] 
   - source_country: Optional[str] = "US"
   - dest_city: Optional[str]
   - dest_state: Optional[str]
   - dest_country: Optional[str] = "US"
   - transport_mode: Optional[str]
   - shipment_date: date (the base date for 7-day projection)

2. **CarrierSpotRate Model**
   - carrier: str
   - rates_by_date: Dict[str, float] (date string -> spot rate)

3. **SpotRateMatrixResponse Model**
   - carriers: List[CarrierSpotRate]
   - date_range: List[str] (7 consecutive dates)
   - lane_info: Dict[str, Any] (lane summary)
   - query_parameters: SpotRateRequest

### Phase 2: Service Layer (spot_rate_service.py)
1. **SpotRateService Class**
   - Load and normalize spot rate data from CSV
   - Filter data by lane (source/destination/mode)
   - Get unique carriers for the filtered lane
   - Generate 7-day rate matrix using numpy for variance

2. **Key Methods**
   - `_load_data()`: Load CSV with normalization
   - `_filter_by_lane()`: Apply lane filters
   - `_get_carriers_for_lane()`: Extract unique carriers
   - `_generate_rate_matrix()`: Create 7-day rates with ±5% variance
   - `query_spot_rate_matrix()`: Main query method

3. **Rate Generation Logic**
   - Base rate from actual data (day 1)
   - Days 2-7: Use numpy.random.uniform with ±5% variance
   - Ensure rates stay positive
   - Round to 2 decimal places

### Phase 3: API Route (spot_rate.py)
1. **Router Setup**
   - Prefix: `/spot-rate`
   - Tags: ["Spot Rate"]
   - Standard error responses

2. **Endpoints**
   - `POST /matrix`: Main endpoint for spot rate matrix
   - `GET /health`: Health check endpoint

3. **Dependency Injection**
   - Service instance creation
   - Error handling for service initialization

### Phase 4: Integration
1. **Route Registration**
   - Add spot rate router to main.py
   - Follow existing pattern

2. **Testing**
   - Manual testing with various lane combinations
   - Verify 7-day matrix generation
   - Test edge cases (no carriers, single carrier, multiple carriers)

## Implementation Details

### Numpy Variance Generation
```python
base_rate = float(spot_rate_from_csv)
variance_range = base_rate * 0.05  # ±5%
min_rate = base_rate - variance_range
max_rate = base_rate + variance_range

# Generate 6 additional days (excluding the base day)
additional_rates = np.random.uniform(min_rate, max_rate, 6)
all_rates = [base_rate] + additional_rates.tolist()
```

### Date Range Generation
```python
from datetime import date, timedelta

def generate_date_range(shipment_date: date, days: int = 7) -> List[str]:
    return [(shipment_date + timedelta(days=i)).isoformat() for i in range(days)]
```

### Carrier Matrix Structure
```json
{
  "carriers": [
    {
      "carrier": "RBTW",
      "rates_by_date": {
        "2024-01-15": 2311.16,
        "2024-01-16": 2250.45,
        "2024-01-17": 2380.90,
        ...
      }
    }
  ],
  "date_range": ["2024-01-15", "2024-01-16", ..., "2024-01-21"],
  "lane_info": {
    "route": "GRAND RAPIDS, MI to DELTA, BC",
    "transport_mode": "TL",
    "carrier_count": 1
  }
}
```

## Questions for Clarification

1. **Date Format**: Should the shipment_date in the request be ISO format (YYYY-MM-DD)?

2. **Variance Distribution**: Should the ±5% variance be:
   - Uniform distribution (all values equally likely)?
   - Normal distribution (clustering around base rate)?

3. **Rate Precision**: Should spot rates be rounded to 2 decimal places?

4. **Multiple Base Rates**: If a lane has multiple entries with the same carrier (different base rates), should we:
   - Use the average as base rate?
   - Use the most recent/highest/lowest rate?
   - Generate separate matrices?

5. **Empty Results**: How should we handle cases where:
   - No carriers found for the specified lane?
   - Invalid lane parameters?

6. **Performance**: Should we implement any caching for frequently requested lanes?

## File Structure After Implementation
```
backend/
├── api/
│   ├── models.py (updated with spot rate models)
│   ├── routes/
│   │   ├── historical_data.py
│   │   ├── chat.py
│   │   ├── knowledge_bases.py
│   │   └── spot_rate.py (new)
│   ├── services/
│   │   ├── historical_data_service.py
│   │   ├── chat_service.py
│   │   ├── kb_service.py
│   │   └── spot_rate_service.py (new)
│   └── main.py (updated to include spot rate router)
├── data/
│   ├── HistoricalData_v2.csv
│   └── SPOT_RATE_V1.csv
└── requirements.txt
```

## Success Criteria
1. ✅ API endpoint returns proper JSON matrix structure
2. ✅ 7-day rate generation with ±5% variance works correctly
3. ✅ Lane filtering matches historical data pattern
4. ✅ Multiple carriers handled appropriately
5. ✅ Edge cases handled gracefully
6. ✅ Follows established code patterns and conventions
7. ✅ Proper error handling and logging
8. ✅ Type annotations and docstrings included 