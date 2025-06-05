/**
 * Event handler setup and coordination
 * Form submissions, button click handlers, global function assignments
 */

import { setupNavigation, setupSidebar, navigateTo } from './ui-manager.js';
import { 
    openCreateKBModal, 
    closeCreateKBModal, 
    openUploadDocModal, 
    closeUploadDocModal,
    openSpotMatrixModal,
    closeSpotMatrixModal,
    fetchSpotMatrixForModal,
    setupModalEventHandlers 
} from './modal-manager.js';
import { 
    handleCreateKB, 
    handleUploadDocument, 
    uploadToKB, 
    processKB, 
    startChatWithKB, 
    handleDefaultKBChange 
} from './knowledge-base.js';
import { sendMessage, clearChat, handleKBSelection, loadChatView } from './chat-system.js';
import { parseAndUpdateLaneInfo } from './data-parser.js';

// Import all API modules to ensure their global functions are assigned
import './riq-api.js';
import './spot-api.js';
import './historical-api.js';
import './order-api.js';
import './ai-recommendations.js';

/**
 * Setup all event listeners for the application
 */
export function setupEventListeners() {
    // Setup navigation and sidebar
    setupNavigation();
    setupSidebar();
    
    // Setup modal event handlers
    setupModalEventHandlers();

    // Quick actions
    const quickCreateKB = document.getElementById('quick-create-kb');
    const quickUploadDoc = document.getElementById('quick-upload-doc');
    const quickStartChat = document.getElementById('quick-start-chat');
    
    if (quickCreateKB) quickCreateKB.addEventListener('click', () => openCreateKBModal());
    if (quickUploadDoc) quickUploadDoc.addEventListener('click', () => openUploadDocModal());
    if (quickStartChat) quickStartChat.addEventListener('click', () => navigateTo('chat'));

    // Create KB Modal
    const createKBBtn = document.getElementById('create-kb-btn');
    const closeCreateKBModalBtn = document.getElementById('close-create-kb-modal');
    const cancelCreateKB = document.getElementById('cancel-create-kb');
    const createKBForm = document.getElementById('create-kb-form');
    
    if (createKBBtn) createKBBtn.addEventListener('click', () => openCreateKBModal());
    if (closeCreateKBModalBtn) closeCreateKBModalBtn.addEventListener('click', closeCreateKBModal);
    if (cancelCreateKB) cancelCreateKB.addEventListener('click', closeCreateKBModal);
    if (createKBForm) createKBForm.addEventListener('submit', handleCreateKB);

    // Upload Doc Modal
    const closeUploadDocModalBtn = document.getElementById('close-upload-doc-modal');
    const cancelUploadDoc = document.getElementById('cancel-upload-doc');
    const uploadDocForm = document.getElementById('upload-doc-form');
    
    if (closeUploadDocModalBtn) closeUploadDocModalBtn.addEventListener('click', closeUploadDocModal);
    if (cancelUploadDoc) cancelUploadDoc.addEventListener('click', closeUploadDocModal);
    if (uploadDocForm) uploadDocForm.addEventListener('submit', handleUploadDocument);

    // Chat input and send button
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const clearChatBtn = document.getElementById('clear-chat');
    const chatKBSelect = document.getElementById('chat-kb-select');
    
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !chatInput.disabled && chatInput.value.trim()) {
                sendMessage();
            }
        });
    }
    
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (clearChatBtn) clearChatBtn.addEventListener('click', clearChat);
    if (chatKBSelect) chatKBSelect.addEventListener('change', handleKBSelection);

    // Spot Matrix Modal
    const closeSpotMatrixModalBtn = document.getElementById('close-spot-matrix-modal');
    if (closeSpotMatrixModalBtn) {
        closeSpotMatrixModalBtn.addEventListener('click', closeSpotMatrixModal);
    }
}

/**
 * Assign global functions to window object for HTML onclick handlers
 */
export function assignGlobalFunctions() {
    // Knowledge base functions are now auto-assigned by knowledge-base.js module
    // No need to assign them here as they're handled by their own module
    
    // Modal functions
    window.openCreateKBModal = openCreateKBModal;
    window.closeCreateKBModal = closeCreateKBModal;
    window.openUploadDocModal = openUploadDocModal;
    window.closeUploadDocModal = closeUploadDocModal;
    window.openSpotMatrixModal = openSpotMatrixModal;
    window.closeSpotMatrixModal = closeSpotMatrixModal;
    window.fetchSpotMatrixForModal = fetchSpotMatrixForModal;
    
    // Chat functions
    window.sendMessage = sendMessage;
    window.clearChat = clearChat;
    window.loadChatView = loadChatView;
    
    // UI functions
    window.navigateTo = navigateTo;
    
    // Data parsing functions
    window.parseAndUpdateLaneInfo = parseAndUpdateLaneInfo;
    
    // Initialize global state objects that will be populated by API modules
    window.currentLaneInfo = null;
    window.aggregatedRecommendationData = {
        rateInquiry: { hasData: false, data: null },
        spotAnalysis: { hasData: false, data: null },
        historicalData: { hasData: false, data: null },
        orderRelease: { hasData: false, data: null }
    };
    
    // These will be assigned by their respective modules when loaded
    window.knowledgeBases = [];
    window.currentKBId = null;
    window.currentView = 'dashboard';
    
    // Note: All API module functions are now auto-assigned by importing the modules above
    console.log('✅ All global functions assigned successfully');
}

/**
 * Setup functions that will be assigned by other modules when they load
 */
export function setupDeferredGlobalFunctions() {
    // These functions will be assigned by their respective modules
    // when those modules are loaded. This is a placeholder to document
    // what global functions are expected.
    
    // RIQ API functions (will be assigned by riq-api.js)
    // window.handleGetRatesClick
    // window.retrieveRateInquiry
    // window.retrieveRateInquiryComprehensive
    
    // Spot API functions (will be assigned by spot-api.js)
    // window.performSpotAnalysis
    // window.toggleSpotRateMatrix
    // window.fetchSpotRateMatrix
    
    // Order API functions (will be assigned by order-api.js)
    // window.selectOrder
    // window.handleGetOrdersClick
    
    // AI Recommendations functions (will be assigned by ai-recommendations.js)
    // window.handleGenerateRecommendationsClick
    
    // Historical API functions (will be assigned by historical-api.js)
    // window.updateHistoricalDataCard
    // window.viewDetailedHistoricalData
}

/**
 * Handle form submissions globally
 * @param {Event} e - Form submit event
 */
export function handleFormSubmission(e) {
    // Prevent default form submission for all forms
    // Individual handlers will be called by their respective modules
    const form = e.target;
    const formId = form.id;
    
    console.log(`Form submission for: ${formId}`);
    
    // Form-specific handling is delegated to respective modules
    // via the event listeners set up in setupEventListeners()
}

/**
 * Global error handler for unhandled errors
 * @param {ErrorEvent} event - Error event
 */
export function handleGlobalError(event) {
    console.error('Global error:', event.error);
    
    // Show user-friendly error message
    if (window.showNotification) {
        window.showNotification('An unexpected error occurred. Please refresh the page if problems persist.', 'error');
    }
}

/**
 * Setup global error handling
 */
export function setupGlobalErrorHandling() {
    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        if (window.showNotification) {
            window.showNotification('An unexpected error occurred. Please try again.', 'error');
        }
    });
} 