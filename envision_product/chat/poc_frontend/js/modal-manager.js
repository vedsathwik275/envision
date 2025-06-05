/**
 * All modal-related functionality
 * Modal open/close functions, modal event handlers, spot matrix modal specific functions
 */

import { escapeHtml } from './utils.js';

/**
 * Open create knowledge base modal
 */
export function openCreateKBModal() {
    const createKBModal = document.getElementById('create-kb-modal');
    if (createKBModal) {
        createKBModal.classList.remove('hidden');
    }
}

/**
 * Close create knowledge base modal
 */
export function closeCreateKBModal() {
    const createKBModal = document.getElementById('create-kb-modal');
    if (createKBModal) {
        createKBModal.classList.add('hidden');
    }
}

/**
 * Open upload document modal
 */
export function openUploadDocModal() {
    const uploadDocModal = document.getElementById('upload-doc-modal');
    if (uploadDocModal) {
        uploadDocModal.classList.remove('hidden');
    }
    
    // Populate knowledge base select in the modal
    const uploadKBSelect = document.getElementById('upload-kb-select');
    if (uploadKBSelect && window.knowledgeBases) {
        uploadKBSelect.innerHTML = '<option value="">Select a knowledge base...</option>';
        window.knowledgeBases.forEach(kb => {
            const option = document.createElement('option');
            option.value = kb.id;
            option.textContent = kb.name;
            uploadKBSelect.appendChild(option);
        });
    }
}

/**
 * Close upload document modal
 */
export function closeUploadDocModal() {
    const uploadDocModal = document.getElementById('upload-doc-modal');
    if (uploadDocModal) {
        uploadDocModal.classList.add('hidden');
    }
}

/**
 * Open spot rate matrix modal
 */
export function openSpotMatrixModal() {
    const modal = document.getElementById('spot-matrix-modal');
    const content = document.getElementById('spot-matrix-content');
    
    if (!modal) return;
    
    // Check if we have lane information
    if (window.currentLaneInfo) {
        content.innerHTML = `
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p class="text-lg mb-2">Loading 7-Day Matrix...</p>
                <p class="text-sm text-neutral-400">Preparing spot rate data for ${window.currentLaneInfo.sourceCity} to ${window.currentLaneInfo.destinationCity}</p>
            </div>
        `;
        
        // Fetch data for the modal
        fetchSpotMatrixForModal();
    } else {
        // Show default empty state
        content.innerHTML = `
            <div class="text-center py-12 text-neutral-500">
                <i class="fas fa-table text-4xl mb-4 text-neutral-300"></i>
                <p class="text-lg mb-2">No Lane Information Available</p>
                <p class="text-sm text-neutral-400">Ask about a transportation lane first, then perform spot analysis</p>
            </div>
        `;
    }
    
    modal.classList.remove('hidden');
}

/**
 * Close spot rate matrix modal
 */
export function closeSpotMatrixModal() {
    const modal = document.getElementById('spot-matrix-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Fetch spot matrix data for modal display
 */
export async function fetchSpotMatrixForModal() {
    const content = document.getElementById('spot-matrix-content');
    const laneInfo = window.currentLaneInfo;
    
    if (!laneInfo) {
        content.innerHTML = `
            <div class="text-center py-12 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p class="text-lg mb-2">No Lane Information</p>
                <p class="text-sm">Please analyze a transportation lane first</p>
            </div>
        `;
        return;
    }
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p class="text-lg mb-2">Loading 7-Day Matrix...</p>
            <p class="text-sm text-neutral-400">Fetching spot rate data</p>
        </div>
    `;
    
    try {
        // Get current date or use the date from the input field
        const shipDateInput = document.getElementById('spot-ship-date');
        const shipmentDate = shipDateInput?.value || new Date().toISOString().split('T')[0];
        
        // Call the spot API function to fetch data
        const data = await window.fetchSpotRateMatrix(laneInfo, shipmentDate);
        if (data) {
            displaySpotMatrixInModal(data);
        }
        
    } catch (error) {
        console.error('Failed to fetch spot matrix for modal:', error);
        content.innerHTML = `
            <div class="text-center py-12 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p class="text-lg mb-2">Failed to Load Matrix</p>
                <p class="text-sm text-neutral-400">${escapeHtml(error.message)}</p>
                <button onclick="fetchSpotMatrixForModal()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Try Again
                </button>
            </div>
        `;
    }
}

/**
 * Display spot matrix data in modal
 * @param {Object} data - Spot rate matrix data
 */
export function displaySpotMatrixInModal(data) {
    const content = document.getElementById('spot-matrix-content');
    
    if (!data || !data.spot_costs) {
        content.innerHTML = `
            <div class="text-center py-12 text-neutral-500">
                <i class="fas fa-table text-4xl mb-4 text-neutral-300"></i>
                <p class="text-lg mb-2">No Matrix Data Available</p>
                <p class="text-sm text-neutral-400">Invalid or empty spot rate data</p>
            </div>
        `;
        return;
    }
    
    const { origin_city, origin_state, destination_city, destination_state, shipment_date, spot_costs } = data;
    const laneInfo = window.currentLaneInfo;
    
    // Get all unique dates and sort them
    const allDates = [...new Set(spot_costs.flatMap(carrier => 
        carrier.cost_details.map(detail => detail.ship_date)
    ))].sort();
    
    let matrixHTML = `
        <div class="mb-6">
            <div class="bg-blue-50 rounded-lg p-4 mb-4">
                <h4 class="font-medium text-blue-900 mb-2">Lane Information</h4>
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div><span class="text-blue-600">Origin:</span> <span class="font-medium">${escapeHtml(origin_city || laneInfo?.sourceCity || 'N/A')}</span></div>
                    <div><span class="text-blue-600">Destination:</span> <span class="font-medium">${escapeHtml(destination_city || laneInfo?.destinationCity || 'N/A')}</span></div>
                    <div><span class="text-blue-600">Weight:</span> <span class="font-medium">${escapeHtml(laneInfo?.weight || 'N/A')}</span></div>
                    <div><span class="text-blue-600">Base Date:</span> <span class="font-medium">${shipment_date}</span></div>
                </div>
            </div>
            
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-gray-200 rounded-lg">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Carrier</th>
    `;
    
    // Create column headers for each date
    allDates.forEach(date => {
        const dateObj = new Date(date);
        const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
        const shortDate = dateObj.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' });
        matrixHTML += `<th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">${dayName}<br><span class="text-xs">${shortDate}</span></th>`;
    });
    
    matrixHTML += `
                            <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Rate</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
    `;
    
    // Process each carrier
    spot_costs.forEach((carrierData, index) => {
        const rowClass = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
        
        matrixHTML += `
            <tr class="${rowClass}">
                <td class="px-4 py-3 text-sm font-medium text-gray-900">${escapeHtml(carrierData.carrier)}</td>
        `;
        
        // Create a map of dates to costs for this carrier
        const dateToRateMap = {};
        carrierData.cost_details.forEach(detail => {
            dateToRateMap[detail.ship_date] = parseFloat(detail.total_spot_cost);
        });
        
        let totalRate = 0;
        let validDays = 0;
        
        // For each date column, show the rate or N/A
        allDates.forEach(date => {
            if (dateToRateMap[date]) {
                const rate = dateToRateMap[date];
                totalRate += rate;
                validDays++;
                matrixHTML += `<td class="px-4 py-3 text-sm text-center text-gray-900">$${rate.toFixed(2)}</td>`;
            } else {
                matrixHTML += `<td class="px-4 py-3 text-sm text-center text-gray-400">N/A</td>`;
            }
        });
        
        // Calculate and display average
        const avgRate = validDays > 0 ? (totalRate / validDays) : 0;
        const avgClass = avgRate > 0 ? 'text-blue-600' : 'text-gray-400';
        const avgText = avgRate > 0 ? `$${avgRate.toFixed(2)}` : 'N/A';
        matrixHTML += `<td class="px-4 py-3 text-sm text-center font-medium ${avgClass}">${avgText}</td>`;
        
        matrixHTML += `</tr>`;
    });
    
    matrixHTML += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Add summary statistics
    const allRatesWithDetails = spot_costs.flatMap(carrier => 
        carrier.cost_details.map(detail => ({
            cost: parseFloat(detail.total_spot_cost),
            carrier: carrier.carrier,
            date: detail.ship_date
        }))
    );
    
    if (allRatesWithDetails.length > 0) {
        const minRate = Math.min(...allRatesWithDetails.map(r => r.cost));
        const maxRate = Math.max(...allRatesWithDetails.map(r => r.cost));
        const avgRate = allRatesWithDetails.reduce((sum, r) => sum + r.cost, 0) / allRatesWithDetails.length;
        
        matrixHTML += `
            <div class="mt-6 bg-gray-50 rounded-lg p-4">
                <h5 class="font-medium text-gray-900 mb-3">Matrix Summary</h5>
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                    <div><span class="text-gray-600">Total Carriers:</span> <span class="font-medium">${spot_costs.length}</span></div>
                    <div><span class="text-gray-600">Best Rate:</span> <span class="font-medium text-green-600">$${minRate.toFixed(2)}</span></div>
                    <div><span class="text-gray-600">Highest Rate:</span> <span class="font-medium text-red-600">$${maxRate.toFixed(2)}</span></div>
                    <div><span class="text-gray-600">Market Avg:</span> <span class="font-medium">$${avgRate.toFixed(2)}</span></div>
                </div>
            </div>
        `;
    }
    
    content.innerHTML = matrixHTML;
}

/**
 * Setup order release modal functionality
 */
export function setupOrderReleaseModal() {
    // This function will be called to initialize order release modal
    // Can be extended as needed
}

/**
 * Setup modal backdrop click handlers
 */
export function setupModalEventHandlers() {
    const createKBModal = document.getElementById('create-kb-modal');
    const uploadDocModal = document.getElementById('upload-doc-modal');
    
    // Close modals on backdrop click
    if (createKBModal) {
        createKBModal.addEventListener('click', (e) => {
            if (e.target === createKBModal) closeCreateKBModal();
        });
    }
    
    if (uploadDocModal) {
        uploadDocModal.addEventListener('click', (e) => {
            if (e.target === uploadDocModal) closeUploadDocModal();
        });
    }
    
    // Close spot matrix modal on backdrop click
    const spotMatrixModal = document.getElementById('spot-matrix-modal');
    if (spotMatrixModal) {
        spotMatrixModal.addEventListener('click', (e) => {
            if (e.target === spotMatrixModal) closeSpotMatrixModal();
        });
    }
} 