/**
 * Historical data API operations
 * Historical data display, data aggregation
 */

import { callDataToolsAPI } from './api-client.js';
import { escapeHtml, showNotification } from './utils.js';

/**
 * Update historical data card
 */
export async function updateHistoricalDataCard(laneInfo, userMessage, response) {
    console.log('📊 Updating historical data card...', laneInfo);
    
    const statusElement = document.getElementById('historical-data-status');
    const contentElement = document.getElementById('historical-data-content');
    
    if (statusElement) {
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800';
        statusElement.textContent = 'Ready';
    }
    
    if (contentElement && laneInfo) {
        contentElement.innerHTML = `
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <h5 class="font-medium text-purple-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-history text-purple-600 mr-2"></i>
                    Historical Data Available
                </h5>
                <div class="text-xs text-purple-700 mb-3">
                    Lane: ${escapeHtml(laneInfo.laneName || 'Unknown')}
                </div>
                <button onclick="viewDetailedHistoricalData()" class="bg-purple-600 text-white px-3 py-1 text-sm rounded-lg hover:bg-purple-700 transition-colors">
                    View Historical Trends
                </button>
            </div>
        `;
    }
}

/**
 * View detailed historical data
 */
export function viewDetailedHistoricalData() {
    console.log('📈 Viewing detailed historical data...');
    showNotification('Historical data analysis starting...', 'info');
}

/**
 * Assign global functions
 */
function assignGlobalFunctions() {
    window.updateHistoricalDataCard = updateHistoricalDataCard;
    window.viewDetailedHistoricalData = viewDetailedHistoricalData;
}

assignGlobalFunctions();
export { assignGlobalFunctions }; 