# TODO List & Implementation Guide

## Project Overview
Implementing three key features for the EnvisionDynamics RAG Chatbot:
1. Grey out processed orders after shipment creation
2. Add loading state in chat window during message submission
3. Clean up chat header to show only connection status

---

## TODO 1: Remove RAG Assistant and Ready text from chat header
**Status**: Done
**Priority**: Low  
**Files**: `index.html`  
**Location**: Lines ~260-270 in chat window header section  

### Current State:
```html
<div class="flex items-center">
    <i class="fas fa-robot text-primary-500 mr-2"></i>
    <h3 class="font-semibold text-neutral-900">RAG Assistant</h3>
</div>
```

### Target State:
- Remove RAG Assistant text and robot icon
- Keep only connection status div (`#connection-status`)
- Maintain proper layout spacing

### Implementation Details:
- Remove the entire div containing robot icon and "RAG Assistant" text
- Update flex layout to properly space remaining elements
- Ensure connection status remains centered/properly positioned

---

## TODO 2: Add chat loading state during message submission
**Status**: Done 
**Priority**: High  
**Files**: `script.js`  
**Location**: `sendMessage()` function (~lines 700-750)  

### Current State:
- Button shows spinner during request
- No visual feedback in chat messages area
- User may think nothing is happening

### Target State:
- Show "Generating Lane Analysis..." message in chat area
- Display loading spinner alongside message
- Remove loading message when response arrives

### Implementation Details:
1. After `addChatMessage()` for user message, add loading message
2. Store reference to loading message element
3. Remove loading message before adding assistant response
4. Style loading message similar to assistant messages but distinct

### Code Changes Needed:
```javascript
// In sendMessage() function after addChatMessage(message, 'user'):
const loadingMessageId = addLoadingMessage();

// Before addChatMessage(response.answer, 'assistant', response):
removeLoadingMessage(loadingMessageId);
```

---

## TODO 3: Add order processing state tracking
**Status**: Done 
**Priority**: High  
**Files**: `script.js`  
**Location**: Global variables section (~lines 20-30)  

### Current State:
- Orders are cleared after shipment creation
- No way to track which orders are being processed
- Orders can be reselected immediately

### Target State:
- Global tracking of processing order IDs
- Helper functions to manage processing state
- Persistent state across UI refreshes

### Implementation Details:
Add global variables and helper functions:
```javascript
// Global state for order processing
window.processingOrders = [];

// Helper functions
function markOrderAsProcessing(orderId)
function isOrderProcessing(orderId)
function markOrdersAsProcessing(orderIds)
```

---

## TODO 4: Modify shipment success flow to mark orders as processing
**Status**: ⏳ Pending  
**Priority**: High  
**Files**: `script.js`  
**Location**: `closeShipmentSuccessModal()` function (~lines 1800-1820)  

### Current State:
```javascript
function closeShipmentSuccessModal() {
    const modal = document.getElementById('shipment-success-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Clear selections after successful shipment creation
    clearShipmentSelections();
    
    console.log('DEBUG: Shipment success modal closed and selections cleared');
}
```

### Target State:
- Mark selected orders as processing before clearing
- Refresh order display to show new state
- Maintain existing functionality

### Implementation Details:
1. Mark `window.selectedOrders` as processing
2. Clear selections after marking
3. Refresh display to show visual changes
4. Add new `refreshOrderDisplay()` helper function

---

## TODO 5: Update order display to show processing state visually
**Status**: ⏳ Pending  
**Priority**: High  
**Files**: `script.js`  
**Location**: `createOrderTableRow()` and `displayUnplannedOrders()` (~lines 1400-1500)  

### Current State:
- All orders appear identical
- All orders can be selected
- No visual indication of processing state

### Target State:
- Processing orders are greyed out (opacity-50)
- Processing orders cannot be selected
- Processing orders show "(Processing)" label
- Processing orders have disabled checkboxes

### Implementation Details:
1. Store orders globally in `displayUnplannedOrders()`
2. Check processing state in `createOrderTableRow()`
3. Apply conditional styling and behavior:
   - Disabled styling for processing orders
   - Remove click handlers for processing orders
   - Disable checkboxes for processing orders
   - Add "(Processing)" text label

### Visual Changes:
```css
/* Processing orders styling */
.opacity-50.bg-gray-50 {
    /* Applied to processing order rows */
}
```

---

## Testing Strategy

### Manual Testing Checklist:
1. **Chat Header Cleanup**:
   - [ ] Verify "RAG Assistant" text is removed
   - [ ] Verify robot icon is removed
   - [ ] Verify connection status still shows "Ready (HTTP)"
   - [ ] Verify layout looks proper

2. **Chat Loading State**:
   - [ ] Submit a chat message
   - [ ] Verify loading message appears immediately
   - [ ] Verify loading message shows spinner
   - [ ] Verify loading message is removed when response arrives
   - [ ] Test with different message types

3. **Order Processing Flow**:
   - [ ] Load orders for a lane
   - [ ] Select multiple orders
   - [ ] Click "Create Shipment"
   - [ ] Complete shipment creation flow
   - [ ] Close success modal
   - [ ] Verify selected orders are greyed out
   - [ ] Verify processed orders show "(Processing)" label
   - [ ] Verify processed orders cannot be selected
   - [ ] Verify processing state persists on refresh

### Edge Cases to Test:
- Empty order selection
- Single order selection
- All orders selected
- Mixed processed/unprocessed orders
- Page refresh with processed orders
- Multiple shipment creations

---

## Dependencies & Considerations

### Browser Compatibility:
- Uses modern JavaScript (ES6+)
- DOM manipulation methods
- No external dependencies for new features

### Performance:
- Global state arrays should be reasonable size
- Order refresh should be efficient
- No impact on existing chat functionality

### Error Handling:
- Handle missing DOM elements gracefully
- Validate order IDs before processing
- Fallback behavior if refresh fails

---

## Rollback Plan

If issues arise, features can be rolled back independently:

1. **Chat Header**: Restore original HTML structure
2. **Chat Loading**: Remove loading message calls from `sendMessage()`
3. **Order Processing**: Remove global processing arrays and restore original `closeShipmentSuccessModal()`

Each TODO can be implemented and tested independently, allowing for incremental rollout if needed.