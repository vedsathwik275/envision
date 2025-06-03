# Project TODO: RIQ Rate API Integration

## 🎯 High-Level Objectives

This project aims to integrate the RIQ Rate Quote API into the chat interface, allowing users to get rate quotes by typing natural language requests. The system will make two API calls: one to get the cheapest carrier rate and another to get the rate for the best performing carrier identified from chat analysis.

1.  **[ ] Integrate RIQ Rate Quote API into Chat:** Connect the chat interface's rate inquiry detection to the backend's `/rate-quote` and `/cheap-rate-quote` API endpoints.
2.  **[ ] Implement Dual Rate Query Strategy:** Use `/cheap-rate-quote` to get the cheapest carrier option and `/rate-quote` to get the rate for the best performing carrier identified from chat parsing.
3.  **[ ] Parse Chat Response for Best Carrier:** Extract the best carrier information from the already-parsed chat response structured data.
4.  **[ ] Extract Location Data for API Requests:** Parse source and destination cities from the chat response to build proper API request payloads.
5.  **[ ] Update RIQ Card with Rate Results:** Display both cheapest carrier and best carrier rates in the RIQ card with clear comparisons.
6.  **[ ] Add UI Feedback (Loading/Errors):** Provide clear visual indicators during API requests and handle error states gracefully.
7.  **[ ] Configure API Endpoint:** Ensure the frontend is configured with the correct backend API URL for the data_tool service.

## 📋 Prerequisites

* **[ ] Access to Codebase:** `envision_product/chat/poc_frontend/script.js` and `index.html` for the chat interface.
* **[ ] Running Data Tool Backend:** The `envision_product/tools/data_tool` FastAPI application running on port 8006 (or configured port).
* **[ ] API Understanding:** Knowledge of the two RIQ API endpoints:
  - `/rate-quote`: Requires `servprov_gid` (service provider/carrier ID) for specific carrier rates
  - `/cheap-rate-quote`: No `servprov_gid` required, returns rates from all carriers to find cheapest
* **[ ] Current System Analysis:** Understanding of existing chat parsing that extracts `bestCarrier`, `sourceCity`, `destinationCity`, and other lane information.

## 🤔 Key Assumptions

* **[ ] Existing RIQ Card Structure:** The chat interface has the `rate-inquiry-status` and `rate-inquiry-content` elements for displaying rate information.
* **[ ] Chat Parsing Works:** The `parseLaneInformationFromResponse()` function already extracts necessary data including `bestCarrier`, `sourceCity`, `destinationCity`.
* **[ ] Backend API Stable:** The data_tool backend at `http://localhost:8006` is accessible and the `/rate-quote` and `/cheap-rate-quote` endpoints work as documented.
* **[ ] Default Parameters:** Use reasonable defaults for missing optional data (weight, volume, etc.) when making API requests.

## 🚀 Implementation Plan

### Phase 1: Backend Analysis and Configuration

1.  **[ ] Configure RIQ API Base URL:**
    * Add `RIQ_API_BASE_URL` constant at the top of `script.js` set to `http://localhost:8006` (or appropriate backend URL).
    * Verify this matches the running data_tool service port.

2.  **[ ] Understand Backend API Contracts:**
    * **`/rate-quote` endpoint:** Accepts `RateRequestModel` with `servprov_gid` for specific carrier rates
    * **`/cheap-rate-quote` endpoint:** Accepts `SimpleRateRequestModel` without `servprov_gid` for all carrier rates
    * Both return `RateResponseModel` with success flag, data, and optional error message
    * Response data structure: `data.rateAndRouteResponse` array with rate information

### Phase 2: Enhanced Data Extraction and Mapping

3.  **[ ] Create Location Parsing Helper Functions:**
    * **[ ] `extractLocationData(cityName)`:** Parse city name to extract city, state, and create a reasonable postal code default
    * **[ ] Handle format variations:** Support "City, ST", "City ST", "City" formats
    * **[ ] State code mapping:** Convert full state names to 2-letter codes if needed
    * **[ ] Default postal codes:** Provide reasonable defaults for major cities when specific zip not available

4.  **[ ] Create RIQ Request Builder Functions:**
    * **[ ] `buildLocationObject(city, state, zip)`:** Create location object matching backend `LocationModel`
    * **[ ] `buildItemObject(weight, volume)`:** Create item object with defaults (weight in LB, volume in CUFT)
    * **[ ] `buildRateRequest(sourceLocation, destLocation, items, servprovGid)`:** Build complete rate request
    * **[ ] `buildSimpleRateRequest(sourceLocation, destLocation, items)`:** Build request without carrier ID

5.  **[ ] Extract Default Values from Chat Data:**
    * **[ ] Parse weight from `laneInfo.weight`** (e.g., "2400 lbs" → 2400, "LB")
    * **[ ] Parse volume from `laneInfo.volume`** (e.g., "150 cuft" → 150, "CUFT")
    * **[ ] Use sensible defaults:** Weight: 1000 LB, Volume: 50 CUFT if not specified
    * **[ ] Currency defaults:** "USD" for declared value

### Phase 3: Carrier ID Mapping and API Integration

6.  **[ ] Implement Best Carrier to Service Provider GID Mapping:**
    * **[ ] Create `mapCarrierToServprovGid(carrierName)`** function
    * **[ ] Handle common carrier name variations** (case insensitive, abbreviations)
    * **[ ] Use default servprov_gid** ("BSL.RYGB") if mapping not found
    * **[ ] Log mapping results** for debugging and future improvements

7.  **[ ] Create Dual API Call Functions:**
    * **[ ] `getCheapestCarrierRate(requestPayload)`:** Call `/cheap-rate-quote` endpoint
    * **[ ] `getBestCarrierRate(requestPayload)`:** Call `/rate-quote` endpoint with specific carrier
    * **[ ] `executeDualRateQuery(laneInfo)`:** Orchestrate both API calls and combine results
    * **[ ] Error handling:** Gracefully handle API failures, network issues, and partial failures

### Phase 4: RIQ Card UI Enhancement

8.  **[ ] Enhance `retrieveRateInquiry()` Function:**
    * **[ ] Replace placeholder with actual API integration**
    * **[ ] Extract current `laneInfo` from the displayed RIQ card data**
    * **[ ] Call `executeDualRateQuery(laneInfo)` and handle results**
    * **[ ] Update UI with loading states during API calls**

9.  **[ ] Update RIQ Card Display Logic:**
    * **[ ] Modify `updateRateInquiryCard()` to show "Ready for API Call" state initially**
    * **[ ] Create `displayRateComparisonResults(cheapestRate, bestCarrierRate)` function**
    * **[ ] Show side-by-side comparison** of cheapest carrier vs best performing carrier
    * **[ ] Include rate amounts, carriers, transit times, and service types**
    * **[ ] Highlight cost savings or performance trade-offs**

10. **[ ] Implement Comprehensive Error Handling:**
    * **[ ] Network connectivity errors:** Show "Unable to connect to rate service"
    * **[ ] API errors:** Display specific error messages from backend
    * **[ ] Partial failures:** Handle when one API call succeeds but other fails
    * **[ ] Invalid location errors:** Guide user to provide more specific location data

### Phase 5: Advanced Features and Polish

11. **[ ] Add Rate Result Analytics:**
    * **[ ] Calculate potential savings** (difference between best carrier and cheapest)
    * **[ ] Show percentage differences** in cost and performance
    * **[ ] Recommend optimal choice** based on cost vs performance trade-offs

12. **[ ] Implement Rate History and Caching:**
    * **[ ] Store recent rate queries** in browser localStorage
    * **[ ] Show "Last Updated" timestamps** on rate information
    * **[ ] Allow manual refresh** of rate data
    * **[ ] Cache results** for same lane/parameters to reduce API calls

13. **[ ] Enhanced Location Intelligence:**
    * **[ ] Validate city/state combinations** before API calls
    * **[ ] Suggest corrections** for invalid or ambiguous locations
    * **[ ] Support major airport codes** as location identifiers
    * **[ ] ZIP code auto-completion** for known cities

### Phase 6: Testing and Validation

14. **[ ] Comprehensive End-to-End Testing:**
    * **[ ] Test with various chat queries** containing rate requests
    * **[ ] Verify both API endpoints** are called correctly
    * **[ ] Test error scenarios:** Invalid locations, API downtime, malformed responses
    * **[ ] Validate rate comparison accuracy** and UI updates
    * **[ ] Test with different carrier names** and mapping scenarios

15. **[ ] Performance and User Experience Testing:**
    * **[ ] Measure API response times** and optimize UI feedback
    * **[ ] Test with slow network connections**
    * **[ ] Verify loading states** and error recovery
    * **[ ] Test browser compatibility** and mobile responsiveness

## 📐 Technical Implementation Details

### API Request Structure

**For Cheapest Carrier (using `/cheap-rate-quote`):**
```javascript
{
  "source_location": {
    "city": "Dallas",
    "province_code": "TX", 
    "postal_code": "75201",
    "country_code": "US"
  },
  "destination_location": {
    "city": "Chicago",
    "province_code": "IL",
    "postal_code": "60601", 
    "country_code": "US"
  },
  "items": [{
    "weight_value": 2400,
    "weight_unit": "LB",
    "volume_value": 150,
    "volume_unit": "CUFT"
  }]
}
```

**For Best Carrier (using `/rate-quote`):**
```javascript
// Same as above, plus:
{
  "servprov_gid": "BSL.CARRIER_NAME", // Mapped from bestCarrier
  // ... other fields
}
```

### Response Processing

**Expected Response Structure:**
```javascript
{
  "success": true,
  "data": {
    "rateAndRouteResponse": [{
      "totalCost": 1250.00,
      "transitTime": "2-3 days",
      "carrier": "CARRIER_NAME",
      "serviceType": "Standard"
    }]
  }
}
```

### Error Handling Strategy

1. **Network Errors:** Show user-friendly connectivity messages
2. **API Validation Errors:** Display specific field validation issues  
3. **Location Errors:** Guide users to provide valid city/state combinations
4. **Rate Unavailable:** Explain when rates cannot be obtained and suggest alternatives
5. **Partial Success:** Show available rates even if one API call fails

## ✅ Definition of Done

* **[ ] Dual API Integration Complete:** Both `/cheap-rate-quote` and `/rate-quote` endpoints are successfully integrated
* **[ ] Rate Comparison Display:** RIQ card shows side-by-side comparison of cheapest vs best performing carrier
* **[ ] Error Handling Robust:** All error scenarios are gracefully handled with helpful user messages
* **[ ] Location Parsing Accurate:** City/state extraction from chat responses works reliably
* **[ ] Carrier Mapping Functional:** Best carrier names from chat are properly mapped to service provider GIDs
* **[ ] UI Feedback Complete:** Loading states, success indicators, and error messages are implemented
* **[ ] Performance Optimized:** API calls are efficient and UI remains responsive
* **[ ] Testing Verified:** End-to-end functionality works with various chat inputs and scenarios

## 🔄 Current System Integration Points

### Existing Functions to Leverage:
- `parseLaneInformationFromResponse()` - Already extracts bestCarrier, sourceCity, destinationCity
- `updateRateInquiryCard()` - Already displays parsed lane info and "Get Rates" button
- `isRateInquiryPrompt()` - Already detects rate-related chat messages
- `showNotification()` - For user feedback during API operations

### New Functions to Implement:
- `executeRateQueries()` - Main orchestration function for dual API calls
- `mapCarrierToServprovGid()` - Carrier name to service provider ID mapping
- `buildRateRequestPayload()` - Construct API request from parsed data  
- `displayRateResults()` - Update RIQ card with rate comparison results
- `handleRateQueryErrors()` - Comprehensive error handling and user feedback

### Modified Functions:
- `retrieveRateInquiry()` - Replace placeholder with actual API integration
- `updateRateInquiryCard()` - Enhance to show rate results and comparisons

## 💡 Future Enhancements (Out of Scope)

* **Multi-Modal Rate Comparison:** Include rail, air, and ocean freight options
* **Real-Time Rate Updates:** WebSocket integration for live rate changes
* **Rate Alerts:** Notify users when rates change for saved lanes
* **Historical Rate Analysis:** Show rate trends over time
* **API Rate Limiting:** Implement request throttling and queuing
* **Advanced Carrier Mapping:** Machine learning for better carrier name recognition