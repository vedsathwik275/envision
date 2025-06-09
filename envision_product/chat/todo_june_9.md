# Comprehensive Todo List for RAG Chatbot Updates

## 1. Auto Show SPOT Details for Same Date

### Frontend Changes (script.js)
- [x] Modify `updateSpotAPICard()` function to auto-trigger spot analysis when lane info is detected
- [x] Update `performSpotAnalysis()` to use current date as default if no date is selected
- [x] Add auto-date population logic:
  ```javascript
  // In updateSpotAPICard function, add:
  const shipDateInput = document.getElementById('spot-ship-date');
  if (!shipDateInput.value) {
    shipDateInput.value = new Date().toISOString().split('T')[0];
  }
  ```
- [x] Modify the auto-trigger delay to happen after RIQ completion (sequential execution)
- [x] Add status synchronization between RIQ and Spot analysis

### HTML Changes (index.html)
- [x] Update spot analysis card header to show auto-selected date
- [x] Add visual indicator when auto-analysis is triggered

## 2. Show Transport Mode on Spot Matrix and Summary

### Frontend Changes (script.js)
- [x] Modify `displaySpotRateMatrix()` function to include transport mode in summary
- [x] Update the rate statistics section to show mode breakdown:
  ```javascript
  // Add transport mode to summary grid
  if (laneInfo.equipmentType || laneInfo.transportMode) {
    content += `<div><span class="text-neutral-600">Mode:</span> <span class="font-medium">${laneInfo.equipmentType || 'N/A'}</span></div>`;
  }
  ```
- [x] Modify `displaySpotMatrixInModal()` to include transport mode column
- [x] Add transport mode to the matrix table headers
- [x] Update carrier data processing to extract and display transport mode

### Backend Integration
- [x] Ensure spot rate API response includes transport mode data
- [x] Verify transport mode is properly parsed from API response

## 3. Convert Order Release Management to Table with Checkboxes

### HTML Changes (index.html)
- [ ] Replace the order list div structure with a table:
  ```html
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-3 py-2 text-left">Select</th>
          <th class="px-3 py-2 text-left">Order ID</th>
          <th class="px-3 py-2 text-left">Cost</th>
          <th class="px-3 py-2 text-left">Date</th>
          <th class="px-3 py-2 text-left">Weight</th>
          <th class="px-3 py-2 text-left">Volume</th>
          <th class="px-3 py-2 text-left">Carrier</th>
        </tr>
      </thead>
      <tbody id="orders-table-body">
        <!-- Orders will be populated here -->
      </tbody>
    </table>
  </div>
  ```

### Frontend Changes (script.js)
- [ ] Rewrite `displayUnplannedOrders()` function to generate table rows instead of cards
- [ ] Add checkbox functionality:
  ```javascript
  function createOrderTableRow(order, index) {
    return `
      <tr class="border-b hover:bg-gray-50">
        <td class="px-3 py-2">
          <input type="checkbox" class="order-checkbox" data-order-id="${order.orderReleaseXid}" onchange="updateSelectedOrders()">
        </td>
        <td class="px-3 py-2">${escapeHtml(order.orderReleaseName)}</td>
        <!-- Add other columns -->
      </tr>
    `;
  }
  ```
- [ ] Add global selection tracking:
  ```javascript
  window.selectedOrders = [];
  function updateSelectedOrders() {
    const checkboxes = document.querySelectorAll('.order-checkbox:checked');
    window.selectedOrders = Array.from(checkboxes).map(cb => cb.dataset.orderId);
  }
  ```
- [ ] Add "Select All" functionality in table header
- [ ] Update order selection behavior (remove single order modal, use multi-select)

## 4. Add Carrier Dropdown to Order Release Management Header

### HTML Changes (index.html)
- [ ] Add carrier dropdown to Order Release Management card header:
  ```html
  <div class="flex items-center justify-between">
    <div class="flex items-center">
      <i class="fas fa-shipping-fast text-orange-500 mr-3 text-xl"></i>
      <h3 class="text-lg font-semibold text-neutral-900">Order Release Management</h3>
    </div>
    <div class="flex items-center space-x-3">
      <select id="carrier-selection-dropdown" class="appearance-none bg-neutral-50 border border-neutral-200 rounded-lg px-3 py-1 text-sm">
        <option value="">Select Carrier...</option>
      </select>
      <span id="order-release-status">No data</span>
    </div>
  </div>
  ```

### Frontend Changes (script.js)
- [ ] Create function to populate carrier dropdown from RIQ response:
  ```javascript
  function populateCarrierDropdown(riqResults) {
    const dropdown = document.getElementById('carrier-selection-dropdown');
    const carriers = [...new Set(riqResults.metadata.carriers)];
    
    dropdown.innerHTML = '<option value="">Select Carrier...</option>';
    carriers.forEach(carrier => {
      const option = document.createElement('option');
      option.value = carrier;
      option.textContent = cleanServiceProviderGid(carrier);
      dropdown.appendChild(option);
    });
  }
  ```
- [ ] Hook into RIQ completion to populate dropdown
- [ ] Add carrier selection change handler
- [ ] Update order display based on selected carrier

## 5. Auto Select Recommended Carrier

### Frontend Changes (script.js)
- [ ] Modify carrier dropdown population to auto-select recommended carrier:
  ```javascript
  function autoSelectRecommendedCarrier(riqResults, laneInfo) {
    const dropdown = document.getElementById('carrier-selection-dropdown');
    const recommendedCarrier = laneInfo.bestCarrier || riqResults.cheapest?.data?.carrier;
    
    if (recommendedCarrier) {
      dropdown.value = recommendedCarrier;
      dropdown.dispatchEvent(new Event('change'));
    }
  }
  ```
- [ ] Add visual indicator for auto-selected carrier (star icon, different styling)
- [ ] Update carrier dropdown to show "★ Recommended" next to auto-selected option

## 6. Create "Create Shipment" Button Under All Cards

### HTML Changes (index.html)
- [ ] Add shipment creation section below the cards grid:
  ```html
  <!-- Create Shipment Section -->
  <div class="mt-8 bg-white rounded-xl shadow-sm border border-neutral-200 p-6">
    <div class="text-center">
      <h3 class="text-lg font-semibold text-neutral-900 mb-4">Ready to Create Shipment?</h3>
      <button id="create-shipment-btn" class="inline-flex items-center px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed" disabled>
        <i class="fas fa-shipping-fast mr-2"></i>
        Create Shipment
      </button>
      <p class="text-sm text-neutral-500 mt-2" id="shipment-btn-status">Select orders and carrier to enable</p>
    </div>
  </div>
  ```

### Frontend Changes (script.js)
- [ ] Add button state management:
  ```javascript
  function updateCreateShipmentButton() {
    const btn = document.getElementById('create-shipment-btn');
    const status = document.getElementById('shipment-btn-status');
    const hasOrders = window.selectedOrders && window.selectedOrders.length > 0;
    const hasCarrier = document.getElementById('carrier-selection-dropdown').value;
    
    if (hasOrders && hasCarrier) {
      btn.disabled = false;
      status.textContent = `Ready to create shipment for ${window.selectedOrders.length} order(s)`;
    } else {
      btn.disabled = true;
      status.textContent = 'Select orders and carrier to enable';
    }
  }
  ```
- [ ] Add event listener for button click
- [ ] Integrate with order selection and carrier dropdown changes

## 7. Create Fake Success Screen for Shipment Creation

### HTML Changes (index.html)
- [ ] Add shipment success modal:
  ```html
  <!-- Shipment Success Modal -->
  <div id="shipment-success-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden z-50">
    <div class="flex items-center justify-center min-h-screen p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full">
        <div class="p-6 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <i class="fas fa-check text-green-600 text-xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Shipment Creation Initiated</h3>
          <p class="text-sm text-gray-600 mb-4" id="shipment-success-details">
            Your shipment request has been submitted successfully.
          </p>
          <div class="bg-gray-50 rounded-lg p-3 mb-4">
            <div class="text-xs text-gray-600" id="shipment-summary">
              <!-- Summary details -->
            </div>
          </div>
          <button id="close-shipment-success" class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            Continue
          </button>
        </div>
      </div>
    </div>
  </div>
  ```

### Frontend Changes (script.js)
- [ ] Create shipment creation handler:
  ```javascript
  async function handleCreateShipment() {
    const selectedOrders = window.selectedOrders;
    const selectedCarrier = document.getElementById('carrier-selection-dropdown').value;
    
    // Show loading state
    showLoading('Creating shipment...');
    
    // Simulate API call delay
    setTimeout(() => {
      hideLoading();
      showShipmentSuccess(selectedOrders, selectedCarrier);
    }, 2000);
  }
  
  function showShipmentSuccess(orders, carrier) {
    const modal = document.getElementById('shipment-success-modal');
    const summary = document.getElementById('shipment-summary');
    
    summary.innerHTML = `
      <div>Orders: ${orders.length}</div>
      <div>Carrier: ${cleanServiceProviderGid(carrier)}</div>
      <div>Shipment ID: SHP-${Date.now()}</div>
      <div>Status: Processing</div>
    `;
    
    modal.classList.remove('hidden');
  }
  ```
- [ ] Add modal close functionality
- [ ] Add cleanup after successful shipment creation (clear selections, reset forms)

## 8. Change Label from "Shipments" to "Order Volume"

### Global Text Replacements
- [ ] Search and replace in `index.html`:
  - [ ] Lane summary section: `shipments` → `order volume`
  - [ ] Historical data display: `total_shipments_in_data` → `total_order_volume_in_data`
  - [ ] Any other instances of "shipments" in labels

### Frontend Changes (script.js)
- [ ] Update `displayHistoricalData()` function:
  ```javascript
  // Change this line:
  <div><span class="text-neutral-600">Shipments:</span> <span class="font-medium">${lane_summary.total_shipments_in_data || 'N/A'}</span></div>
  // To:
  <div><span class="text-neutral-600">Order Volume:</span> <span class="font-medium">${lane_summary.total_order_volume_in_data || 'N/A'}</span></div>
  ```

### Backend Verification
- [ ] Ensure API responses use "order_volume" terminology where applicable

## 9. Change "Chat" Labels to "Intelligent Carrier Selection"

### HTML Changes (index.html)
- [ ] Update navigation menu:
  ```html
  <span class="font-medium ml-3 sidebar-text whitespace-nowrap">Intelligent Carrier Selection</span>
  ```
- [ ] Update page title mappings in JavaScript
- [ ] Update any tooltips or help text

### Frontend Changes (script.js)
- [ ] Update `updatePageTitle()` function:
  ```javascript
  const titles = {
    dashboard: { title: 'Dashboard', subtitle: 'RAG Chatbot Management' },
    knowledgeBases: { title: 'Knowledge Bases', subtitle: 'Manage your document collections' },
    chat: { title: 'Intelligent Carrier Selection', subtitle: 'AI-powered carrier recommendations' }
  };
  ```
- [ ] Update any other references to "chat" in user-facing text

## 10. Change "AI Transportation Recommendations" to "Recommendations Powered by AI"

### HTML Changes (index.html)
- [ ] Update card header:
  ```html
  <h3 class="text-lg font-semibold text-neutral-900">Recommendations Powered by AI</h3>
  ```

### Frontend Changes (script.js)
- [ ] Update any JavaScript that sets this title dynamically
- [ ] Update placeholder text:
  ```javascript
  <p class="text-sm mb-2">Recommendations Powered by AI</p>
  ```

## Additional Tasks for Integration

### State Management
- [ ] Create global state object to track:
  ```javascript
  window.shipmentCreationState = {
    selectedOrders: [],
    selectedCarrier: null,
    riqData: null,
    spotData: null,
    isReady: false
  };
  ```

### Event Coordination
- [ ] Implement proper event sequencing:
  1. Chat analysis → RIQ analysis → Spot analysis (auto-date) → Order fetching
  2. Carrier dropdown population → Auto-selection → Button enabling
  3. Order selection → Button state updates

### Error Handling
- [ ] Add comprehensive error handling for all new functionality
- [ ] Add user feedback for each step of the process
- [ ] Add fallback behaviors when APIs fail

### Testing Checklist
- [ ] Test with different lane combinations
- [ ] Test with missing data scenarios
- [ ] Test carrier auto-selection with various RIQ responses
- [ ] Test order table with different numbers of orders
- [ ] Test shipment creation flow end-to-end
- [ ] Test responsive design with new table layout
- [ ] Test modal interactions and state management

### Performance Considerations
- [ ] Optimize sequential API calls to minimize wait times
- [ ] Add loading indicators for each step
- [ ] Implement caching for repeated requests
- [ ] Add debouncing for rapid user interactions

### Accessibility
- [ ] Ensure table is screen reader accessible
- [ ] Add proper ARIA labels for checkboxes and dropdowns
- [ ] Ensure keyboard navigation works for all new elements
- [ ] Test color contrast for new UI elements

### Documentation
- [ ] Update code comments for new functions
- [ ] Document the new workflow sequence
- [ ] Add inline documentation for complex state management
- [ ] Update any existing documentation or README files