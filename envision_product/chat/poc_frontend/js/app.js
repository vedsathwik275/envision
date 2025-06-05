/**
 * Main application coordinator
 * Module initialization, DOMContentLoaded handler, application startup sequence
 */

import { checkAPIHealth } from './api-client.js';
import { showNotification } from './utils.js';
import { updateDashboardStats } from './ui-manager.js';
import { loadKnowledgeBases, populateKBSelects } from './knowledge-base.js';
import { setupEventListeners, assignGlobalFunctions, setupGlobalErrorHandling } from './event-handlers.js';

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        console.log('🚀 Initializing RAG Chatbot Application...');
        
        // Load knowledge bases first
        console.log('📚 Loading knowledge bases...');
        await loadKnowledgeBases();
        
        // Update dashboard statistics
        console.log('📊 Updating dashboard statistics...');
        updateDashboardStats();
        
        // Populate knowledge base selects
        console.log('🔄 Populating KB selects...');
        populateKBSelects();
        
        console.log('✅ Application initialized successfully');
        
    } catch (error) {
        console.error('❌ Failed to initialize application:', error);
        showNotification('Failed to initialize application. Please refresh the page.', 'error');
    }
}

/**
 * Setup the application when DOM is loaded
 */
function setupApplication() {
    console.log('🔧 Setting up application...');
    
    // Setup global error handling first
    setupGlobalErrorHandling();
    
    // Assign global functions for HTML onclick handlers
    assignGlobalFunctions();
    
    // Setup all event listeners
    setupEventListeners();
    
    // Check API health
    checkAPIHealth();
    
    console.log('✅ Application setup complete');
}

/**
 * Main application entry point
 */
function main() {
    console.log('🎬 Starting RAG Chatbot Application...');
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setupApplication();
            initializeApp();
        });
    } else {
        // DOM already loaded
        setupApplication();
        initializeApp();
    }
}

// Start the application
main();

// Export for potential external use
export { initializeApp, setupApplication, main }; 