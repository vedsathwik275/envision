# Historical Data Card Feature - Implementation Plan

## Overview

This document outlines the implementation plan for adding a Historical Data card feature to the RAG Chatbot interface. The feature will display historical transportation data based on parsed lane information from chat responses, complementing the existing RAQ and Spot API cards.

## Current Architecture Analysis

### Frontend Structure
- **Location**: `envision_product/chat/poc_frontend/`
- **Main Files**: `index.html`, `script.js`
- **Current Cards**: Rate Inquiry Details, Spot API Analysis
- **Lane Parsing**: Existing `parseAndUpdateLaneInfo()` function extracts route information

### Backend Structure
- **Location**: `envision_product/chat/backend/`
- **Framework**: FastAPI
- **Current APIs**: Knowledge bases, Chat services
- **Architecture**: Modular with separate routes, services, and models

### Data Source
- **File**: `envision_product/neural/data/HistoricalData_v2.csv`
- **Structure**: SOURCE_CITY, SOURCE_STATE, SOURCE_COUNTRY, DEST_CITY, DEST_STATE, DEST_COUNTRY, TMODE, COST_PER_LB, COST_PER_MILE, COST_PER_CUFT, SHP_COUNT, MODE_PREFERENCE
- **Records**: 3,074 historical transportation records

## Implementation Architecture

### Design Pattern
The Historical Data card will follow the same architectural pattern as existing cards:
1. **HTML Structure**: Card container with status indicator and content area
2. **JavaScript Integration**: Parse lane info → API call → Update card display
3. **Backend API**: RESTful endpoint to query and filter historical data
4. **Styling**: Consistent with existing Tailwind CSS design system

### Data Flow
```
Chat Response → Lane Parser → Historical Data API → Card Display
```

## Detailed Implementation Plan

### Phase 1: Backend Implementation

#### 1.1 Create Historical Data Models
**File**: `envision_product/chat/backend/api/models.py`

```python
# Add new Pydantic models
class HistoricalDataRequest(BaseModel):
    source_city: Optional[str] = None
    source_state: Optional[str] = None
    source_country: Optional[str] = "US"
    dest_city: Optional[str] = None
    dest_state: Optional[str] = None
    dest_country: Optional[str] = "US"
    transport_mode: Optional[str] = None
    limit: Optional[int] = 50

class HistoricalRecord(BaseModel):
    source_city: str
    source_state: str
    source_country: str
    dest_city: str
    dest_state: str
    dest_country: str
    transport_mode: str
    cost_per_lb: float
    cost_per_mile: float
    cost_per_cuft: float
    shipment_count: int
    mode_preference: str

class HistoricalDataResponse(BaseModel):
    records: List[HistoricalRecord]
    total_count: int
    lane_summary: Dict[str, Any]
    cost_statistics: Dict[str, float]
```

#### 1.2 Create Historical Data Service
**File**: `envision_product/chat/backend/api/services/historical_data_service.py`

```python
class HistoricalDataService:
    """Service for managing historical transportation data."""
    
    def __init__(self):
        self.data_file = "data/HistoricalData_v2.csv"
        self.df = None
        self._load_data()
    
    async def query_historical_data(self, request: HistoricalDataRequest) -> HistoricalDataResponse:
        """Query historical data based on lane information."""
        pass
    
    def _load_data(self) -> None:
        """Load CSV data with caching."""
        pass
    
    def _normalize_city_name(self, city: str) -> str:
        """Normalize city names for matching."""
        pass
    
    def _calculate_statistics(self, filtered_df) -> Dict[str, float]:
        """Calculate cost statistics for filtered data."""
        pass
```

#### 1.3 Create Historical Data Routes
**File**: `envision_product/chat/backend/api/routes/historical_data.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from ..services.historical_data_service import HistoricalDataService
from ..models import HistoricalDataRequest, HistoricalDataResponse

router = APIRouter(prefix="/historical-data", tags=["Historical Data"])

@router.post("/query", response_model=HistoricalDataResponse)
async def query_historical_data(
    request: HistoricalDataRequest,
    service: HistoricalDataService = Depends()
) -> HistoricalDataResponse:
    """Query historical transportation data by lane information."""
    pass

@router.get("/health")
async def historical_data_health():
    """Health check for historical data service."""
    pass
```

#### 1.4 Update Main Application
**File**: `envision_product/chat/backend/api/main.py`

```python
# Add import
from .routes import historical_data as historical_routes

# Add router inclusion
app.include_router(historical_routes.router, prefix=settings.api_v1_prefix)
```

### Phase 2: Frontend Implementation

#### 2.1 Add Historical Data Card HTML
**File**: `envision_product/chat/poc_frontend/index.html`
**Location**: After line 380 (after Spot API card)

```html
<!-- Historical Data Card -->
<div class="bg-white rounded-xl shadow-sm border border-neutral-200">
    <div class="p-6 border-b border-neutral-100">
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <i class="fas fa-history text-purple-500 mr-3 text-xl"></i>
                <h3 class="text-lg font-semibold text-neutral-900">Historical Data Analysis</h3>
            </div>
            <span id="historical-data-status" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                No data
            </span>
        </div>
    </div>
    <div class="p-6">
        <div id="historical-data-content" class="space-y-4">
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-database text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about transportation routes to see historical data</p>
                <p class="text-sm mt-2">Example: "Show me rates from Chicago to Miami"</p>
            </div>
        </div>
    </div>
</div>
```

#### 2.2 Update Grid Layout
**File**: `envision_product/chat/poc_frontend/index.html`
**Location**: Line 330 (Lane Information Cards Section)

```html
<!-- Update grid to accommodate third card -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Existing cards + new historical data card -->
</div>
```

#### 2.3 Implement JavaScript Functions
**File**: `envision_product/chat/poc_frontend/script.js`

```javascript
// Add to parseAndUpdateLaneInfo function (around line 930)
function parseAndUpdateLaneInfo(userMessage, response) {
    const laneInfo = parseLaneInformationFromResponse(response.answer);
    
    // Store lane info globally for API access
    window.currentLaneInfo = laneInfo;
    
    const hasPerformanceAnalysis = laneInfo.bestCarrier || laneInfo.worstCarrier || 
                                 laneInfo.sourceCity || laneInfo.destinationCity;
    
    if (hasPerformanceAnalysis) {
        updateRateInquiryCard(laneInfo, userMessage, response);
        updateSpotAPICard(laneInfo, userMessage, response);
        updateHistoricalDataCard(laneInfo, userMessage, response); // NEW LINE
    }
}

// New function to add
async function updateHistoricalDataCard(laneInfo, userMessage, response) {
    const statusElement = document.getElementById('historical-data-status');
    const contentElement = document.getElementById('historical-data-content');
    
    // Update status to loading
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
    statusElement.textContent = 'Loading...';
    
    try {
        const historicalData = await fetchHistoricalData(laneInfo);
        displayHistoricalData(historicalData, contentElement);
        
        // Update status to success
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800';
        statusElement.textContent = `${historicalData.total_count} Records Found`;
        
    } catch (error) {
        console.error('Failed to fetch historical data:', error);
        
        // Update status to error
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        statusElement.textContent = 'Data Error';
        
        contentElement.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p>Failed to load historical data</p>
                <p class="text-sm mt-2">${error.message}</p>
            </div>
        `;
    }
}

async function fetchHistoricalData(laneInfo) {
    const requestPayload = {
        source_city: laneInfo.sourceCity,
        dest_city: laneInfo.destinationCity,
        limit: 50
    };
    
    const response = await fetch(`${API_BASE_URL}/historical-data/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestPayload)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
}

function displayHistoricalData(data, contentElement) {
    let content = `
        <div class="space-y-4">
            <!-- Lane Summary -->
            <div class="bg-purple-50 rounded-lg p-4">
                <h4 class="font-medium text-purple-900 mb-3 flex items-center">
                    <i class="fas fa-route text-purple-600 mr-2"></i>
                    Lane Summary: ${data.lane_summary.route || 'Unknown Route'}
                </h4>
                <div class="grid grid-cols-2 gap-3 text-sm">
                    <div><span class="text-neutral-600">Total Records:</span> <span class="font-medium">${data.total_count}</span></div>
                    <div><span class="text-neutral-600">Avg Cost/Mile:</span> <span class="font-medium">$${data.cost_statistics.avg_cost_per_mile || 'N/A'}</span></div>
                    <div><span class="text-neutral-600">Avg Cost/Lb:</span> <span class="font-medium">$${data.cost_statistics.avg_cost_per_lb || 'N/A'}</span></div>
                    <div><span class="text-neutral-600">Most Common Mode:</span> <span class="font-medium">${data.lane_summary.most_common_mode || 'N/A'}</span></div>
                </div>
            </div>
            
            <!-- Historical Records Table -->
            <div class="bg-neutral-50 rounded-lg p-4">
                <h4 class="font-medium text-neutral-900 mb-3">Recent Historical Records</h4>
                <div class="overflow-x-auto">
                    <table class="min-w-full text-sm">
                        <thead>
                            <tr class="border-b border-neutral-200">
                                <th class="text-left py-2 px-3">Route</th>
                                <th class="text-left py-2 px-3">Mode</th>
                                <th class="text-left py-2 px-3">Cost/Mile</th>
                                <th class="text-left py-2 px-3">Cost/Lb</th>
                                <th class="text-left py-2 px-3">Preference</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    // Add table rows for historical records
    data.records.slice(0, 10).forEach(record => {
        const preferenceColor = record.mode_preference === 'Preferred Mode' ? 'text-green-600' : 'text-red-600';
        content += `
            <tr class="border-b border-neutral-100">
                <td class="py-2 px-3">${record.source_city} → ${record.dest_city}</td>
                <td class="py-2 px-3">${record.transport_mode}</td>
                <td class="py-2 px-3">$${record.cost_per_mile}</td>
                <td class="py-2 px-3">$${record.cost_per_lb}</td>
                <td class="py-2 px-3 ${preferenceColor}">${record.mode_preference}</td>
            </tr>
        `;
    });
    
    content += `
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- View All Data Button -->
            <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white">
                <div class="flex items-center justify-between">
                    <div>
                        <h5 class="font-medium mb-1">Detailed Historical Analysis</h5>
                        <p class="text-purple-100 text-sm">View complete historical data and trends</p>
                    </div>
                    <button onclick="viewDetailedHistoricalData()" class="bg-white text-purple-600 px-4 py-2 rounded-lg font-medium hover:bg-purple-50 transition-colors flex items-center">
                        <i class="fas fa-chart-area mr-2"></i>
                        View Details
                    </button>
                </div>
            </div>
        </div>
    `;
    
    contentElement.innerHTML = content;
}

function viewDetailedHistoricalData() {
    // Future implementation for detailed view/modal
    showNotification('Detailed historical analysis feature coming soon!', 'info');
}

// Add to clearLaneInfoCards function (around line 834)
function clearLaneInfoCards() {
    // Clear Rate Inquiry Card
    const rateInquiryStatus = document.getElementById('rate-inquiry-status');
    const rateInquiryContent = document.getElementById('rate-inquiry-content');
    
    if (rateInquiryStatus) {
        rateInquiryStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        rateInquiryStatus.textContent = 'No data';
    }
    
    if (rateInquiryContent) {
        rateInquiryContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-search text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about lane rates to see parsed information here</p>
                <p class="text-sm mt-2">Example: "What's the best rate from Los Angeles to Chicago?"</p>
            </div>
        `;
    }
    
    // Clear Spot API Card
    const spotApiStatus = document.getElementById('spot-api-status');
    const spotApiContent = document.getElementById('spot-api-content');
    
    if (spotApiStatus) {
        spotApiStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        spotApiStatus.textContent = 'No data';
    }
    
    if (spotApiContent) {
        spotApiContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-analytics text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about carrier performance or spot rates to see analysis here</p>
                <p class="text-sm mt-2">Example: "Show carrier performance for Dallas to Miami"</p>
            </div>
        `;
    }
    
    // Clear Historical Data Card (NEW)
    const historicalDataStatus = document.getElementById('historical-data-status');
    const historicalDataContent = document.getElementById('historical-data-content');
    
    if (historicalDataStatus) {
        historicalDataStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        historicalDataStatus.textContent = 'No data';
    }
    
    if (historicalDataContent) {
        historicalDataContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-database text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about transportation routes to see historical data</p>
                <p class="text-sm mt-2">Example: "Show me rates from Chicago to Miami"</p>
            </div>
        `;
    }
}
```

### Phase 3: Data Processing Implementation

#### 3.1 Move Historical Data File
**Source**: `envision_product/neural/data/HistoricalData_v2.csv`
**Destination**: `envision_product/chat/backend/data/HistoricalData_v2.csv`

#### 3.2 Update Requirements
**File**: `envision_product/chat/backend/requirements.txt`

```txt
# Add pandas for CSV processing
pandas>=2.0.0
numpy>=1.24.0
```

### Phase 4: Integration & Testing

#### 4.1 Testing Scenarios
1. **Lane Information Parsing**: Test with existing chat responses
2. **API Endpoint Testing**: Verify data filtering and response format
3. **Frontend Integration**: Ensure seamless card updates
4. **Error Handling**: Test with invalid/missing data
5. **Performance**: Test with large datasets

#### 4.2 Manual Testing Queries
- "Show me rates from Chicago to Miami"
- "What's the cost per mile from Delta BC to Calgary AB?"
- "Compare transportation modes for Los Angeles to Denver"
- "Historical performance for LTL shipments"

## File Structure After Implementation

```
envision_product/chat/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── historical_data.py (NEW)
│   │   │   ├── knowledge_bases.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── historical_data_service.py (NEW)
│   │   │   ├── kb_service.py
│   │   │   └── chat_service.py
│   │   ├── models.py (UPDATED)
│   │   └── main.py (UPDATED)
│   ├── data/
│   │   └── HistoricalData_v2.csv (MOVED)
│   └── requirements.txt (UPDATED)
└── poc_frontend/
    ├── index.html (UPDATED)
    └── script.js (UPDATED)
```

## Implementation Priority

### High Priority (MVP)
1. Backend API endpoint with basic filtering
2. Frontend card with data display
3. Integration with existing lane parsing
4. Basic error handling

### Medium Priority
1. Advanced filtering options
2. Cost statistics and summaries
3. Data visualization improvements
4. Export functionality

### Low Priority (Future Enhancements)
1. Interactive charts and graphs
2. Historical trend analysis
3. Predictive cost modeling
4. Advanced data comparison tools

## Success Criteria

### Functional Requirements
- ✅ Historical data card displays when lane information is parsed
- ✅ API successfully filters data based on source/destination
- ✅ Card shows relevant historical records and statistics
- ✅ Integration works seamlessly with existing cards

### Performance Requirements
- ✅ API response time < 2 seconds
- ✅ Frontend card updates smoothly
- ✅ CSV data loads efficiently on backend startup
- ✅ Handles up to 10,000 records without performance issues

### User Experience Requirements
- ✅ Consistent design with existing cards
- ✅ Clear data presentation and formatting
- ✅ Appropriate loading states and error messages
- ✅ Intuitive navigation and interaction

## Technical Considerations

### Data Matching Strategy
- **Exact Match**: First attempt exact city/state matching
- **Fuzzy Match**: Fall back to partial/fuzzy matching for common variations
- **Normalization**: Convert cities to consistent format (capitalize, trim)
- **Caching**: Cache processed data for performance

### Error Handling
- **No Data Found**: Display appropriate message with suggestions
- **API Errors**: Show user-friendly error messages
- **Network Issues**: Implement retry logic and offline states
- **Invalid Input**: Validate and sanitize input parameters

### Performance Optimization
- **Data Indexing**: Create efficient indexes for common queries
- **Caching**: Implement response caching for frequent requests
- **Pagination**: Limit response size and implement pagination
- **Lazy Loading**: Load detailed data only when requested

## Future Enhancements

### Advanced Analytics
1. **Cost Trend Analysis**: Track cost changes over time
2. **Seasonal Patterns**: Identify seasonal cost variations
3. **Mode Comparison**: Compare efficiency across transport modes
4. **Route Optimization**: Suggest optimal routes based on historical data

### Data Visualization
1. **Interactive Charts**: Cost trends, volume patterns, mode preferences
2. **Geographical Maps**: Route visualization on interactive maps
3. **Comparative Analysis**: Side-by-side lane comparisons
4. **Export Options**: PDF reports, Excel exports, data downloads

### Machine Learning Integration
1. **Cost Prediction**: Predict future costs based on historical trends
2. **Route Recommendations**: ML-powered route optimization
3. **Anomaly Detection**: Identify unusual cost patterns
4. **Demand Forecasting**: Predict transportation demand

This comprehensive implementation plan provides a roadmap for successfully integrating the Historical Data card feature into the existing RAG Chatbot system while maintaining consistency with current architecture and design patterns. 