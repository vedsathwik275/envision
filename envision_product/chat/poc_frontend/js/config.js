/**
 * Configuration constants and API endpoints
 * Global configuration object for the RAG chatbot application
 */

export const CONFIG = {
    // API endpoints
    API_BASE_URL: 'http://localhost:8004/api/v1',
    DATA_TOOLS_API_BASE_URL: 'http://localhost:8006',
    RIQ_API_BASE_URL: 'http://localhost:8006',
    
    // Service provider settings
    SERVICE_PROVIDER: 'BSL',
    
    // Default values
    DEFAULT_LOADING_TEXT: 'Processing...',
    
    // Status colors
    STATUS_COLORS: {
        processing: 'bg-yellow-100 text-yellow-800',
        ready: 'bg-green-100 text-green-800',
        error: 'bg-red-100 text-red-800',
        default: 'bg-neutral-100 text-neutral-800'
    }
};

// Export individual constants for backward compatibility
export const API_BASE_URL = CONFIG.API_BASE_URL;
export const DATA_TOOLS_API_BASE_URL = CONFIG.DATA_TOOLS_API_BASE_URL;
export const RIQ_API_BASE_URL = CONFIG.RIQ_API_BASE_URL;
export const SERVICE_PROVIDER = CONFIG.SERVICE_PROVIDER; 