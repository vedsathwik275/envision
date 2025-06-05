/**
 * RIQ API specific functionality
 * Rate inquiry operations, comprehensive RIQ workflow, XML parsing functions, rate result display
 */

import { callDataToolsAPI } from './api-client.js';
import { escapeHtml, parseWeightAndVolume, cleanServiceProviderGid } from './utils.js';
import { showNotification } from './utils.js';

/**
 * Handle get rates click - placeholder for complex functionality
 */
export async function handleGetRatesClick() {
    console.log('🚛 Handling get rates click...');
    showNotification('Rate inquiry feature loading...', 'info');
    
    // This is a placeholder for the complex rate inquiry functionality
    // The full implementation would include all the rate card updates
}

/**
 * Retrieve rate inquiry - placeholder
 */
export async function retrieveRateInquiry() {
    console.log('📊 Retrieving rate inquiry...');
    showNotification('Basic rate inquiry starting...', 'info');
    
    // Placeholder implementation
    if (window.currentLaneInfo) {
        console.log('Using lane info:', window.currentLaneInfo);
        // Complex rate logic would go here
    } else {
        showNotification('No lane information available for rate inquiry', 'warning');
    }
}

/**
 * Retrieve comprehensive rate inquiry
 */
export async function retrieveRateInquiryComprehensive() {
    console.log('🔍 Retrieving comprehensive rate inquiry...');
    showNotification('Comprehensive rate inquiry starting...', 'info');
    
    // Placeholder implementation
    if (window.currentLaneInfo) {
        console.log('Using lane info for comprehensive analysis:', window.currentLaneInfo);
        // Complex comprehensive rate logic would go here
    } else {
        showNotification('No lane information available for comprehensive rate inquiry', 'warning');
    }
}

/**
 * Update rate inquiry card - placeholder
 */
export function updateRateInquiryCard(laneInfo, userMessage, response) {
    console.log('📋 Updating rate inquiry card...', laneInfo);
    
    const statusElement = document.getElementById('rate-inquiry-status');
    const contentElement = document.getElementById('rate-inquiry-content');
    
    if (statusElement) {
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
        statusElement.textContent = 'Ready';
    }
    
    if (contentElement && laneInfo) {
        contentElement.innerHTML = `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <h5 class="font-medium text-blue-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-route text-blue-600 mr-2"></i>
                    Lane Information Detected
                </h5>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    ${laneInfo.sourceCity ? `<div><span class="text-blue-600">Origin:</span> <span class="font-medium">${escapeHtml(laneInfo.sourceCity)}</span></div>` : ''}
                    ${laneInfo.destinationCity ? `<div><span class="text-blue-600">Destination:</span> <span class="font-medium">${escapeHtml(laneInfo.destinationCity)}</span></div>` : ''}
                    ${laneInfo.weight ? `<div><span class="text-blue-600">Weight:</span> <span class="font-medium">${escapeHtml(laneInfo.weight)}</span></div>` : ''}
                    ${laneInfo.volume ? `<div><span class="text-blue-600">Volume:</span> <span class="font-medium">${escapeHtml(laneInfo.volume)}</span></div>` : ''}
                </div>
                <button onclick="window.retrieveRateInquiry()" class="mt-3 px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors">
                    Get Rates
                </button>
                <button onclick="window.retrieveRateInquiryComprehensive()" class="mt-3 ml-2 px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                    Comprehensive Analysis
                </button>
            </div>
        `;
    }
}

/**
 * Clear lane info cards
 */
export function clearLaneInfoCards() {
    const cards = [
        'rate-inquiry-content',
        'spot-api-content', 
        'historical-data-content',
        'order-release-content'
    ];
    
    cards.forEach(cardId => {
        const element = document.getElementById(cardId);
        if (element) {
            element.innerHTML = '';
        }
    });
    
    // Reset status elements
    const statusElements = [
        'rate-inquiry-status',
        'spot-api-status',
        'historical-data-status', 
        'order-release-status'
    ];
    
    statusElements.forEach(statusId => {
        const element = document.getElementById(statusId);
        if (element) {
            element.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-neutral-100 text-neutral-800';
            element.textContent = 'Pending';
        }
    });
}

/**
 * Assign global functions for this module
 */
function assignGlobalFunctions() {
    window.handleGetRatesClick = handleGetRatesClick;
    window.retrieveRateInquiry = retrieveRateInquiry; 
    window.retrieveRateInquiryComprehensive = retrieveRateInquiryComprehensive;
    window.clearLaneInfoCards = clearLaneInfoCards;
    window.updateRateInquiryCard = updateRateInquiryCard;
}

// Auto-assign global functions when module loads
assignGlobalFunctions();

export { assignGlobalFunctions }; 