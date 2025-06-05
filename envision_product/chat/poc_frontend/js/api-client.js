/**
 * Base API client functionality
 * Common API error handling and health check functionality
 */

import { CONFIG } from './config.js';

/**
 * Base API request function
 * @param {string} endpoint - API endpoint (relative to base URL)
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} API response
 */
export async function makeAPIRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API request failed for ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Check API health status
 * @returns {Promise<boolean>} True if API is healthy
 */
export async function checkAPIHealth() {
    try {
        await fetch(`${CONFIG.API_BASE_URL}/health`);
        updateConnectionStatus(true);
        return true;
    } catch (error) {
        console.error('API health check failed:', error);
        updateConnectionStatus(false);
        return false;
    }
}

/**
 * Update connection status display
 * @param {boolean} connected - Connection status
 */
export function updateConnectionStatus(connected) {
    const connectionStatus = document.getElementById('connection-status');
    if (!connectionStatus) return;
    
    if (connected) {
        connectionStatus.innerHTML = '<i class="fas fa-circle text-green-500 mr-2"></i>Connected';
        connectionStatus.className = 'flex items-center text-sm text-neutral-600';
    } else {
        connectionStatus.innerHTML = '<i class="fas fa-circle text-red-500 mr-2"></i>Disconnected';
        connectionStatus.className = 'flex items-center text-sm text-red-600';
    }
}

/**
 * Make request to Data Tools API
 * @param {string} endpoint - API endpoint
 * @param {Object} payload - Request payload
 * @returns {Promise<Object>} API response
 */
export async function callDataToolsAPI(endpoint, payload) {
    try {
        const response = await fetch(`${CONFIG.DATA_TOOLS_API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Data Tools API request failed for ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Make request to RIQ API (backward compatibility)
 * @param {string} endpoint - API endpoint
 * @param {Object} payload - Request payload
 * @returns {Promise<Object>} API response
 */
export async function callRiqAPI(endpoint, payload) {
    return callDataToolsAPI(endpoint, payload);
} 