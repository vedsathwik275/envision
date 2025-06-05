/**
 * Spot rate API operations
 * Spot matrix functionality, spot analysis and display
 */

import { callDataToolsAPI } from './api-client.js';
import { escapeHtml, showNotification } from './utils.js';

/**
 * Perform spot analysis
 */
export function performSpotAnalysis() {
    console.log('📈 Performing spot analysis...');
    showNotification('Spot analysis starting...', 'info');
    
    if (window.currentLaneInfo) {
        console.log('Using lane info for spot analysis:', window.currentLaneInfo);
        // Complex spot analysis logic would go here
    } else {
        showNotification('No lane information available for spot analysis', 'warning');
    }
}

/**
 * Toggle spot rate matrix display
 */
export function toggleSpotRateMatrix() {
    console.log('🔄 Toggling spot rate matrix...');
    if (window.openSpotMatrixModal) {
        window.openSpotMatrixModal();
    }
}

/**
 * Fetch spot rate matrix from API
 */
export async function fetchSpotRateMatrix(laneInfo, shipmentDate) {
    console.log('📊 Fetching spot rate matrix...', { laneInfo, shipmentDate });
    
    try {
        const payload = {
            origin_city: laneInfo?.sourceCity || '',
            destination_city: laneInfo?.destinationCity || '',
            shipment_date: shipmentDate || new Date().toISOString().split('T')[0]
        };
        
        const response = await callDataToolsAPI('/spot-rate/matrix', payload);
        return response;
    } catch (error) {
        console.error('Failed to fetch spot rate matrix:', error);
        showNotification('Failed to fetch spot rate matrix', 'error');
        
        // Return placeholder data on error
        return {
            origin_city: laneInfo?.sourceCity || 'Unknown',
            destination_city: laneInfo?.destinationCity || 'Unknown', 
            shipment_date: shipmentDate,
            spot_costs: []
        };
    }
}

/**
 * Update spot API card
 */
export function updateSpotAPICard(laneInfo, userMessage, response) {
    console.log('📋 Updating spot API card...', laneInfo);
    
    const statusElement = document.getElementById('spot-api-status');
    const contentElement = document.getElementById('spot-api-content');
    
    if (statusElement) {
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
        statusElement.textContent = 'Ready';
    }
    
    if (contentElement && laneInfo) {
        contentElement.innerHTML = `
            <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <h5 class="font-medium text-green-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-chart-line text-green-600 mr-2"></i>
                    Spot Analysis Ready
                </h5>
                <div class="grid grid-cols-2 gap-2 text-xs mb-3">
                    ${laneInfo.sourceCity ? `<div><span class="text-green-600">Origin:</span> <span class="font-medium">${escapeHtml(laneInfo.sourceCity)}</span></div>` : ''}
                    ${laneInfo.destinationCity ? `<div><span class="text-green-600">Destination:</span> <span class="font-medium">${escapeHtml(laneInfo.destinationCity)}</span></div>` : ''}
                </div>
                <button onclick="performSpotAnalysis()" class="mt-2 bg-red-500 text-white px-3 py-1 text-sm rounded-lg hover:bg-red-600 transition-colors">
                    Analyze Market
                </button>
                <button onclick="toggleSpotRateMatrix()" class="mt-2 ml-2 bg-blue-500 text-white px-3 py-1 text-sm rounded-lg hover:bg-blue-600 transition-colors">
                    View 7-Day Matrix
                </button>
            </div>
        `;
    }
}

/**
 * Assign global functions for this module
 */
function assignGlobalFunctions() {
    window.performSpotAnalysis = performSpotAnalysis;
    window.toggleSpotRateMatrix = toggleSpotRateMatrix;
    window.fetchSpotRateMatrix = fetchSpotRateMatrix;
    window.updateSpotAPICard = updateSpotAPICard;
}

// Auto-assign global functions when module loads
assignGlobalFunctions();

export { assignGlobalFunctions }; 