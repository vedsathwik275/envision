// Configuration
const API_BASE_URL = 'http://localhost:8004/api/v1';
const DATA_TOOLS_API_BASE_URL = 'http://localhost:8006'; // Consolidated Data Tools API (formerly RIQ API)
const RIQ_API_BASE_URL = 'http://localhost:8006'; // Keep for backward compatibility with existing RIQ rate quote calls
const SERVICE_PROVIDER = 'BSL'; // Service provider prefix for order release GIDs
let currentView = 'dashboard';
let knowledgeBases = [];
let currentKBId = null;

// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebarToggleCollapsed = document.getElementById('sidebar-toggle-collapsed');
const sidebarToggleIcon = document.getElementById('sidebar-toggle-icon');
const mainContent = document.getElementById('main-content');
const header = document.getElementById('header');

// Navigation elements
const navLinks = document.querySelectorAll('.nav-link');
const navItems = document.querySelectorAll('.nav-link');

// Page title elements
const pageTitle = document.getElementById('page-title');
const pageSubtitle = document.getElementById('page-subtitle');

// Chat elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatKBSelect = document.getElementById('chat-kb-select');
const connectionStatus = document.getElementById('connection-status');
const clearChatBtn = document.getElementById('clear-chat');

// Modal elements
const createKBModal = document.getElementById('create-kb-modal');
const uploadDocModal = document.getElementById('upload-doc-modal');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkAPIHealth();
});

// Initialize application
async function initializeApp() {
    await loadKnowledgeBases();
    updateDashboardStats();
    populateKBSelects();
}

// Setup navigation
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            const viewName = targetSection === 'knowledge-bases' ? 'knowledgeBases' : targetSection;
            navigateTo(viewName);
        });
    });
}

// Setup sidebar
function setupSidebar() {
    if (!sidebarToggle || !sidebarToggleCollapsed || !sidebar || !sidebarToggleIcon || !mainContent || !header) {
        console.error('Some sidebar elements are missing!');
        return;
    }
    
    // Toggle sidebar between expanded and collapsed (from expanded state button)
    sidebarToggle.addEventListener('click', () => {
        collapseSidebar();
    });
    
    // Toggle sidebar between collapsed and expanded (from collapsed state button)
    sidebarToggleCollapsed.addEventListener('click', () => {
        expandSidebar();
    });
    
    // Initialize sidebar as expanded
    expandSidebar();
}

function expandSidebar() {
    // Update sidebar width
    sidebar.classList.remove('w-16');
    sidebar.classList.add('w-64');
    
    // Show expanded header content and hide collapsed header
    const expandedHeader = document.querySelector('.sidebar-expanded-header');
    const collapsedHeader = document.querySelector('.sidebar-collapsed-header');
    if (expandedHeader) expandedHeader.classList.remove('hidden');
    if (collapsedHeader) collapsedHeader.classList.add('hidden');
    
    // Show text elements in navigation and footer
    const sidebarTexts = document.querySelectorAll('.sidebar-text');
    sidebarTexts.forEach(text => text.classList.remove('hidden'));
    
    // Update main content and header margins
    mainContent.classList.remove('ml-16');
    mainContent.classList.add('ml-64');
    header.classList.remove('left-16');
    header.classList.add('left-64');
}

function collapseSidebar() {
    // Update sidebar width
    sidebar.classList.remove('w-64');
    sidebar.classList.add('w-16');
    
    // Hide expanded header content and show collapsed header
    const expandedHeader = document.querySelector('.sidebar-expanded-header');
    const collapsedHeader = document.querySelector('.sidebar-collapsed-header');
    if (expandedHeader) expandedHeader.classList.add('hidden');
    if (collapsedHeader) collapsedHeader.classList.remove('hidden');
    
    // Hide text elements in navigation and footer
    const sidebarTexts = document.querySelectorAll('.sidebar-text');
    sidebarTexts.forEach(text => text.classList.add('hidden'));
    
    // Update main content and header margins
    mainContent.classList.remove('ml-64');
    mainContent.classList.add('ml-16');
    header.classList.remove('left-64');
    header.classList.add('left-16');
}

// Setup event listeners
function setupEventListeners() {
    // Setup navigation
    setupNavigation();
    
    // Setup sidebar
    setupSidebar();

    // Quick actions
    document.getElementById('quick-create-kb').addEventListener('click', () => openCreateKBModal());
    document.getElementById('quick-upload-doc').addEventListener('click', () => openUploadDocModal());
    document.getElementById('quick-start-chat').addEventListener('click', () => navigateTo('chat'));

    // Create KB Modal
    document.getElementById('create-kb-btn').addEventListener('click', () => openCreateKBModal());
    document.getElementById('close-create-kb-modal').addEventListener('click', closeCreateKBModal);
    document.getElementById('cancel-create-kb').addEventListener('click', closeCreateKBModal);
    document.getElementById('create-kb-form').addEventListener('submit', handleCreateKB);

    // Upload Doc Modal
    document.getElementById('close-upload-doc-modal').addEventListener('click', closeUploadDocModal);
    document.getElementById('cancel-upload-doc').addEventListener('click', closeUploadDocModal);
    document.getElementById('upload-doc-form').addEventListener('submit', handleUploadDocument);

    // Chat input and send button
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !chatInput.disabled && chatInput.value.trim()) {
            sendMessage();
        }
    });
    
    sendBtn.addEventListener('click', sendMessage);
    
    // Clear chat button
    clearChatBtn.addEventListener('click', clearChat);
    
    chatKBSelect.addEventListener('change', handleKBSelection);

    // Close modals on backdrop click
    createKBModal.addEventListener('click', (e) => {
        if (e.target === createKBModal) closeCreateKBModal();
    });
    
    uploadDocModal.addEventListener('click', (e) => {
        if (e.target === uploadDocModal) closeUploadDocModal();
    });
    
    // Spot Matrix Modal
    document.getElementById('close-spot-matrix-modal').addEventListener('click', closeSpotMatrixModal);
}

// Navigation functions
function navigateTo(view) {
    // Update active navigation
    navItems.forEach(item => {
        item.classList.remove('bg-white/20', 'text-white');
        item.classList.add('text-neutral-300');
    });
    
    const activeNav = document.getElementById(`nav-${view === 'knowledgeBases' ? 'knowledge-bases' : view}`);
    if (activeNav) {
        activeNav.classList.remove('text-neutral-300');
        activeNav.classList.add('bg-white/20', 'text-white');
    }

    // Hide all sections
    const sections = document.querySelectorAll('#dashboard, #knowledge-bases, #chat');
    sections.forEach(section => {
        section.classList.add('hidden');
        section.classList.remove('block');
    });
    
    // Show target section
    const targetElement = document.getElementById(view === 'knowledgeBases' ? 'knowledge-bases' : view);
    if (targetElement) {
        targetElement.classList.remove('hidden');
        targetElement.classList.add('block');
        currentView = view;
    }

    // Update page title
    updatePageTitle(view);
    
    // Load data for specific views
    if (view === 'knowledgeBases') {
        loadKnowledgeBasesView();
    } else if (view === 'chat') {
        loadChatView();
    }
}

function updatePageTitle(view) {
    const titles = {
        dashboard: { title: 'Dashboard', subtitle: 'RAG Chatbot Management' },
        knowledgeBases: { title: 'Knowledge Bases', subtitle: 'Manage your document collections' },
        chat: { title: 'Chat', subtitle: 'Ask questions about your documents' }
    };
    
    const config = titles[view] || titles.dashboard;
    pageTitle.textContent = config.title;
    pageSubtitle.textContent = config.subtitle;
}

// API Functions
async function makeAPIRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
        console.error('API request failed:', error);
        showNotification(`API Error: ${error.message}`, 'error');
        throw error;
    }
}

async function checkAPIHealth() {
    try {
        await makeAPIRequest('/health');
        updateConnectionStatus(true);
    } catch (error) {
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (connected) {
        statusIndicator.className = 'w-2 h-2 bg-green-500 rounded-full';
        statusText.textContent = 'API Connected';
    } else {
        statusIndicator.className = 'w-2 h-2 bg-red-500 rounded-full';
        statusText.textContent = 'API Disconnected';
    }
}

// Knowledge Base Functions
async function loadKnowledgeBases() {
    try {
        knowledgeBases = await makeAPIRequest('/knowledge_bases/');
        
        // Clean up default KB if it no longer exists
        const defaultKBId = getDefaultKB();
        if (defaultKBId && !knowledgeBases.find(kb => kb.id === defaultKBId)) {
            clearDefaultKB();
            showNotification('Default knowledge base was removed and has been cleared', 'info');
        }
        
        populateKBSelects();
        updateDashboardStats();
    } catch (error) {
        console.error('Failed to load knowledge bases:', error);
        knowledgeBases = [];
    }
}

function populateKBSelects() {
    const selects = [chatKBSelect, document.getElementById('upload-kb-select')];
    const defaultKBId = getDefaultKB();
    
    selects.forEach(select => {
        if (!select) return;
        
        // Clear existing options except the first one
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Update the default option text based on which select this is
        if (select === chatKBSelect) {
            select.children[0].textContent = "★ All sources";
            select.children[0].value = "";
        }
        
        knowledgeBases.forEach(kb => {
            const option = document.createElement('option');
            option.value = kb.id;
            const isDefault = kb.id === defaultKBId;
            const starPrefix = isDefault ? '★ ' : '';
            
            // For chat select, use cleaner formatting
            if (select === chatKBSelect) {
                option.textContent = `${starPrefix}${kb.name}`;
            } else {
                // For upload select, keep status indicator
                option.textContent = `${starPrefix}${kb.name} (${kb.status})`;
            }
            select.appendChild(option);
        });
        
        // Auto-select default KB in chat dropdown only
        if (select === chatKBSelect && defaultKBId) {
            const defaultKB = knowledgeBases.find(kb => kb.id === defaultKBId);
            if (defaultKB) {
                select.value = defaultKBId;
                // Trigger the selection handler to update the UI
                if (currentView === 'chat') {
                    handleKBSelection();
                }
            }
        }
    });
}

async function loadKnowledgeBasesView() {
    const kbList = document.getElementById('kb-list');
    const kbLoading = document.getElementById('kb-loading');
    const kbEmpty = document.getElementById('kb-empty');
    
    kbLoading.classList.remove('hidden');
    kbList.classList.add('hidden');
    kbEmpty.classList.add('hidden');
    
    try {
        await loadKnowledgeBases();
        
        if (knowledgeBases.length === 0) {
            kbEmpty.classList.remove('hidden');
        } else {
            renderKnowledgeBases();
            kbList.classList.remove('hidden');
        }
    } catch (error) {
        showNotification('Failed to load knowledge bases', 'error');
    } finally {
        kbLoading.classList.add('hidden');
    }
}

function renderKnowledgeBases() {
    const kbList = document.getElementById('kb-list');
    kbList.innerHTML = '';
    
    knowledgeBases.forEach(kb => {
        const kbCard = createKnowledgeBaseCard(kb);
        kbList.appendChild(kbCard);
    });
}

function createKnowledgeBaseCard(kb) {
    const card = document.createElement('div');
    const isDefault = getDefaultKB() === kb.id;
    const defaultBorderClass = isDefault ? 'border-yellow-300 bg-yellow-50' : 'border-neutral-200 bg-white';
    card.className = `border rounded-xl p-6 hover:shadow-md transition-shadow ${defaultBorderClass}`;
    
    const statusColor = getStatusColor(kb.status);
    const defaultBadge = isDefault ? '<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 ml-2"><i class="fas fa-star mr-1"></i>DEFAULT</span>' : '';
    
    card.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex-1">
                <div class="flex items-center">
                    <h4 class="font-semibold text-neutral-900">${escapeHtml(kb.name)}</h4>
                    ${defaultBadge}
                </div>
                <p class="text-sm text-neutral-600 mt-1">${escapeHtml(kb.description || 'No description')}</p>
                <div class="flex items-center mt-3 space-x-4 text-xs text-neutral-500">
                    <span class="inline-flex items-center px-2 py-1 rounded-full ${statusColor}">${kb.status}</span>
                    <span><i class="fas fa-file-alt mr-1"></i>${kb.document_count || 0} documents</span>
                    <span><i class="fas fa-clock mr-1"></i>${formatDate(kb.created_at)}</span>
                </div>
                <div class="flex items-center mt-3">
                    <label class="flex items-center text-sm text-neutral-600 cursor-pointer">
                        <input type="checkbox" 
                               class="default-kb-checkbox mr-2 rounded border-neutral-300 text-yellow-600 focus:ring-yellow-500" 
                               ${isDefault ? 'checked' : ''} 
                               onchange="handleDefaultKBChange('${kb.id}', this)">
                        Set as default knowledge base
                    </label>
                </div>
            </div>
            <div class="flex items-center space-x-2 ml-4">
                <button onclick="uploadToKB('${kb.id}')" class="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors">
                    <i class="fas fa-upload mr-1"></i>Upload
                </button>
                <button onclick="processKB('${kb.id}')" class="px-3 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors" ${kb.status === 'processing' ? 'disabled' : ''}>
                    <i class="fas fa-cog mr-1"></i>Process
                </button>
                <button onclick="startChatWithKB('${kb.id}')" class="px-3 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors" ${kb.status !== 'ready' ? 'disabled' : ''}>
                    <i class="fas fa-comment mr-1"></i>Chat
                </button>
            </div>
        </div>
    `;
    
    return card;
}

function getStatusColor(status) {
    const colors = {
        'new': 'bg-neutral-100 text-neutral-800',
        'needs_processing': 'bg-yellow-100 text-yellow-800',
        'processing': 'bg-yellow-100 text-yellow-800',
        'ready': 'bg-green-100 text-green-800',
        'error': 'bg-red-100 text-red-800'
    };
    return colors[status] || colors.new;
}

// Modal Functions
function openCreateKBModal() {
    createKBModal.classList.remove('hidden');
    document.getElementById('kb-name').focus();
}

function closeCreateKBModal() {
    createKBModal.classList.add('hidden');
    document.getElementById('create-kb-form').reset();
}

function openUploadDocModal() {
    if (knowledgeBases.length === 0) {
        showNotification('Please create a knowledge base first', 'warning');
        return;
    }
    uploadDocModal.classList.remove('hidden');
}

function closeUploadDocModal() {
    document.getElementById('upload-doc-modal').classList.add('hidden');
}

function showLoading(text = 'Processing...') {
    loadingText.textContent = text;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// Form Handlers
async function handleCreateKB(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        showLoading('Creating knowledge base...');
        
        const kbData = {
            name: formData.get('name'),
            description: formData.get('description') || ''
        };
        
        await makeAPIRequest('/knowledge_bases/', {
            method: 'POST',
            body: JSON.stringify(kbData)
        });
        
        showNotification('Knowledge base created successfully!', 'success');
        closeCreateKBModal();
        await loadKnowledgeBases();
        
        if (currentView === 'knowledgeBases') {
            renderKnowledgeBases();
        }
    } catch (error) {
        showNotification(`Failed to create knowledge base: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function handleUploadDocument(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        showLoading('Uploading document...');
        
        const kbId = formData.get('kb_id');
        const file = formData.get('file');
        
        if (!file) {
            throw new Error('Please select a file');
        }
        
        const uploadFormData = new FormData();
        uploadFormData.append('file', file);
        
        await fetch(`${API_BASE_URL}/knowledge_bases/${kbId}/documents`, {
            method: 'POST',
            body: uploadFormData
        });
        
        showNotification('Document uploaded successfully!', 'success');
        closeUploadDocModal();
        await loadKnowledgeBases();
        
        if (currentView === 'knowledgeBases') {
            renderKnowledgeBases();
        }
    } catch (error) {
        showNotification(`Failed to upload document: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Global functions for KB card actions
window.uploadToKB = function(kbId) {
    document.getElementById('upload-kb-select').value = kbId;
    openUploadDocModal();
};

window.processKB = async function(kbId) {
    try {
        showLoading('Processing knowledge base...');
        
        await makeAPIRequest(`/knowledge_bases/${kbId}/process`, {
            method: 'POST',
            body: JSON.stringify({ retriever_type: 'hybrid' })
        });
        
        showNotification('Knowledge base processing started!', 'success');
        await loadKnowledgeBases();
        
        if (currentView === 'knowledgeBases') {
            renderKnowledgeBases();
        }
    } catch (error) {
        showNotification(`Failed to process knowledge base: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
};

window.startChatWithKB = function(kbId) {
    chatKBSelect.value = kbId;
    handleKBSelection();
    navigateTo('chat');
};

window.handleDefaultKBChange = function(kbId, checkbox) {
    if (checkbox.checked) {
        setDefaultKB(kbId);
    } else {
        clearDefaultKB();
    }
}

// Chat Functions
function loadChatView() {
    populateKBSelects();
}

function handleKBSelection() {
    const selectedKBId = chatKBSelect.value;
    const kbStatusElement = document.getElementById('kb-selection-status');
    
    if (selectedKBId) {
        const kb = knowledgeBases.find(k => k.id === selectedKBId);
        if (kb) {
            // Update the inline status indicator next to KB selector
            const statusDot = kbStatusElement.querySelector('.w-2');
            const statusText = kbStatusElement.querySelector('span');
            
            if (kb.status === 'ready') {
                statusDot.className = 'w-2 h-2 bg-green-500 rounded-full mr-2';
                statusText.textContent = 'Ready';
                statusText.className = 'text-sm text-green-600';
            } else {
                statusDot.className = 'w-2 h-2 bg-yellow-500 rounded-full mr-2';
                statusText.textContent = kb.status;
                statusText.className = 'text-sm text-yellow-600';
            }
            
            // Update the dropdown to show selected KB name (without the dropdown arrow text)
            const defaultKBId = getDefaultKB();
            const isDefault = kb.id === defaultKBId;
            const starPrefix = isDefault ? '★ ' : '';
            
            // Update the selected option display
            const selectedOption = chatKBSelect.querySelector(`option[value="${selectedKBId}"]`);
            if (selectedOption) {
                selectedOption.textContent = `${starPrefix}${kb.name}`;
            }
            
            if (kb.status === 'ready') {
                currentKBId = selectedKBId;
                enableChat();
                updateChatConnectionStatus(true);
            } else {
                disableChat(`Knowledge base is ${kb.status}. Please wait for processing to complete.`);
                updateChatConnectionStatus(false);
            }
        }
    } else {
        // Reset status indicator when no KB is selected
        const statusDot = kbStatusElement.querySelector('.w-2');
        const statusText = kbStatusElement.querySelector('span');
        
        statusDot.className = 'w-2 h-2 bg-gray-400 rounded-full mr-2';
        statusText.textContent = 'Ready';
        statusText.className = 'text-sm text-neutral-500';
        
        currentKBId = null;
        disableChat('Please select a knowledge base');
        updateChatConnectionStatus(false);
        
        // Reset the dropdown to show "All sources"
        chatKBSelect.children[0].textContent = "★ All sources";
    }
}

// WebSocket functions removed - using HTTP API instead
// TODO: Implement WebSocket when available

function updateChatConnectionStatus(connected) {
    const statusDot = connectionStatus.querySelector('.w-2');
    const statusText = connectionStatus.querySelector('span');
    
    if (connected) {
        statusDot.className = 'w-2 h-2 bg-green-500 rounded-full mr-2';
        statusText.textContent = 'Ready (HTTP)';
        statusText.className = 'text-green-600';
    } else {
        statusDot.className = 'w-2 h-2 bg-neutral-400 rounded-full mr-2';
        statusText.textContent = 'Not Ready';
        statusText.className = 'text-neutral-500';
    }
}

function enableChat() {
    chatInput.disabled = false;
    sendBtn.disabled = false;
    chatInput.placeholder = 'Ask a question about your documents...';
    
    // Update visual state for the new design
    chatInput.classList.remove('text-neutral-400');
    chatInput.classList.add('text-neutral-900');
}

function disableChat(reason) {
    chatInput.disabled = true;
    sendBtn.disabled = true;
    chatInput.placeholder = reason;
    
    // Update visual state for the new design
    chatInput.classList.remove('text-neutral-900');
    chatInput.classList.add('text-neutral-400');
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !currentKBId) return;
    
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // Disable chat while processing
    enableChat();
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin text-sm"></i>';
    
    try {
        const response = await makeAPIRequest(`/knowledge_bases/${currentKBId}/chat`, {
            method: 'POST',
            body: JSON.stringify({
                query: message
            })
        });
        
        addChatMessage(response.answer, 'assistant', response);
        
        // Parse lane information from the message and update cards
        parseAndUpdateLaneInfo(message, response);
    } catch (error) {
        addChatMessage('Sorry, I encountered an error processing your question. Please try again.', 'assistant');
        showNotification(`Chat error: ${error.message}`, 'error');
    } finally {
        // Re-enable chat
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane text-sm"></i>';
    }
}

function addChatMessage(content, sender, metadata = null) {
    const messagesContainer = chatMessages;
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3';
    
    const isUser = sender === 'user';
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Process content for assistant messages to handle markdown and structure
    let processedContent = content;
    if (!isUser) {
        processedContent = formatRAGResponse(content);
    }
    
    messageDiv.innerHTML = `
        <div class="flex-shrink-0 w-8 h-8 ${isUser ? 'bg-neutral-600' : 'bg-primary-500'} rounded-full flex items-center justify-center">
            <i class="fas ${isUser ? 'fa-user' : 'fa-robot'} text-white text-sm"></i>
        </div>
        <div class="flex-1">
            <div class="${isUser ? 'bg-neutral-600 text-white' : 'bg-neutral-100'} rounded-lg p-4">
                ${isUser ? `<p class="text-white">${escapeHtml(content)}</p>` : processedContent}
            </div>
            <p class="text-xs text-neutral-500 mt-1">${timestamp}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Function to format RAG response content
function formatRAGResponse(content) {
    // Clean up the content first
    let formatted = content.trim();
    
    // Remove the structured data section before formatting (it's only for parsing)
    formatted = formatted.replace(/---STRUCTURED_DATA---[\s\S]*?---END_STRUCTURED_DATA---/gi, '');
    
    // Remove the confidence indicator and extract it (only the FIRST occurrence)
    let confidence = null;
    const confidenceMatch = formatted.match(/🎯\s*\*\*Answer\*\*\s*\(Confidence:\s*(\d+\.?\d*)%\)/);
    if (confidenceMatch) {
        confidence = confidenceMatch[1];
        // Remove only the FIRST occurrence of the confidence header
        formatted = formatted.replace(/🎯\s*\*\*Answer\*\*\s*\(Confidence:\s*(\d+\.?\d*)%\)\s*/, '');
    }
    
    // Remove any duplicate confidence headers that might exist
    formatted = formatted.replace(/🎯\s*\*\*Answer\*\*\s*\(Confidence:\s*(\d+\.?\d*)%\)\s*/g, '');
    
    // Clean up any extra whitespace left from removing the structured data
    formatted = formatted.replace(/\n\s*\n\s*\n/g, '\n\n').trim();
    
    // Split content into sections
    const sections = formatted.split(/📚\s*\*\*Sources\*\*/);
    const mainContent = sections[0].trim();
    const sourcesContent = sections[1] ? sections[1].trim() : '';
    
    let result = '';
    
    // Add confidence badge if present
    if (confidence) {
        result += `
            <div class="mb-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <svg class="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    ${confidence}% Confidence
                </span>
            </div>
        `;
    }
    
    // Process main content
    result += '<div class="prose prose-sm max-w-none">';
    
    // Handle headings (### and ####)
    let processedContent = mainContent.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-gray-900 mt-6 mb-3 first:mt-0">$1</h3>');
    processedContent = processedContent.replace(/^#### (.+)$/gm, '<h4 class="text-base font-medium text-gray-800 mt-4 mb-2">$1</h4>');
    
    // Handle numbered lists with bold labels
    processedContent = processedContent.replace(/^(\d+)\.\s*\*\*([^*]+)\*\*:\s*(.+)$/gm, 
        '<div class="mb-4"><div class="flex"><span class="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 text-sm font-medium rounded-full flex items-center justify-center mr-3 mt-0.5">$1</span><div><p class="font-medium text-gray-900 mb-1">$2</p><p class="text-gray-700">$3</p></div></div></div>');
    
    // Handle bullet points with percentages (like "42.06%: - 31.57%")
    processedContent = processedContent.replace(/^\s*-\s*(\d+\.?\d*%)\s*[:;]\s*(.+)$/gm, 
        '<div class="ml-6 mb-2 flex"><span class="text-gray-400 mr-2">•</span><div><span class="font-medium text-blue-600">$1</span><span class="text-gray-700">: $2</span></div></div>');
    
    // Handle bullet points with bold text and colons
    processedContent = processedContent.replace(/^\s*-\s*\*\*([^*]+)\*\*\s*[:]\s*(.+)$/gm, 
        '<div class="ml-6 mb-2 flex"><span class="text-gray-400 mr-2">•</span><div><span class="font-medium text-gray-800">$1:</span> <span class="text-gray-700">$2</span></div></div>');
    
    // Handle sub-bullet points with dashes and bold text (no colon)
    processedContent = processedContent.replace(/^\s*-\s*\*\*([^*]+)\*\*\s*(.+)$/gm, 
        '<div class="ml-6 mb-2 flex"><span class="text-gray-400 mr-2">•</span><div><span class="font-medium text-gray-800">$1</span> <span class="text-gray-700">$2</span></div></div>');
    
    // Handle regular bullet points
    processedContent = processedContent.replace(/^\s*-\s*(.+)$/gm, 
        '<div class="ml-6 mb-1 flex"><span class="text-gray-400 mr-2">•</span><span class="text-gray-700">$1</span></div>');
    
    // Handle bold text
    processedContent = processedContent.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');
    
    // Handle percentage highlighting
    processedContent = processedContent.replace(/(\d+\.?\d*%)/g, '<span class="font-medium text-blue-600">$1</span>');
    
    // Convert line breaks to paragraphs
    const paragraphs = processedContent.split(/\n\s*\n/);
    processedContent = paragraphs.map(p => {
        if (p.trim() && !p.includes('<div') && !p.includes('<h3')) {
            return `<p class="mb-3 text-gray-700 leading-relaxed">${p.trim()}</p>`;
        }
        return p;
    }).join('');
    
    result += processedContent;
    result += '</div>';
    
    // // Handle sources section if present
    // if (sourcesContent) {
    //     result += `
    //         <div class="mt-6 pt-4 border-t border-gray-200">
    //             <h4 class="text-sm font-medium text-gray-900 mb-3">Sources</h4>
    //             <div class="space-y-2">
    //     `;
        
    //     // Parse individual sources
    //     const sourceLines = sourcesContent.split('\n').filter(line => line.trim());
    //     let currentSource = '';
    //     let sourceNumber = 0;
        
    //     for (const line of sourceLines) {
    //         if (/^\s*\d+\./.test(line)) {
    //             if (currentSource) {
    //                 // Close previous source
    //                 result += '</div></div>';
    //             }
    //             sourceNumber++;
    //             const sourceMatch = line.match(/^\s*\d+\.\s*(.+)$/);
    //             if (sourceMatch) {
    //                 currentSource = sourceMatch[1];
    //                 result += `
    //                     <div class="bg-gray-50 rounded-lg p-3">
    //                         <div class="flex items-start">
    //                             <span class="flex-shrink-0 w-5 h-5 bg-gray-200 text-gray-700 text-xs font-medium rounded flex items-center justify-center mr-2 mt-0.5">${sourceNumber}</span>
    //                             <div class="min-w-0 flex-1">
    //                                 <p class="text-sm text-gray-700 font-medium">${currentSource}</p>
    //                 `;
    //             }
    //         } else if (line.includes('└─')) {
    //             const detailMatch = line.match(/└─\s*(.+)$/);
    //             if (detailMatch) {
    //                 result += `<p class="text-xs text-gray-500 font-mono mt-1 bg-gray-100 rounded px-2 py-1">${detailMatch[1]}</p>`;
    //             }
    //         }
    //     }
        
    //     if (currentSource) {
    //         result += '</div></div>';
    //     }
        
    //     result += '</div></div>';
    // }
    
    return result;
}

// Function to format sources properly
function formatSources(sources) {
    if (!sources || sources.length === 0) return '';
    
    let sourcesHtml = '<div class="mt-4 pt-4 border-t border-neutral-200"><h4 class="font-semibold text-neutral-900 mb-3"><i class="fas fa-book mr-2 text-blue-500"></i>Sources</h4><div class="space-y-2">';
    
    sources.forEach((source, index) => {
        // Handle both string sources and object sources
        let sourceText = '';
        if (typeof source === 'string') {
            sourceText = source;
        } else if (source && typeof source === 'object') {
            // Extract meaningful information from object
            sourceText = source.content || source.text || source.document || JSON.stringify(source);
        }
        
        sourcesHtml += `
            <div class="bg-neutral-50 rounded-lg p-3 border-l-4 border-blue-500">
                <div class="flex items-start">
                    <span class="inline-flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-800 text-xs font-medium rounded-full mr-3 mt-0.5">${index + 1}</span>
                    <div class="flex-1">
                        <p class="text-sm text-neutral-700 break-words">${escapeHtml(sourceText)}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    sourcesHtml += '</div></div>';
    return sourcesHtml;
}

function clearChat() {
    const welcomeMessage = chatMessages.querySelector('.flex.items-start.space-x-3');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage.cloneNode(true));
    }
    
    // Clear lane information cards
    clearLaneInfoCards();
    
    // Clear global variables
    window.currentLaneInfo = null;
    
    // Reset AI recommendations to initial state
    resetAIRecommendationsPanel();
}

// Function to clear lane information cards
function clearLaneInfoCards() {
    // Clear Rate Inquiry Card
    const rateInquiryStatus = document.getElementById('rate-inquiry-status');
    const rateInquiryContent = document.getElementById('rate-inquiry-content');
    
    if (rateInquiryStatus && rateInquiryContent) {
        rateInquiryStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        rateInquiryStatus.textContent = 'Ready for API Call';
        
        rateInquiryContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-search text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about lane rates to see parsed information here</p>
                <p class="text-sm mt-2">Example: "What's the best rate from Los Angeles to Chicago?"</p>
            </div>
        `;
    }

    // Clear Spot API Analysis Card
    const spotApiStatus = document.getElementById('spot-api-status');
    const spotApiContent = document.getElementById('spot-api-content');
    
    if (spotApiStatus && spotApiContent) {
        spotApiStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        spotApiStatus.textContent = 'No data';
        
        spotApiContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-analytics text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about carrier performance or spot rates to see analysis here</p>
                <p class="text-sm mt-2">Example: "Show carrier performance for Dallas to Miami"</p>
            </div>
        `;
    }

    // Clear Historical Data Card
    const historicalStatus = document.getElementById('historical-lane-status');
    const historicalContent = document.getElementById('historical-data-content');
    
    if (historicalStatus) {
        historicalStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        historicalStatus.textContent = 'No data';
    }
    
    if (historicalContent) {
        historicalContent.innerHTML = `
            <div class="text-center py-0 text-neutral-500">
                <i class="fas fa-database text-2xl mb-4 text-neutral-300"></i>
                <p>Ask about transportation routes to see historical data</p>
                <p class="text-sm mt-2">Example: "Show me rates from Chicago to Miami"</p>
            </div>
        `;
    }

    // Clear Order Release Card
    const orderReleaseStatus = document.getElementById('order-release-status');
    const orderReleaseContent = document.getElementById('order-release-content');
    
    if (orderReleaseStatus && orderReleaseContent) {
        orderReleaseStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        orderReleaseStatus.textContent = 'No data';
        
        orderReleaseContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-truck text-4xl mb-4 text-neutral-300"></i>
                <p>Ask about lane orders to see unplanned order releases</p>
                <p class="text-sm mt-2">Example: "Show me orders from Atlanta to Miami"</p>
            </div>
        `;
    }
}

// Function to reset AI recommendations panel to initial state
function resetAIRecommendationsPanel() {
    // Reset aggregated data
    window.aggregatedRecommendationData = {
        riq_data: null,
        spot_data: null,
        historical_data: null,
        chat_insights: null
    };
    
    // Reset data collection status (removed order_data)
    Object.keys(dataCollectionStatus).forEach(key => {
        if (key !== 'order_data') { // Skip order_data since we're removing it
            dataCollectionStatus[key] = false;
        }
    });
    
    // Remove order_data from dataCollectionStatus if it exists
    if ('order_data' in dataCollectionStatus) {
        delete dataCollectionStatus.order_data;
    }
    
    // Reset AI recommendations status and content
    const aiStatus = document.getElementById('ai-recommendations-status');
    const aiContent = document.getElementById('ai-recommendations-content');
    const generateBtn = document.getElementById('generate-recommendations-btn');
    
    if (aiStatus) {
        aiStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        aiStatus.textContent = 'Awaiting Data';
    }
    
    if (generateBtn) {
        generateBtn.classList.add('hidden');
    }
    
    if (aiContent) {
        aiContent.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-lightbulb text-4xl mb-4 text-neutral-300"></i>
                <p class="text-sm mb-2">AI-Powered Transportation Recommendations</p>
                <p class="text-xs text-neutral-400">Gather transportation data from multiple sources to unlock intelligent recommendations</p>
                <div class="mt-6 max-w-md mx-auto">
                    <div class="text-xs text-neutral-600 mb-2">Data Collection Progress</div>
                    <div class="space-y-2">
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="riq-data-indicator"></i>
                                RIQ Rate Analysis
                            </span>
                            <span class="text-neutral-400" id="riq-data-status">Not Available</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="spot-data-indicator"></i>
                                Spot Rate Matrix
                            </span>
                            <span class="text-neutral-400" id="spot-data-status">Not Available</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="historical-data-indicator"></i>
                                Historical Lane Data
                            </span>
                            <span class="text-neutral-400" id="historical-data-status">Not Available</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="chat-insights-indicator"></i>
                                Chat-Parsed Insights
                            </span>
                            <span class="text-neutral-400" id="chat-insights-status">Not Available</span>
                        </div>
                    </div>
                    <div class="mt-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div id="data-collection-progress" class="bg-indigo-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                        </div>
                        <div class="text-xs text-neutral-500 mt-1" id="data-collection-summary">0 of 4 data sources collected</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Update data collection indicators
    updateDataCollectionIndicators();
}

// Dashboard Functions
function updateDashboardStats() {
    document.getElementById('kb-count').textContent = knowledgeBases.length;
    
    const totalDocs = knowledgeBases.reduce((sum, kb) => sum + (kb.document_count || 0), 0);
    document.getElementById('doc-count').textContent = totalDocs;
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    try {
        return new Date(dateString).toLocaleDateString();
    } catch {
        return 'Unknown';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
    
    const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white'
    };
    
    notification.className += ` ${colors[type] || colors.info}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

// Lane Information Parsing Functions
function parseAndUpdateLaneInfo(userMessage, response) {
    const laneInfo = parseLaneInformationFromResponse(response.answer);
    
    // Store lane info globally for RIQ API access
    window.currentLaneInfo = laneInfo; // Potentially use this for historical data too
    
    // Check if we have performance analysis data or basic lane info
    const hasSufficientLaneInfo = laneInfo.sourceCity && laneInfo.destinationCity;
    
    if (hasSufficientLaneInfo) { // Changed condition to be more general for all cards
        // Update cards with parsed performance data
        updateRateInquiryCard(laneInfo, userMessage, response);
        updateSpotAPICard(laneInfo, userMessage, response);
        updateHistoricalDataCard(laneInfo, userMessage, response); // NEW: Call historical data card update
        updateOrderReleaseCard(laneInfo, userMessage, response); // NEW: Call order release card update
    } else {
        console.warn("Insufficient lane information to update contextual cards.", laneInfo);
        // Optionally, clear cards or show a generic message if not enough info
        // clearLaneInfoCards(); // Or a more specific clearing if needed
    }
}

function parseLaneInformationFromResponse(answer) {
    const laneInfo = {
        sourceCity: null,
        destinationCity: null,
        state: null,
        zipCode: null,
        weight: null,
        volume: null,
        equipmentType: null,
        serviceType: null,
        carrierName: null,
        requestType: null,
        bestCarrier: null,
        bestPerformance: null,
        worstCarrier: null,
        worstPerformance: null,
        laneName: null
    };
    
    // Look for the structured data section
    const structuredDataMatch = answer.match(/---STRUCTURED_DATA---([\s\S]*?)---END_STRUCTURED_DATA---/i);
    
    if (structuredDataMatch) {
        const structuredData = structuredDataMatch[1];
        
        // Parse each field from the structured data
        const laneMatch = structuredData.match(/LANE:\s*(.+)/i);
        if (laneMatch && laneMatch[1].trim() !== 'N/A') {
            laneInfo.laneName = laneMatch[1].trim();
            // Extract source and destination from lane
            const laneParts = laneInfo.laneName.split(' to ');
            if (laneParts.length === 2) {
                laneInfo.sourceCity = laneParts[0].trim();
                laneInfo.destinationCity = laneParts[1].trim();
            }
        }
        
        const bestCarrierMatch = structuredData.match(/BEST_CARRIER:\s*(.+)/i);
        if (bestCarrierMatch && bestCarrierMatch[1].trim() !== 'N/A') {
            laneInfo.bestCarrier = bestCarrierMatch[1].trim();
        }
        
        const bestPerformanceMatch = structuredData.match(/BEST_PERFORMANCE:\s*(.+)/i);
        if (bestPerformanceMatch && bestPerformanceMatch[1].trim() !== 'N/A') {
            laneInfo.bestPerformance = bestPerformanceMatch[1].trim();
        }
        
        const worstCarrierMatch = structuredData.match(/WORST_CARRIER:\s*(.+)/i);
        if (worstCarrierMatch && worstCarrierMatch[1].trim() !== 'N/A') {
            laneInfo.worstCarrier = worstCarrierMatch[1].trim();
        }
        
        const worstPerformanceMatch = structuredData.match(/WORST_PERFORMANCE:\s*(.+)/i);
        if (worstPerformanceMatch && worstPerformanceMatch[1].trim() !== 'N/A') {
            laneInfo.worstPerformance = worstPerformanceMatch[1].trim();
        }
        
        const orderWeightMatch = structuredData.match(/ORDER_WEIGHT:\s*(.+)/i);
        if (orderWeightMatch && orderWeightMatch[1].trim() !== 'N/A') {
            laneInfo.weight = orderWeightMatch[1].trim();
        }
        
        const orderVolumeMatch = structuredData.match(/ORDER_VOLUME:\s*(.+)/i);
        if (orderVolumeMatch && orderVolumeMatch[1].trim() !== 'N/A') {
            laneInfo.volume = orderVolumeMatch[1].trim();
        }
        
        console.log('Parsed structured data:', {
            lane: laneInfo.laneName,
            bestCarrier: laneInfo.bestCarrier,
            bestPerformance: laneInfo.bestPerformance,
            worstCarrier: laneInfo.worstCarrier,
            worstPerformance: laneInfo.worstPerformance,
            weight: laneInfo.weight,
            volume: laneInfo.volume
        });
        
        return laneInfo;
    }
    
    // Fallback: If no structured data found, try the old regex patterns as backup
    console.log('No structured data found, trying fallback parsing...');
    
    // Parse Best Performance Analysis section - more flexible patterns
    let bestPerformanceMatch = answer.match(/Best Performance Analysis[^]*?(?:best predicted performance|best.*?performance)\s+is\s+(\d+\.?\d*%)\s+for carrier\s+([A-Z\s&.-]+?)\s+on.*?([A-Z\s]+?)\s+to\s+([A-Z\s]+?)\s+lane/i);
    if (!bestPerformanceMatch) {
        // Try alternative pattern
        bestPerformanceMatch = answer.match(/(?:best|highest).*?performance.*?(\d+\.?\d*%)[^]*?carrier[^]*?([A-Z\s&.-]+?)[^]*?([A-Z\s]+?)\s+to\s+([A-Z\s]+?)/i);
    }
    if (bestPerformanceMatch) {
        laneInfo.bestPerformance = bestPerformanceMatch[1];
        laneInfo.bestCarrier = bestPerformanceMatch[2].trim();
        laneInfo.sourceCity = cleanCityName(bestPerformanceMatch[3]);
        laneInfo.destinationCity = cleanCityName(bestPerformanceMatch[4]);
    }
    
    // Parse Worst Performance Analysis section - more flexible patterns
    let worstPerformanceMatch = answer.match(/Worst Performance Analysis[^]*?(?:worst predicted performance|worst.*?performance)\s+is\s+(\d+\.?\d*%)\s+for carrier\s+([A-Z\s&.-]+?)\s+on.*?([A-Z\s]+?)\s+to\s+([A-Z\s]+?)\s+lane/i);
    if (!worstPerformanceMatch) {
        // Try alternative pattern
        worstPerformanceMatch = answer.match(/(?:worst|lowest).*?performance.*?(\d+\.?\d*%)[^]*?carrier[^]*?([A-Z\s&.-]+?)[^]*?([A-Z\s]+?)\s+to\s+([A-Z\s]+?)/i);
    }
    if (worstPerformanceMatch) {
        laneInfo.worstPerformance = worstPerformanceMatch[1];
        laneInfo.worstCarrier = worstPerformanceMatch[2].trim();
        // Use the lane info from worst performance if best performance didn't provide it
        if (!laneInfo.sourceCity) {
            laneInfo.sourceCity = cleanCityName(worstPerformanceMatch[3]);
        }
        if (!laneInfo.destinationCity) {
            laneInfo.destinationCity = cleanCityName(worstPerformanceMatch[4]);
        }
    }
    
    // Create lane name if we have source and destination
    if (laneInfo.sourceCity && laneInfo.destinationCity) {
        laneInfo.laneName = `${laneInfo.sourceCity} to ${laneInfo.destinationCity}`;
    }
    
    // Parse cities (from X to Y, X-Y, between X and Y) - fallback if performance sections don't have them
    if (!laneInfo.sourceCity || !laneInfo.destinationCity) {
        const cityPatterns = [
            /from\s+([a-zA-Z\s,]+?)\s+to\s+([a-zA-Z\s,]+?)(?:\s|$|[.?!,])/i,
            /between\s+([a-zA-Z\s,]+?)\s+and\s+([a-zA-Z\s,]+?)(?:\s|$|[.?!,])/i,
            /([a-zA-Z\s,]+?)\s*[-–—]\s*([a-zA-Z\s,]+?)(?:\s|$|[.?!,])/i,
            /lane\s+([a-zA-Z\s,]+?)\s+to\s+([a-zA-Z\s,]+?)(?:\s|$|[.?!,])/i,
            /shipping\s+from\s+([a-zA-Z\s,]+?)\s+to\s+([a-zA-Z\s,]+?)(?:\s|$|[.?!,])/i,
            /transport\s+from\s+([a-zA-Z\s,]+?)\s+to\s+([a-zA-Z\s,]+?)(?:\s|$|[.?!,])/i,
            /([a-zA-Z\s,]+?)\s+to\s+([a-zA-Z\s,]+?)(?:\s+lane|\s+route|\s+corridor)(?:\s|$|[.?!,])/i
        ];
        
        for (const pattern of cityPatterns) {
            const match = answer.match(pattern);
            if (match) {
                if (!laneInfo.sourceCity) laneInfo.sourceCity = cleanCityName(match[1]);
                if (!laneInfo.destinationCity) laneInfo.destinationCity = cleanCityName(match[2]);
                break;
            }
        }
    }
    
    // Additional city parsing for specific formats like "Elwood to Miami"
    if (!laneInfo.sourceCity && !laneInfo.destinationCity) {
        const simplePattern = /\b([A-Z][a-zA-Z\s]{2,})\s+to\s+([A-Z][a-zA-Z\s]{2,})\b/;
        const simpleMatch = answer.match(simplePattern);
        if (simpleMatch) {
            laneInfo.sourceCity = cleanCityName(simpleMatch[1]);
            laneInfo.destinationCity = cleanCityName(simpleMatch[2]);
        }
    }
    
    // Parse weight (lbs, pounds, kg, tons)
    const weightMatch = answer.match(/(\d+(?:,\d{3})*(?:\.\d+)?)\s*(lbs?|pounds?|kg|tons?|#)/i);
    if (weightMatch) {
        laneInfo.weight = `${weightMatch[1]} ${weightMatch[2] === '#' ? 'lbs' : weightMatch[2]}`;
    }
    
    // Parse volume (cuft, cubic feet, cbm)
    const volumeMatch = answer.match(/(\d+(?:,\d{3})*(?:\.\d+)?)\s*(cuft|cubic\s*feet?|cbm|cubic\s*meters?|ft3|m3)/i);
    if (volumeMatch) {
        laneInfo.volume = `${volumeMatch[1]} ${volumeMatch[2]}`;
    }
    
    // Parse zip codes
    const zipMatch = answer.match(/\b(\d{5}(?:-\d{4})?)\b/);
    if (zipMatch) {
        laneInfo.zipCode = zipMatch[1];
    }
    
    // Parse states (both abbreviations and full names)
    const stateMatch = answer.match(/\b([A-Z]{2})\b/);
    if (stateMatch) {
        laneInfo.state = stateMatch[1];
    }
    
    // Parse equipment types with more variations
    const equipmentPatterns = [
        { pattern: /dry\s*van/i, name: 'Dry Van' },
        { pattern: /flatbed/i, name: 'Flatbed' },
        { pattern: /refrigerated|reefer/i, name: 'Refrigerated' },
        { pattern: /tanker/i, name: 'Tanker' },
        { pattern: /ltl|less\s*than\s*truckload/i, name: 'LTL' },
        { pattern: /ftl|full\s*truck\s*load/i, name: 'FTL' },
        { pattern: /container|intermodal/i, name: 'Container' },
        { pattern: /step\s*deck/i, name: 'Step Deck' },
        { pattern: /lowboy/i, name: 'Lowboy' },
        { pattern: /van/i, name: 'Van' }
    ];
    
    for (const { pattern, name } of equipmentPatterns) {
        if (pattern.test(answer)) {
            laneInfo.equipmentType = name;
            break;
        }
    }
    
    // Parse carrier names (enhanced detection for RIQ)
    const carrierPatterns = [
        // Direct carrier mentions
        /carrier\s+([a-zA-Z\s&.-]+?)(?:\s|$|[.?!,])/i,
        /with\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+carrier|\s+trucking|\s+logistics)(?:\s|$|[.?!,])/i,
        /([A-Z][A-Z\s&.-]+?)\s+(?:carrier|trucking|logistics)(?:\s|$|[.?!,])/i,
        
        // Common carrier abbreviations and names
        /\b(ODFL|Old Dominion|UPS|FedEx|YRC|XPO|JB Hunt|Werner|Schneider|Swift|Knight|Landstar|Estes|ABF|Saia|R\+L|TForce|Ryder|Penske)\b/i,
        
        // Carrier mentioned in context
        /operated?\s+by\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|$|[.?!,])/i,
        /([A-Z][a-zA-Z\s&.-]+?)\s+operates?\s+(?:on\s+)?(?:this\s+)?(?:the\s+)?lane/i,
        /lane\s+(?:operated\s+)?(?:by\s+)?([A-Z][a-zA-Z\s&.-]+?)(?:\s|$|[.?!,])/i,
        
        // From RAG responses mentioning carriers
        /carrier\s+responsible\s+.*?is\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|$|[.?!,])/i,
        /The\s+carrier\s+.*?is\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s|$|[.?!,])/i,
        
        // Carrier info patterns
        /\*\*([A-Z][A-Z\s&.-]+?)\*\*\s+(?:\([^)]+\))?\s*(?:operates|is\s+the\s+carrier|handles)/i
    ];
    
    for (const pattern of carrierPatterns) {
        const match = answer.match(pattern);
        if (match) {
            let carrierName = match[1].trim();
            
            // Clean up common carrier name variations
            if (carrierName.toUpperCase() === 'ODFL') {
                carrierName = 'ODFL (Old Dominion Freight Line)';
            } else if (carrierName.toLowerCase().includes('old dominion')) {
                carrierName = 'ODFL (Old Dominion Freight Line)';
            }
            
            laneInfo.carrierName = carrierName;
            break;
        }
    }
    
    // Parse service types
    const servicePatterns = [
        { pattern: /expedited|rush|urgent/i, name: 'Expedited' },
        { pattern: /standard|regular/i, name: 'Standard' },
        { pattern: /economy/i, name: 'Economy' },
        { pattern: /same\s*day/i, name: 'Same Day' },
        { pattern: /next\s*day/i, name: 'Next Day' },
        { pattern: /ground/i, name: 'Ground' }
    ];
    
    for (const { pattern, name } of servicePatterns) {
        if (pattern.test(answer)) {
            laneInfo.serviceType = name;
            break;
        }
    }
    
    return laneInfo;
}

function cleanCityName(cityName) {
    return cityName.trim()
        .replace(/,$/, '')  // Remove trailing comma
        .replace(/\s+/g, ' ')  // Normalize whitespace
        .split(',')[0]  // Take only the city part if state is included
        .trim();
}

function isRateInquiryPrompt(message) {
    const rateKeywords = [
        'rate', 'rates', 'price', 'pricing', 'cost', 'costs', 'quote', 'quotes',
        'freight', 'shipping', 'transport', 'shipment', 'best rate', 'cheapest',
        'how much', 'what does it cost', 'rate inquiry'
    ];
    
    return rateKeywords.some(keyword => 
        message.toLowerCase().includes(keyword.toLowerCase())
    );
}

function isSpotAPIPrompt(message) {
    const spotKeywords = [
        'spot', 'carrier performance', 'performance', 'analytics', 'analysis',
        'market', 'trends', 'spot rate', 'spot market', 'capacity', 'utilization',
        'on-time', 'delivery', 'reliability', 'metrics', 'kpi'
    ];
    
    return spotKeywords.some(keyword => 
        message.toLowerCase().includes(keyword.toLowerCase())
    );
}

function updateRateInquiryCard(laneInfo, userMessage, response) {
    const statusElement = document.getElementById('rate-inquiry-status');
    const contentElement = document.getElementById('rate-inquiry-content');
    
    // Update status to show loading
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
    statusElement.textContent = 'Analyzing Rates...';
    
    // Build content with analysis parameters (optimized for fixed height)
    let content = `
        <div class="bg-blue-50 rounded-lg p-3">
            <h4 class="font-medium text-blue-900 mb-2 flex items-center text-sm">
                <i class="fas fa-shipping-fast text-blue-600 mr-2"></i>
                Rate Inquiry Parameters
            </h4>
            <div class="grid grid-cols-2 gap-2 text-xs">
    `;
    
    if (laneInfo.sourceCity) {
        content += `<div><span class="text-neutral-600">Origin:</span> <span class="font-medium">${laneInfo.sourceCity}</span></div>`;
    }
    if (laneInfo.destinationCity) {
        content += `<div><span class="text-neutral-600">Destination:</span> <span class="font-medium">${laneInfo.destinationCity}</span></div>`;
    }
    if (laneInfo.laneName) {
        content += `<div class="col-span-2"><span class="text-neutral-600">Route:</span> <span class="font-medium">${laneInfo.laneName}</span></div>`;
    }
    if (laneInfo.equipmentType) {
        content += `<div><span class="text-neutral-600">Equipment:</span> <span class="font-medium">${laneInfo.equipmentType}</span></div>`;
    }
    if (laneInfo.serviceType) {
        content += `<div><span class="text-neutral-600">Service:</span> <span class="font-medium">${laneInfo.serviceType}</span></div>`;
    }
    if (laneInfo.carrierName) {
        content += `<div class="col-span-2"><span class="text-neutral-600">Carrier:</span> <span class="font-medium">${laneInfo.carrierName}</span></div>`;
    }
    if (laneInfo.weight) {
        content += `<div><span class="text-neutral-600">Weight:</span> <span class="font-medium">${laneInfo.weight}</span></div>`;
    }
    if (laneInfo.volume) {
        content += `<div><span class="text-neutral-600">Volume:</span> <span class="font-medium">${laneInfo.volume}</span></div>`;
    }
    
    content += `<div><span class="text-neutral-600">Type:</span> <span class="font-medium">Rate Inquiry</span></div>`;
    content += `<div><span class="text-neutral-600">Status:</span> <span class="font-medium text-blue-600">Processing...</span></div>`;
    
    content += `
            </div>
        </div>
        <div class="mt-3 text-center">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <p class="text-xs text-blue-600">Fetching rate data automatically...</p>
        </div>
    `;
    
    contentElement.innerHTML = content;
    
    // Auto-trigger RIQ rate analysis
    setTimeout(async () => {
        try {
            if (window.retrieveRateInquiryComprehensive) {
                await window.retrieveRateInquiryComprehensive();
            } else {
                throw new Error('Rate inquiry function not available');
            }
        } catch (error) {
            console.error('Auto-run RIQ analysis failed:', error);
            
            // Show error state with retry option
            statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
            statusElement.textContent = 'Analysis Failed';
            
            contentElement.innerHTML = `
                <div class="bg-red-50 rounded-lg p-3">
                    <div class="text-center">
                        <i class="fas fa-exclamation-triangle text-red-500 text-2xl mb-2"></i>
                        <p class="text-sm text-red-700 mb-3">Failed to fetch rate data automatically</p>
                        <p class="text-xs text-red-600 mb-3">${escapeHtml(error.message)}</p>
                        <button onclick="window.retrieveRateInquiryComprehensive()" class="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors">
                            <i class="fas fa-retry mr-1"></i>
                            Retry Analysis
                        </button>
                    </div>
                </div>
            `;
        }
    }, 1000); // 1 second delay to allow UI to update
}

function updateSpotAPICard(laneInfo, userMessage, response) {
    const statusElement = document.getElementById('spot-api-status');
    const contentElement = document.getElementById('spot-api-content');
    
    // Update status
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
    statusElement.textContent = 'Ready for Analysis';
    
    // Build content with analysis parameters (simplified since controls are now in header)
    let content = `
        <div class="bg-green-50 rounded-lg p-4">
            <h4 class="font-medium text-green-900 mb-3 flex items-center">
                <i class="fas fa-analytics text-green-600 mr-2"></i>
                Spot API Parameters
            </h4>
            <div class="grid grid-cols-2 gap-3 text-sm">
    `;
    
    if (laneInfo.sourceCity) {
        content += `<div><span class="text-neutral-600">Origin:</span> <span class="font-medium">${laneInfo.sourceCity}</span></div>`;
    }
    if (laneInfo.destinationCity) {
        content += `<div><span class="text-neutral-600">Destination:</span> <span class="font-medium">${laneInfo.destinationCity}</span></div>`;
    }
    if (laneInfo.laneName) {
        content += `<div class="col-span-2"><span class="text-neutral-600">Route:</span> <span class="font-medium">${laneInfo.laneName}</span></div>`;
    }
    if (laneInfo.equipmentType) {
        content += `<div><span class="text-neutral-600">Equipment:</span> <span class="font-medium">${laneInfo.equipmentType}</span></div>`;
    }
    if (laneInfo.serviceType) {
        content += `<div><span class="text-neutral-600">Service:</span> <span class="font-medium">${laneInfo.serviceType}</span></div>`;
    }
    if (laneInfo.weight) {
        content += `<div><span class="text-neutral-600">Weight:</span> <span class="font-medium">${laneInfo.weight}</span></div>`;
    }
    if (laneInfo.volume) {
        content += `<div><span class="text-neutral-600">Volume:</span> <span class="font-medium">${laneInfo.volume}</span></div>`;
    }
    
    // Add analysis type and status
    content += `<div><span class="text-neutral-600">Type:</span> <span class="font-medium">Spot Market Analysis</span></div>`;
    content += `<div><span class="text-neutral-600">Status:</span> <span class="font-medium text-green-600">Ready for Analysis</span></div>`;
    
    content += `
            </div>
        </div>
        <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div class="flex items-center text-blue-800">
                <i class="fas fa-info-circle mr-2"></i>
                <span class="text-sm font-medium">Ready for Spot Analysis</span>
            </div>
            <p class="text-xs text-blue-600 mt-1">Use the date picker and "Analyze" button in the header to perform spot rate analysis.</p>
        </div>
    `;
    
    contentElement.innerHTML = content;
}

// RIQ API Helper Functions
function cleanServiceProviderGid(servprovGid) {
    /**
     * Clean service provider GID by removing BSL. prefix
     * Example: "BSL.ODFL" -> "ODFL"
     */
    if (!servprovGid) return 'N/A';
    
    // Remove BSL. prefix if present
    if (servprovGid.startsWith('BSL.')) {
        return servprovGid.substring(4); // Remove "BSL."
    }
    
    return servprovGid;
}

function capitalizeLocation(locationString) {
    /**
     * Capitalize each word in a location string
     * Example: "elwood" -> "Elwood", "los angeles" -> "Los Angeles"
     */
    if (!locationString) return '';
    
    return locationString
        .toLowerCase()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function parseLocationFromCity(cityString) {
    /**
     * Parse city string to extract city, state, and country
     * Supports formats like "Elwood, IL, US" or "Elwood, IL" or "Elwood"
     * Also handles formats like "Elwood IL US" (space-separated)
     */
    if (!cityString) return null;
    
    // Try comma-separated format first
    let parts = cityString.split(',').map(part => part.trim());
    
    // If no commas, try space-separated format
    if (parts.length === 1) {
        parts = cityString.split(/\s+/);
        
        // For space-separated, we expect at least City + State
        if (parts.length >= 2) {
            // Reconstruct city name (all parts except last 1-2)
            let city, state, country;
            
            if (parts.length >= 3 && parts[parts.length - 1].length <= 3) {
                // Likely format: "City Name State Country"
                country = parts[parts.length - 1];
                state = parts[parts.length - 2];
                city = parts.slice(0, -2).join(' ');
            } else if (parts.length >= 2) {
                // Likely format: "City Name State"
                state = parts[parts.length - 1];
                city = parts.slice(0, -1).join(' ');
                country = 'US';
            }
            
            if (city && state) {
                return {
                    city: city,
                    province_code: state,
                    country_code: country || 'US'
                };
            }
        }
        
        // If still only one part, we can't make a valid API call
        console.warn(`Insufficient location data: ${cityString}`);
        return null;
    }
    
    // Handle comma-separated format
    if (parts.length >= 2) {
        return {
            city: parts[0],
            province_code: parts[1],
            country_code: parts[2] || 'US'
        };
    }
    
    return null;
}

function parseWeightAndVolume(weightStr, volumeStr) {
    /**
     * Parse weight and volume strings to extract numeric values and units
     */
    const result = {
        weight_value: 1000, // Default
        weight_unit: 'LB',
        volume_value: 50,   // Default
        volume_unit: 'CUFT'
    };
    
    if (weightStr) {
        const weightMatch = weightStr.match(/(\d+(?:,\d{3})*(?:\.\d+)?)\s*(lbs?|pounds?|kg|#)?/i);
        if (weightMatch) {
            result.weight_value = parseFloat(weightMatch[1].replace(/,/g, ''));
            if (weightMatch[2]) {
                const unit = weightMatch[2].toLowerCase();
                result.weight_unit = (unit === '#' || unit.includes('lb') || unit.includes('pound')) ? 'LB' : 'KG';
            }
        }
    }
    
    if (volumeStr) {
        const volumeMatch = volumeStr.match(/(\d+(?:,\d{3})*(?:\.\d+)?)\s*(cuft|cubic\s*feet?|cbm|cubic\s*meters?|ft3|m3)?/i);
        if (volumeMatch) {
            result.volume_value = parseFloat(volumeMatch[1].replace(/,/g, ''));
            if (volumeMatch[2]) {
                const unit = volumeMatch[2].toLowerCase();
                result.volume_unit = (unit.includes('cbm') || unit.includes('m3') || unit.includes('cubic m')) ? 'CBM' : 'CUFT';
            }
        }
    }
    
    return result;
}

function buildLocationObject(city, state, country = 'US') {
    /**
     * Build location object for RIQ API request
     */
    return {
        city: city,
        province_code: state,
        country_code: country
        // postal_code is optional and not included
    };
}

function buildItemObject(weightValue, weightUnit, volumeValue, volumeUnit) {
    /**
     * Build item object for RIQ API request
     */
    return {
        weight_value: weightValue || 1000,
        weight_unit: weightUnit || 'LB',
        volume_value: volumeValue || 50,
        volume_unit: volumeUnit || 'CUFT',
        declared_value: 0,
        currency: 'USD',
        package_count: 1,
        packaged_item_gid: 'DEFAULT'
    };
}

function mapCarrierToServprovGid(carrierName) {
    /**
     * Map carrier name to service provider GID
     * Uses BSL. prefix and carrier name - no hardcoded mapping
     */
    if (!carrierName) {
        console.log('No carrier name provided, using default BSL.RYGB');
        return 'BSL.RYGB'; // Default fallback
    }
    
    // Clean carrier name - remove extra spaces, special characters, and convert to uppercase
    let cleanName = carrierName.trim().toUpperCase();
    
    // Remove common words and punctuation
    cleanName = cleanName
        .replace(/\(.*?\)/g, '') // Remove parentheses and content
        .replace(/[.,&-]/g, '') // Remove punctuation
        .replace(/\s+/g, '_') // Replace spaces with underscores
        .replace(/^_+|_+$/g, ''); // Remove leading/trailing underscores
    
    // Handle common carrier name variations
    if (cleanName.includes('OLD_DOMINION') || cleanName === 'ODFL') {
        cleanName = 'ODFL';
    }
    
    const servprovGid = `BSL.${cleanName}`;
    console.log(`Mapping carrier "${carrierName}" to servprov_gid: "${servprovGid}"`);
    
    return servprovGid;
}

async function callRiqAPI(endpoint, payload) {
    /**
     * Make API call to RIQ endpoint
     */
    try {
        console.log(`Making RIQ API call to ${endpoint}:`, payload);
        
        const response = await fetch(`${RIQ_API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        console.log(`RIQ API response status: ${response.status}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`RIQ API error response:`, errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const result = await response.json();
        console.log(`RIQ API response:`, result);
        
        if (!result.success) {
            throw new Error(result.error || 'API request failed');
        }
        
        // Check if the API returned a 500 status in the data (carrier not available)
        if (result.data && result.data.status === 500) {
            throw new Error('The rate for the best carrier is not available currently');
        }
        
        return result;
    } catch (error) {
        console.error('RIQ API call failed:', error);
        throw error;
    }
}

async function getCheapestCarrierRate(sourceLocation, destLocation, items) {
    /**
     * Get cheapest carrier rate using /cheap-rate-quote endpoint
     */
    const payload = {
        source_location: sourceLocation,
        destination_location: destLocation,
        items: items,
        request_type: 'AllOptions',
        perspective: 'B',
        max_primary_options: '99',
        primary_option_definition: 'BY_ITINERARY'
    };
    
    return await callRiqAPI('/cheap-rate-quote', payload);
}

async function getBestCarrierRate(sourceLocation, destLocation, items, carrierName) {
    /**
     * Get rate for specific carrier using /rate-quote endpoint
     */
    const servprovGid = mapCarrierToServprovGid(carrierName);
    
    const payload = {
        source_location: sourceLocation,
        destination_location: destLocation,
        items: items,
        servprov_gid: servprovGid,
        request_type: 'AllOptions',
        perspective: 'B',
        max_primary_options: '99',
        primary_option_definition: 'BY_ITINERARY'
    };
    
    return await callRiqAPI('/rate-quote', payload);
}

async function executeDualRateQuery(laneInfo) {
    /**
     * Execute both cheapest and best carrier rate queries
     */
    // Parse source and destination
    const sourceLocation = parseLocationFromCity(laneInfo.sourceCity);
    const destLocation = parseLocationFromCity(laneInfo.destinationCity);
    
    if (!sourceLocation || !destLocation) {
        throw new Error('Invalid source or destination location data');
    }
    
    console.log('Parsed locations:', { sourceLocation, destLocation });
    
    // Parse weight and volume
    const { weight_value, weight_unit, volume_value, volume_unit } = parseWeightAndVolume(
        laneInfo.weight, 
        laneInfo.volume
    );
    
    console.log('Parsed weight/volume:', { weight_value, weight_unit, volume_value, volume_unit });
    
    // Build items array
    const items = [buildItemObject(weight_value, weight_unit, volume_value, volume_unit)];
    
    console.log('Built items array:', items);
    
    const results = {
        cheapest: null,
        bestCarrier: null,
        error: null
    };
    
    try {
        // Execute both API calls in parallel
        const promises = [
            getCheapestCarrierRate(sourceLocation, destLocation, items)
        ];
        
        if (laneInfo.bestCarrier) {
            console.log(`Adding best carrier query for: ${laneInfo.bestCarrier}`);
            promises.push(getBestCarrierRate(sourceLocation, destLocation, items, laneInfo.bestCarrier));
        } else {
            console.log('No best carrier specified, skipping best carrier query');
            promises.push(Promise.resolve(null));
        }
        
        const [cheapestResult, bestCarrierResult] = await Promise.allSettled(promises);
        
        if (cheapestResult.status === 'fulfilled') {
            results.cheapest = cheapestResult.value;
            console.log('Cheapest rate query succeeded');
        } else {
            console.error('Cheapest rate query failed:', cheapestResult.reason);
            results.error = `Cheapest rate query failed: ${cheapestResult.reason.message}`;
        }
        
        if (bestCarrierResult.status === 'fulfilled' && bestCarrierResult.value) {
            results.bestCarrier = bestCarrierResult.value;
            console.log('Best carrier rate query succeeded');
        } else if (laneInfo.bestCarrier) {
            console.error('Best carrier rate query failed:', bestCarrierResult.reason);
            if (!results.error) {
                results.error = `Best carrier rate query failed: ${bestCarrierResult.reason.message}`;
            } else {
                results.error += ` | Best carrier rate query failed: ${bestCarrierResult.reason.message}`;
            }
        }
        
        return results;
    } catch (error) {
        console.error('Dual rate query failed:', error);
        results.error = error.message;
        return results;
    }
}

function displayRateResults(results, laneInfo) {
    /**
     * Display rate results in the RIQ card
     */
    const statusElement = document.getElementById('rate-inquiry-status');
    const contentElement = document.getElementById('rate-inquiry-content');
    
    if (results.error && !results.cheapest && !results.bestCarrier) {
        // Complete failure
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        statusElement.textContent = 'Error';
        
        contentElement.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                <h5 class="font-medium text-red-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
                    Rate Query Failed
                </h5>
                <p class="text-xs text-red-700">${results.error}</p>
            </div>
        `;
        return;
    }
    
    // Keep status as "Ready for API Call" - don't duplicate status information
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
    statusElement.textContent = 'Ready for API Call';
    
    let content = '<div class="space-y-3">';
    
    // Display cheapest rate
    if (results.cheapest?.data?.rateAndRouteResponse?.length > 0) {
        const rateOptions = results.cheapest.data.rateAndRouteResponse;
        
        // Find the cheapest rate based on totalActualCost
        const cheapestRate = rateOptions.reduce((min, rate) => {
            const currentCost = parseFloat(rate.totalActualCost?.value || rate.primaryTotalCost?.value || 0);
            const minCost = parseFloat(min.totalActualCost?.value || min.primaryTotalCost?.value || Infinity);
            return currentCost < minCost ? rate : min;
        });
        
        // Extract key information
        const totalCost = cheapestRate.totalActualCost?.value || cheapestRate.primaryTotalCost?.value || 'N/A';
        const currency = cheapestRate.totalActualCost?.currency || cheapestRate.primaryTotalCost?.currency || 'USD';
        const serviceProviderGid = cheapestRate.serviceProvider?.servprovGid || 'N/A';
        const cleanCarrierName = cleanServiceProviderGid(serviceProviderGid);
        const transitTime = cheapestRate.transitTime?.amount || 'N/A';
        const transitTimeType = cheapestRate.transitTime?.type || '';
        
        // Calculate average cost per distance unit
        let averageCost = 'N/A';
        if (cheapestRate.toShipments?.[0]?.distance && totalCost !== 'N/A') {
            const distance = cheapestRate.toShipments[0].distance.amount;
            const distanceUnit = cheapestRate.toShipments[0].distance.type;
            const cost = parseFloat(totalCost);
            if (distance > 0) {
                averageCost = `${currency} ${(cost / distance).toFixed(2)}/${distanceUnit}`;
            }
        }
        
        content += `
            <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <h5 class="font-medium text-green-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-dollar-sign text-green-600 mr-2"></i>
                    Cheapest Option
                </h5>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div><span class="text-neutral-600">Total Cost:</span> <span class="font-medium text-green-700">${currency} ${parseFloat(totalCost).toLocaleString()}</span></div>
                    <div><span class="text-neutral-600">Avg Cost:</span> <span class="font-medium">${averageCost}</span></div>
                    <div><span class="text-neutral-600">Carrier:</span> <span class="font-medium">${cleanCarrierName}</span></div>
                    <div><span class="text-neutral-600">Transit:</span> <span class="font-medium">${transitTime} ${transitTimeType}</span></div>
                </div>
            </div>
        `;
    }
    
    // Display best carrier rate (if available)
    if (results.bestCarrier?.data?.rateAndRouteResponse?.length > 0 && laneInfo.bestCarrier) {
        const bestCarrierRates = results.bestCarrier.data.rateAndRouteResponse;
        const bestRate = bestCarrierRates[0]; // Take first rate from best carrier
        
        // Extract key information
        const totalCost = bestRate.totalActualCost?.value || bestRate.primaryTotalCost?.value || 'N/A';
        const currency = bestRate.totalActualCost?.currency || bestRate.primaryTotalCost?.currency || 'USD';
        const serviceProviderGid = bestRate.serviceProvider?.servprovGid || 'N/A';
        const cleanCarrierName = cleanServiceProviderGid(serviceProviderGid);
        const transitTime = bestRate.transitTime?.amount || 'N/A';
        const transitTimeType = bestRate.transitTime?.type || '';
        
        // Calculate average cost per distance unit
        let averageCost = 'N/A';
        if (bestRate.toShipments?.[0]?.distance && totalCost !== 'N/A') {
            const distance = bestRate.toShipments[0].distance.amount;
            const distanceUnit = bestRate.toShipments[0].distance.type;
            const cost = parseFloat(totalCost);
            if (distance > 0) {
                averageCost = `${currency} ${(cost / distance).toFixed(2)}/${distanceUnit}`;
            }
        }
        
        content += `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <h5 class="font-medium text-blue-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-star text-blue-600 mr-2"></i>
                    Best Performer (${laneInfo.bestCarrier})
                </h5>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div><span class="text-neutral-600">Total Cost:</span> <span class="font-medium text-blue-700">${currency} ${parseFloat(totalCost).toLocaleString()}</span></div>
                    <div><span class="text-neutral-600">Avg Cost:</span> <span class="font-medium">${averageCost}</span></div>
                    <div><span class="text-neutral-600">Carrier:</span> <span class="font-medium">${cleanCarrierName}</span></div>
                    <div><span class="text-neutral-600">Transit:</span> <span class="font-medium">${transitTime} ${transitTimeType}</span></div>
                </div>
            </div>
        `;
        
        // Add comparison if both rates available
        if (results.cheapest?.data?.rateAndRouteResponse?.length > 0) {
            const cheapestRateData = results.cheapest.data.rateAndRouteResponse.reduce((min, rate) => {
                const currentCost = parseFloat(rate.totalActualCost?.value || rate.primaryTotalCost?.value || 0);
                const minCost = parseFloat(min.totalActualCost?.value || min.primaryTotalCost?.value || Infinity);
                return currentCost < minCost ? rate : min;
            });
            
            const cheapestCost = parseFloat(cheapestRateData.totalActualCost?.value || cheapestRateData.primaryTotalCost?.value || 0);
            const bestCost = parseFloat(totalCost || 0);
            const difference = bestCost - cheapestCost;
            const percentDiff = cheapestCost > 0 ? ((difference / cheapestCost) * 100).toFixed(1) : 0;
            
            content += `
                <div class="bg-neutral-50 border border-neutral-200 rounded-lg p-4">
                    <h5 class="font-medium text-neutral-800 mb-2 flex items-center">
                        <i class="fas fa-balance-scale text-neutral-600 mr-2"></i>
                        Rate Comparison
                    </h5>
                    <p class="text-sm text-neutral-700">
                        ${difference >= 0 
                            ? `Best performer costs ${currency} ${Math.abs(difference).toLocaleString()} more (+${percentDiff}%) than cheapest option` 
                            : `Best performer costs ${currency} ${Math.abs(difference).toLocaleString()} less (-${Math.abs(percentDiff)}%) than cheapest option`
                        }
                    </p>
                </div>
            `;
        }
    }
    
    // Show any partial errors or best carrier unavailable message
    if (results.error && (results.cheapest || results.bestCarrier)) {
        const isCarrierUnavailable = results.error.includes('best carrier is not available currently');
        const bgColor = isCarrierUnavailable ? 'bg-blue-50 border-blue-200' : 'bg-yellow-50 border-yellow-200';
        const textColor = isCarrierUnavailable ? 'text-blue-800' : 'text-yellow-800';
        const iconColor = isCarrierUnavailable ? 'text-blue-600' : 'text-yellow-600';
        const icon = isCarrierUnavailable ? 'fa-info-circle' : 'fa-exclamation-triangle';
        
        content += `
            <div class="${bgColor} rounded-lg p-4">
                <h5 class="font-medium ${textColor} mb-2 flex items-center">
                    <i class="fas ${icon} ${iconColor} mr-2"></i>
                    ${isCarrierUnavailable ? 'Best Carrier Rate Unavailable' : 'Partial Results'}
                </h5>
                <p class="text-sm ${textColor.replace('800', '700')}">${results.error}</p>
            </div>
        `;
    }
    
    content += '</div>';
    contentElement.innerHTML = content;
}

// Global functions for API button actions
window.handleGetRatesClick = async function() {
    const getRatesBtn = document.getElementById('get-rates-btn');
    const statusElement = document.getElementById('rate-inquiry-status');
    
    if (!getRatesBtn) return;
    
    // Update button to loading state
    getRatesBtn.textContent = 'Loading...';
    getRatesBtn.className = 'px-3 py-1 bg-yellow-500 text-white text-sm rounded-lg font-medium cursor-not-allowed transition-colors';
    getRatesBtn.disabled = true;
    
    // Add spinner
    getRatesBtn.innerHTML = `
        <div class="flex items-center">
            <div class="animate-spin rounded-full h-3 w-3 border-b border-white mr-2"></div>
            Loading...
        </div>
    `;
    
    try {
        // Call the existing retrieveRateInquiry function
        await retrieveRateInquiry();
        
        // Success state
        getRatesBtn.innerHTML = 'Rates Retrieved';
        getRatesBtn.className = 'px-3 py-1 bg-green-600 text-white text-sm rounded-lg font-medium transition-colors';
        getRatesBtn.disabled = false;
        
    } catch (error) {
        console.error('Rate inquiry failed:', error);
        
        // Error state
        getRatesBtn.innerHTML = 'Retry';
        getRatesBtn.className = 'px-3 py-1 bg-red-600 text-white text-sm rounded-lg font-medium hover:bg-red-700 transition-colors';
        getRatesBtn.disabled = false;
        
        // Update status
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        statusElement.textContent = 'Error';
    }
};

// Function to toggle spot rate matrix visibility
window.toggleSpotRateMatrix = function() {
    const matrixTable = document.getElementById('spot-rate-matrix-table');
    const toggleIcon = document.getElementById('matrix-toggle-icon');
    const toggleText = document.getElementById('matrix-toggle-text');
    
    if (!matrixTable || !toggleIcon || !toggleText) return;
    
    if (matrixTable.classList.contains('hidden')) {
        // Show matrix
        matrixTable.classList.remove('hidden');
        toggleIcon.className = 'fas fa-chevron-up mr-2';
        toggleText.textContent = 'Hide Matrix';
    } else {
        // Hide matrix
        matrixTable.classList.add('hidden');
        toggleIcon.className = 'fas fa-chevron-down mr-2';
        toggleText.textContent = 'Show Matrix';
    }
};

// Perform comprehensive rate inquiry (replacing simple retrieveRateInquiry)
window.retrieveRateInquiry = async function() {
    const contentElement = document.getElementById('rate-inquiry-content');
    
    try {
        // Show loading state in content area
        contentElement.innerHTML = `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
                    <p class="text-sm text-blue-700">Retrieving comprehensive rate quotes from RIQ API...</p>
                </div>
            </div>
        `;
        
        // Extract lane information from the currently displayed RIQ card
        // We need to get the laneInfo from the last parsed response
        // This is stored in the global scope from parseAndUpdateLaneInfo
        if (!window.currentLaneInfo) {
            throw new Error('No lane information available. Please ensure the chat has parsed location and carrier data.');
        }
        
        const laneInfo = window.currentLaneInfo;
        
        // Validate required data
        if (!laneInfo.sourceCity || !laneInfo.destinationCity) {
            throw new Error('Missing required location data. Please ensure both origin and destination cities are specified.');
        }
        
        console.log('Executing comprehensive dual rate query with data:', laneInfo);
        
        // Execute the comprehensive dual rate query using the new two-step API workflow
        const results = await executeDualRateQueryComprehensive(laneInfo);
        
        console.log('Comprehensive rate query results:', results);
        
        // Display the results using the new comprehensive display function
        displayRateResultsComprehensive(results, laneInfo);
        
        // Update recommendation data collection with the comprehensive results
        if (results.cheapest || results.bestCarrier) {
            updateRecommendationDataCollection('riq_rates', results, true);
        }
        
    } catch (error) {
        console.error('Comprehensive rate inquiry failed:', error);
        
        // Show error state in content area
        contentElement.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <h5 class="font-medium text-red-800 mb-2 flex items-center">
                    <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
                    Comprehensive Rate Query Failed
                </h5>
                <p class="text-sm text-red-700">${error.message}</p>
                <button onclick="window.retrieveRateInquiry()" class="mt-3 px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors">
                    <i class="fas fa-redo mr-2"></i>Retry
                </button>
            </div>
        `;
        
        // Re-throw the error so handleGetRatesClick can catch it
        throw error;
    }
};

// NEW: Comprehensive rate inquiry function for direct use
window.retrieveRateInquiryComprehensive = async function() {
    const contentElement = document.getElementById('rate-inquiry-content');
    
    try {
        // Show loading state with two-step progress indicator
        contentElement.innerHTML = `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center mb-3">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
                    <p class="text-sm text-blue-700 font-medium">Comprehensive RIQ Rate Query</p>
                </div>
                <div class="space-y-2 text-xs text-blue-600">
                    <div class="flex items-center">
                        <div class="animate-pulse w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                        <span>Step 1: Looking up location IDs...</span>
                    </div>
                    <div class="flex items-center">
                        <div class="w-2 h-2 bg-blue-200 rounded-full mr-2"></div>
                        <span>Step 2: Querying comprehensive rate data...</span>
                    </div>
                </div>
            </div>
        `;
        
        // Extract lane information
        if (!window.currentLaneInfo) {
            throw new Error('No lane information available. Please ensure the chat has parsed location and carrier data.');
        }
        
        const laneInfo = window.currentLaneInfo;
        
        // Validate required data
        if (!laneInfo.sourceCity || !laneInfo.destinationCity) {
            throw new Error('Missing required location data. Please ensure both origin and destination cities are specified.');
        }
        
        // Update progress indicator for step 2
        setTimeout(() => {
            if (contentElement.innerHTML.includes('Step 1: Looking up location IDs')) {
                contentElement.innerHTML = `
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div class="flex items-center mb-3">
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
                            <p class="text-sm text-blue-700 font-medium">Comprehensive RIQ Rate Query</p>
                        </div>
                        <div class="space-y-2 text-xs text-blue-600">
                            <div class="flex items-center">
                                <div class="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                                <span>Step 1: Location IDs retrieved ✓</span>
                            </div>
                            <div class="flex items-center">
                                <div class="animate-pulse w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                                <span>Step 2: Querying comprehensive rate data...</span>
                            </div>
                        </div>
                    </div>
                `;
            }
        }, 1500);
        
        console.log('🚀 Starting comprehensive rate query:', laneInfo);
        
        // Execute the comprehensive dual rate query
        const results = await executeDualRateQueryComprehensive(laneInfo);
        
        console.log('✅ Comprehensive rate query completed:', results);
        
        // Display the results
        displayRateResultsComprehensive(results, laneInfo);
        
        // Update recommendation data collection
        if (results.cheapest || results.bestCarrier) {
            updateRecommendationDataCollection('riq_rates', results, true);
        }
        
        // Show success notification
        if (results.metadata && results.metadata.totalOptions > 0) {
            showNotification(`Found ${results.metadata.totalOptions} rate options from ${results.metadata.carriers.length} carriers`, 'success');
        }
        
    } catch (error) {
        console.error('Comprehensive rate inquiry failed:', error);
        
        // Show detailed error state
        contentElement.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <h5 class="font-medium text-red-800 mb-2 flex items-center">
                    <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
                    Comprehensive Rate Query Failed
                </h5>
                <div class="space-y-2 text-xs text-red-700 mb-3">
                    <div>Error: ${error.message}</div>
                    <div class="text-red-600">This uses the new two-step RIQ API workflow:</div>
                    <div>• Step 1: /new-riq-rest (location lookup)</div>
                    <div>• Step 2: /riq-xml (comprehensive rate query)</div>
                </div>
                <button onclick="window.retrieveRateInquiryComprehensive()" class="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors">
                    <i class="fas fa-redo mr-2"></i>Retry Comprehensive Query
                </button>
            </div>
        `;
        
        // Show error notification
        showNotification(`Rate query failed: ${error.message}`, 'error');
        
        throw error;
    }
};

window.performSpotAnalysis = function() {
    // Get the date value
    const shipmentDate = document.getElementById('spot-ship-date')?.value;
    
    if (!shipmentDate) {
        showNotification('Please select a shipment date', 'warning');
        return;
    }
    
    // Use the globally stored lane info
    const laneInfo = window.currentLaneInfo;
    
    if (!laneInfo || !laneInfo.sourceCity || !laneInfo.destinationCity) {
        showNotification('Lane information is incomplete. Please provide source and destination cities.', 'warning');
        return;
    }
    
    console.log('Performing spot analysis with:', {
        laneInfo,
        shipmentDate
    });
    
    // Update the card to show loading state
    updateSpotAnalysisLoadingState();
    
    // Call the spot rate matrix API
    fetchSpotRateMatrix(laneInfo, shipmentDate);
};

async function fetchSpotRateMatrix(laneInfo, shipmentDate) {
    try {
        // Parse location information similar to historical data
        let sourceLocationParsed = null;
        if (laneInfo.sourceCity) {
            sourceLocationParsed = parseLocationFromCity(laneInfo.sourceCity);
        }

        let destLocationParsed = null;
        if (laneInfo.destinationCity) {
            destLocationParsed = parseLocationFromCity(laneInfo.destinationCity);
        }

        // Build the request payload
        const requestPayload = {
            source_city: sourceLocationParsed ? sourceLocationParsed.city : laneInfo.sourceCity,
            source_state: sourceLocationParsed ? sourceLocationParsed.province_code : laneInfo.sourceState,
            source_country: sourceLocationParsed ? sourceLocationParsed.country_code : laneInfo.sourceCountry,
            dest_city: destLocationParsed ? destLocationParsed.city : laneInfo.destinationCity,
            dest_state: destLocationParsed ? destLocationParsed.province_code : laneInfo.destinationState,
            dest_country: destLocationParsed ? destLocationParsed.country_code : laneInfo.destinationCountry,
            shipment_date: shipmentDate
        };

        // Remove null/undefined keys from payload
        Object.keys(requestPayload).forEach(key => {
            if (requestPayload[key] === null || requestPayload[key] === undefined) {
                delete requestPayload[key];
            }
        });

        console.log("Fetching spot rate matrix with payload:", requestPayload);

        const response = await fetch(`${DATA_TOOLS_API_BASE_URL}/spot-rate/matrix`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        const spotRateData = await response.json();
        
        // Store the spot data for recommendations and modal use
        updateRecommendationDataCollection('spot_data', spotRateData, true);
        
        // Display in the main card
        displaySpotRateMatrix(spotRateData);
        showNotification('Spot rate matrix loaded successfully!', 'success');
        
        // Return the data for use by modal
        return spotRateData;

    } catch (error) {
        console.error('Failed to fetch spot rate matrix:', error);
        updateSpotAnalysisErrorState(error.message);
        showNotification(`Failed to fetch spot rate matrix: ${error.message}`, 'error');
        throw error; // Re-throw so modal can handle the error
    }
}

function updateSpotAnalysisLoadingState() {
    const statusElement = document.getElementById('spot-api-status');
    const contentElement = document.getElementById('spot-api-content');
    
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
    statusElement.textContent = 'Loading...';
    
    contentElement.innerHTML = `
        <div class="text-center py-8 text-neutral-500">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
            <p>Loading spot rate matrix...</p>
        </div>
    `;
}

function updateSpotAnalysisErrorState(errorMessage) {
    const statusElement = document.getElementById('spot-api-status');
    const contentElement = document.getElementById('spot-api-content');
    
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
    statusElement.textContent = 'Error';
    
    contentElement.innerHTML = `
        <div class="text-center py-8 text-red-500">
            <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
            <p>Failed to load spot rate matrix</p>
            <p class="text-sm mt-2">${escapeHtml(errorMessage)}</p>
            <button onclick="performSpotAnalysis()" class="mt-4 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                <i class="fas fa-redo mr-2"></i>Retry
            </button>
        </div>
    `;
}

function displaySpotRateMatrix(data) {
    const statusElement = document.getElementById('spot-api-status');
    const contentElement = document.getElementById('spot-api-content');
    
    if (!data || !data.spot_costs) {
        updateSpotAnalysisErrorState('Invalid data received from server');
        return;
    }

    const { origin_city, origin_state, destination_city, destination_state, shipment_date, spot_costs } = data;
    
    // Update status
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
    statusElement.textContent = `${spot_costs.length} Carriers`;

    let content = `
        <div class="space-y-4">
    `;

    if (spot_costs.length > 0) {
        // Collect all rates for statistics
        const allRatesWithDetails = spot_costs.flatMap(carrier => 
            carrier.cost_details.map(detail => ({
                cost: parseFloat(detail.total_spot_cost),
                carrier: carrier.carrier,
                mode: detail.transport_mode,
                date: detail.ship_date
            }))
        );
        
        const minRateData = allRatesWithDetails.reduce((min, rate) => rate.cost < min.cost ? rate : min);
        const maxRateData = allRatesWithDetails.reduce((max, rate) => rate.cost > max.cost ? rate : max);
        
        // Use the best carrier from chat parsing (laneInfo.bestCarrier) instead of calculating independently
        let bestCarrierBestRate = null;
        const laneInfo = window.currentLaneInfo;
        
        if (laneInfo && laneInfo.bestCarrier) {
            // Find the best carrier from chat parsing in the spot rate data
            const bestCarrierFromChat = laneInfo.bestCarrier;
            const bestCarrierRates = allRatesWithDetails.filter(rate => 
                rate.carrier.toLowerCase().includes(bestCarrierFromChat.toLowerCase()) ||
                bestCarrierFromChat.toLowerCase().includes(rate.carrier.toLowerCase())
            );
            
            if (bestCarrierRates.length > 0) {
                bestCarrierBestRate = bestCarrierRates.reduce((min, rate) => rate.cost < min.cost ? rate : min);
            }
        }

        // Combined Rate Statistics and Lane Parameters Section
        content += `
            <!-- Combined Rate Statistics & Lane Parameters -->
            <div class="bg-green-50 rounded-lg p-4">
                <h4 class="font-medium text-green-900 mb-4 flex items-center">
                    <i class="fas fa-chart-bar text-green-600 mr-2"></i>
                    Rate Statistics
                </h4>
                
                <!-- Lane Parameters Grid -->
                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 text-sm mb-4">`;

        // // Add lane parameters dynamically
        // if (laneInfo && laneInfo.sourceCity) {
        //     content += `<div><span class="text-neutral-600">Origin:</span> <span class="font-medium">${laneInfo.sourceCity}</span></div>`;
        // } else {
        //     content += `<div><span class="text-neutral-600">Origin:</span> <span class="font-medium">${escapeHtml(origin_city)}</span></div>`;
        // }
        
        // if (laneInfo && laneInfo.destinationCity) {
        //     content += `<div><span class="text-neutral-600">Destination:</span> <span class="font-medium">${laneInfo.destinationCity}</span></div>`;
        // } else {
        //     content += `<div><span class="text-neutral-600">Destination:</span> <span class="font-medium">${escapeHtml(destination_city)}</span></div>`;
        // }
        
        // content += `<div><span class="text-neutral-600">Shipment Date:</span> <span class="font-medium">${escapeHtml(shipment_date)}</span></div>`;
        // content += `<div><span class="text-neutral-600">Carriers Found:</span> <span class="font-medium">${spot_costs.length}</span></div>`;
        
        // if (laneInfo && laneInfo.laneName) {
        //     content += `<div class="col-span-2"><span class="text-neutral-600">Route:</span> <span class="font-medium">${laneInfo.laneName}</span></div>`;
        // }
        
        // if (laneInfo && laneInfo.equipmentType) {
        //     content += `<div><span class="text-neutral-600">Equipment:</span> <span class="font-medium">${laneInfo.equipmentType}</span></div>`;
        // }
        
        // if (laneInfo && laneInfo.serviceType) {
        //     content += `<div><span class="text-neutral-600">Service:</span> <span class="font-medium">${laneInfo.serviceType}</span></div>`;
        // }
        
        // if (laneInfo && laneInfo.weight) {
        //     content += `<div><span class="text-neutral-600">Weight:</span> <span class="font-medium">${laneInfo.weight}</span></div>`;
        // }
        
        // if (laneInfo && laneInfo.volume) {
        //     content += `<div><span class="text-neutral-600">Volume:</span> <span class="font-medium">${laneInfo.volume}</span></div>`;
        // }

        content += `
                </div>
                
                <!-- Rate Statistics Grid -->
                <div class="border-t border-green-200 pt-4">
                    <div class="grid grid-cols-3 gap-4 text-sm">
                        <div class="text-center">
                            <div class="text-neutral-600 mb-1">Lowest Rate</div>
                            <div class="font-medium text-lg text-green-700">$${minRateData.cost.toFixed(2)}</div>
                            <div class="text-xs text-neutral-500">${minRateData.carrier}</div>
                            <div class="text-xs text-neutral-500">${minRateData.date}</div>
                        </div>
                        <div class="text-center">
                            <div class="text-neutral-600 mb-1">Best Rate</div>`;
        
        if (bestCarrierBestRate) {
            content += `
                            <div class="font-medium text-lg text-green-700">$${bestCarrierBestRate.cost.toFixed(2)}</div>
                            <div class="text-xs text-neutral-500">${bestCarrierBestRate.carrier}</div>
                            <div class="text-xs text-neutral-500">${bestCarrierBestRate.date}</div>`;
        } else if (laneInfo && laneInfo.bestCarrier) {
            content += `
                            <div class="font-medium text-lg text-gray-500">Not Available</div>
                            <div class="text-xs text-neutral-500">${laneInfo.bestCarrier}</div>
                            <div class="text-xs text-neutral-500">Not in spot data</div>`;
        } else {
            content += `
                            <div class="font-medium text-lg text-gray-500">Not Identified</div>
                            <div class="text-xs text-neutral-500">No best carrier</div>
                            <div class="text-xs text-neutral-500">from chat</div>`;
        }
        
        content += `
                        </div>
                        <div class="text-center">
                            <div class="text-neutral-600 mb-1">Highest Rate</div>
                            <div class="font-medium text-lg text-red-600">$${maxRateData.cost.toFixed(2)}</div>
                            <div class="text-xs text-neutral-500">${maxRateData.carrier}</div>
                            <div class="text-xs text-neutral-500">${maxRateData.date}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Get all unique dates from all carriers to ensure consistent columns
        const allDates = [...new Set(spot_costs.flatMap(carrier => 
            carrier.cost_details.map(detail => detail.ship_date)
        ))].sort();

        const minRate = Math.min(...allRatesWithDetails.map(r => r.cost));
        const maxRate = Math.max(...allRatesWithDetails.map(r => r.cost));

    } else {
        content += `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-info-circle text-4xl mb-4 text-neutral-300"></i>
                <p>No carriers found for this lane and date combination.</p>
            </div>
        `;
    }

    content += `</div>`;
    contentElement.innerHTML = content;
}

// Historical Data Card Functions (NEW)
async function updateHistoricalDataCard(laneInfo, userMessage, response) {
    const statusElement = document.getElementById('historical-lane-status');
    const contentElement = document.getElementById('historical-data-content');

    if (!laneInfo || !laneInfo.sourceCity || !laneInfo.destinationCity) {
        console.warn("HistoricalDataCard: Insufficient lane info (source/dest city) to fetch data.", laneInfo);
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        statusElement.textContent = 'Needs Lane';
        contentElement.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-info-circle text-4xl mb-4 text-neutral-300"></i>
                <p>Please provide a full lane (e.g., city to city) to see historical data.</p>
            </div>
        `;
        return;
    }
    
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
    statusElement.textContent = 'Loading...';
    contentElement.innerHTML = `
        <div class="text-center py-8 text-neutral-500">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p>Loading historical data...</p>
        </div>
    `;
    
    try {
        const historicalData = await fetchHistoricalData(laneInfo);
        displayHistoricalData(historicalData, contentElement, laneInfo);
        
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800';
        statusElement.textContent = `${historicalData.total_count} Records`;
        
    } catch (error) {
        console.error('Failed to fetch or display historical data:', error);
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        statusElement.textContent = 'Data Error';
        contentElement.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p>Failed to load historical data</p>
                <p class="text-sm mt-2">${escapeHtml(error.message)}</p>
            </div>
        `;
    }
}

async function fetchHistoricalData(laneInfo) {
    let sourceLocationParsed = null;
    if (laneInfo.sourceCity) {
        sourceLocationParsed = parseLocationFromCity(laneInfo.sourceCity);
    }

    let destLocationParsed = null;
    if (laneInfo.destinationCity) {
        destLocationParsed = parseLocationFromCity(laneInfo.destinationCity);
    }

    // Fallback if parsing fails but we still have the original strings, though backend might not match well
    const source_city = sourceLocationParsed ? sourceLocationParsed.city : laneInfo.sourceCity;
    const source_state = sourceLocationParsed ? sourceLocationParsed.province_code : laneInfo.sourceState; // laneInfo.sourceState might be from a different parsing logic
    const source_country = sourceLocationParsed ? sourceLocationParsed.country_code : laneInfo.sourceCountry;

    const dest_city = destLocationParsed ? destLocationParsed.city : laneInfo.destinationCity;
    const dest_state = destLocationParsed ? destLocationParsed.province_code : laneInfo.destinationState;
    const dest_country = destLocationParsed ? destLocationParsed.country_code : laneInfo.destinationCountry;

    const requestPayload = {
        source_city: source_city,
        source_state: source_state,
        source_country: source_country,
        dest_city: dest_city,
        dest_state: dest_state,
        dest_country: dest_country,
        // transport_mode: laneInfo.equipmentType, // REMOVED as per user request
        limit: 50 
    };
    
    // Remove null/undefined keys from payload to send cleaner requests
    Object.keys(requestPayload).forEach(key => {
        if (requestPayload[key] === null || requestPayload[key] === undefined) {
            delete requestPayload[key];
        }
    });

    console.log("Fetching historical data with payload:", requestPayload);
    const response = await fetch(`${DATA_TOOLS_API_BASE_URL}/historical-data/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestPayload)
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
}

function displayHistoricalData(data, contentElement, laneInfo) {
    if (!data || !data.records) {
        console.error("Invalid historical data received:", data);
        contentElement.innerHTML = `<p class="text-red-500 text-center text-sm">Error: Invalid data received from server.</p>`;
        return;
    }

    const { records, total_count, lane_summary, cost_statistics, query_parameters } = data;
    const queryRoute = `${query_parameters.source_city || 'Any'} to ${query_parameters.dest_city || 'Any'}`;

    let content = `
        <div class="bg-purple-50 rounded-lg p-3">
            <h4 class="font-medium text-purple-900 mb-2 flex items-center text-sm">
                <i class="fas fa-route text-purple-600 mr-2"></i>
                Lane Summary: ${escapeHtml(lane_summary.route || queryRoute)}
            </h4>
            <div class="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
                <div><span class="text-neutral-600">Matches:</span> <span class="font-medium">${total_count}</span></div>
                <div><span class="text-neutral-600">Avg $/Mile:</span> <span class="font-medium">${typeof cost_statistics.avg_cost_per_mile === 'number' ? '$'+cost_statistics.avg_cost_per_mile.toFixed(2) : 'N/A'}</span></div>
                <div><span class="text-neutral-600">Mode:</span> <span class="font-medium">${escapeHtml(lane_summary.most_common_mode || 'N/A')}</span></div>
                <div><span class="text-neutral-600">Avg $/Lb:</span> <span class="font-medium">${typeof cost_statistics.avg_cost_per_lb === 'number' ? '$'+cost_statistics.avg_cost_per_lb.toFixed(2) : 'N/A'}</span></div>
                <div><span class="text-neutral-600">Avg $/CUFT:</span> <span class="font-medium">${typeof cost_statistics.avg_cost_per_cuft === 'number' ? '$'+cost_statistics.avg_cost_per_cuft.toFixed(2) : 'N/A'}</span></div>
                <div><span class="text-neutral-600">Shipments:</span> <span class="font-medium">${lane_summary.total_shipments_in_data || 'N/A'}</span></div>
            </div>
        </div>
    `;
    
    contentElement.innerHTML = content;
}

function viewDetailedHistoricalData() {
    // Future implementation for detailed view/modal or navigating to a new page
    showNotification('Detailed historical analysis and interactive charts are planned for a future update!', 'info', 5000);
}

// Make sure escapeHtml function is available, if not, define a simple one:
if (typeof escapeHtml !== 'function') {
    function escapeHtml(unsafe) {
        if (unsafe === null || typeof unsafe === 'undefined') return '';
        return String(unsafe)
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
}

// Default Knowledge Base Management Functions
function setDefaultKB(kbId) {
    localStorage.setItem('defaultKnowledgeBaseId', kbId);
}

function getDefaultKB() {
    return localStorage.getItem('defaultKnowledgeBaseId');
}

function clearDefaultKB() {
    localStorage.removeItem('defaultKnowledgeBaseId');
}

function handleDefaultKBChange(kbId, checkbox) {
    if (checkbox.checked) {
        setDefaultKB(kbId);
    } else {
        clearDefaultKB();
    }
}

// =============================================================================
// ORDER RELEASE FUNCTIONALITY
// =============================================================================

/**
 * Updates the order release card with lane information and a button to fetch unplanned orders
 */
async function updateOrderReleaseCard(laneInfo, userMessage, response) {
    const statusElement = document.getElementById('order-release-status');
    const contentElement = document.getElementById('order-release-content');
    
    if (!statusElement || !contentElement) {
        console.error('Order release card elements not found');
        return;
    }

    try {
        // Update status to show processing
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-600';
        statusElement.textContent = 'Fetching Orders...';

        // Build the lane display string
        const sourceDisplay = laneInfo.sourceCity && laneInfo.sourceState ? 
            `${laneInfo.sourceCity}, ${laneInfo.sourceState}` : 
            (laneInfo.sourceCity || 'Unknown Origin');
        const destDisplay = laneInfo.destinationCity && laneInfo.destinationState ? 
            `${laneInfo.destinationCity}, ${laneInfo.destinationState}` : 
            (laneInfo.destinationCity || 'Unknown Destination');
        
        const laneDisplay = `${sourceDisplay} → ${destDisplay}`;

        // Display lane information with loading state
        contentElement.innerHTML = `
            <div class="text-center py-4">
                <div class="mb-4">
                    <i class="fas fa-route text-3xl mb-3 text-orange-500"></i>
                    <p class="text-sm font-medium text-neutral-700 mb-2">Lane Detected - Fetching Orders</p>
                    <p class="text-sm text-neutral-600 mb-4">${escapeHtml(laneDisplay)}</p>
                </div>
                <div class="text-center">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500 mx-auto mb-2"></div>
                    <p class="text-xs text-orange-600">Fetching unplanned orders automatically...</p>
                </div>
            </div>
        `;

        // Auto-trigger order fetching
        setTimeout(async () => {
            try {
                console.log('DEBUG: Auto-triggering order fetch for lane:', laneInfo);
                
                // Fetch orders using the existing function
                const ordersData = await fetchUnplannedOrders(laneInfo);
                
                // Update status to show success
                statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-600';
                statusElement.textContent = `${ordersData?.data?.items?.length || 0} Orders Found`;
                
                // Display the orders
                if (ordersData && ordersData.data && ordersData.data.items) {
                    displayUnplannedOrders(ordersData.data.items, contentElement, laneInfo);
                } else {
                    contentElement.innerHTML = `
                        <div class="text-center py-4 text-neutral-500">
                            <i class="fas fa-inbox text-2xl mb-2 text-neutral-300"></i>
                            <p class="text-xs">No unplanned orders found for this lane</p>
                        </div>
                    `;
                }
                
            } catch (error) {
                console.error('Auto-run order fetch failed:', error);
                
                // Show error state with retry option
                statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-600';
                statusElement.textContent = 'Fetch Failed';
                
                contentElement.innerHTML = `
                    <div class="text-center py-4">
                        <div class="bg-red-50 rounded-lg p-3">
                            <i class="fas fa-exclamation-triangle text-red-500 text-2xl mb-2"></i>
                            <p class="text-sm text-red-700 mb-2">Failed to fetch orders automatically</p>
                            <p class="text-xs text-red-600 mb-3">${escapeHtml(error.message)}</p>
                            <button onclick="handleGetOrdersClick()" class="inline-flex items-center px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors duration-200">
                                <i class="fas fa-retry mr-2"></i>
                                Retry Fetch
                            </button>
                        </div>
                    </div>
                `;
            }
        }, 1500); // 1.5 second delay to allow UI to update

    } catch (error) {
        console.error('Error in updateOrderReleaseCard:', error);
        
        // Update status to show error
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-600';
        statusElement.textContent = 'Error';
        
        contentElement.innerHTML = `
            <div class="text-center py-4 text-red-600">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p class="text-xs">Failed to process lane information</p>
            </div>
        `;
    }
}

/**
 * Fetches unplanned orders from the API for the given lane
 */
async function fetchUnplannedOrders(laneInfo) {
    console.log('=== DEBUG: fetchUnplannedOrders started ===');
    console.log('DEBUG: Input laneInfo:', laneInfo);
    
    if (!laneInfo.sourceCity || !laneInfo.destinationCity) {
        console.error('DEBUG: Insufficient lane information:', laneInfo);
        throw new Error('Insufficient lane information');
    }

    // Parse city and state from the lane info
    const sourceLocation = parseLocationFromCity(laneInfo.sourceCity);
    const destLocation = parseLocationFromCity(laneInfo.destinationCity);

    console.log('DEBUG: Parsed sourceLocation:', sourceLocation);
    console.log('DEBUG: Parsed destLocation:', destLocation);

    // Check if parsing was successful
    if (!sourceLocation || !destLocation) {
        console.error('DEBUG: Failed to parse location information');
        console.error('DEBUG: sourceLocation:', sourceLocation);
        console.error('DEBUG: destLocation:', destLocation);
        throw new Error('Failed to parse location information');
    }

    // CAPITALIZE city names for API call (API is case-sensitive)
    const payload = {
        origin_city: sourceLocation.city.toUpperCase(),  // CAPITALIZE
        origin_state: sourceLocation.province_code,  // Fixed: was sourceLocation.state
        origin_country: sourceLocation.country_code || 'US',  // Fixed: was sourceLocation.country
        destination_city: destLocation.city.toUpperCase(),  // CAPITALIZE
        destination_state: destLocation.province_code,  // Fixed: was destLocation.state
        destination_country: destLocation.country_code || 'US'  // Fixed: was destLocation.country
    };

    console.log('DEBUG: API payload (with capitalized cities):', payload);
    console.log('DEBUG: API endpoint:', `${DATA_TOOLS_API_BASE_URL}/order-release/unplanned-orders`);

    try {
        const response = await fetch(`${DATA_TOOLS_API_BASE_URL}/order-release/unplanned-orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        console.log('DEBUG: Raw response status:', response.status);
        console.log('DEBUG: Raw response statusText:', response.statusText);
        console.log('DEBUG: Raw response headers:', [...response.headers.entries()]);

        if (!response.ok) {
            console.error('DEBUG: Response not OK:', response.status, response.statusText);
            if (response.status === 404) {
                throw new Error(`No unplanned orders found for ${payload.origin_city}, ${payload.origin_state} to ${payload.destination_city}, ${payload.destination_state}`);
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        }

        const result = await response.json();
        console.log('DEBUG: Parsed JSON result:', result);
        console.log('DEBUG: Result type:', typeof result);
        console.log('DEBUG: Result keys:', Object.keys(result || {}));
        
        if (result.data && result.data.items) {
            console.log('DEBUG: Found items array with length:', result.data.items.length);
            console.log('DEBUG: First item sample:', result.data.items[0]);
        }

        return result;

    } catch (error) {
        console.error('DEBUG: Error in fetchUnplannedOrders:', error);
        console.error('DEBUG: Error type:', typeof error);
        console.error('DEBUG: Error message:', error.message);
        console.error('DEBUG: Error stack:', error.stack);
        throw error;
    } finally {
        console.log('=== DEBUG: fetchUnplannedOrders completed ===');
    }
}

/**
 * Displays the list of unplanned orders in the card content
 */
function displayUnplannedOrders(orders, contentElement, laneInfo) {
    console.log('=== DEBUG: displayUnplannedOrders started ===');
    console.log('DEBUG: Input orders:', orders);
    console.log('DEBUG: Orders type:', typeof orders);
    console.log('DEBUG: Orders is array:', Array.isArray(orders));
    console.log('DEBUG: Orders length:', orders?.length);
    console.log('DEBUG: contentElement:', contentElement);
    console.log('DEBUG: laneInfo:', laneInfo);
    
    if (!orders || orders.length === 0) {
        console.log('DEBUG: No orders to display - showing empty state');
        contentElement.innerHTML = `
            <div class="text-center py-4 text-neutral-500">
                <i class="fas fa-inbox text-2xl mb-2 text-neutral-300"></i>
                <p class="text-xs">No orders found</p>
            </div>
        `;
        return;
    }

    console.log('DEBUG: Processing', orders.length, 'orders');
    
    const ordersHtml = orders.map((order, index) => {
        console.log(`DEBUG: Processing order ${index + 1}:`, order);
        
        // Extract basic order information
        const orderReleaseId = order.orderReleaseXid || 'N/A';
        const orderName = order.orderReleaseName || 'Unknown Order';
        
        console.log(`DEBUG: Order ${index + 1} - ID: ${orderReleaseId}, Name: ${orderName}`);
        
        // Extract date information (nested object)
        let latePickupDate = 'N/A';
        if (order.latePickupDate && order.latePickupDate.value) {
            latePickupDate = order.latePickupDate.value;
        }
        console.log(`DEBUG: Order ${index + 1} - Late pickup date: ${latePickupDate}`);
        
        // Extract weight information (nested object)
        let totalWeight = 'N/A';
        if (order.totalWeight && order.totalWeight.value !== undefined) {
            const unit = order.totalWeight.unit || 'LB';
            totalWeight = `${order.totalWeight.value} ${unit}`;
        }
        console.log(`DEBUG: Order ${index + 1} - Total weight: ${totalWeight}`);
        
        // Extract volume information (nested object)
        let totalVolume = 'N/A';
        if (order.totalVolume && order.totalVolume.value !== undefined) {
            const unit = order.totalVolume.unit || 'CUFT';
            totalVolume = `${order.totalVolume.value} ${unit}`;
        }
        console.log(`DEBUG: Order ${index + 1} - Total volume: ${totalVolume}`);
        
        // Extract cost information (nested object)
        let bestDirectCost = 'N/A';
        if (order.bestDirectCostBuy && order.bestDirectCostBuy.value !== undefined) {
            const currency = order.bestDirectCostBuy.currency || 'USD';
            bestDirectCost = `$${order.bestDirectCostBuy.value} ${currency}`;
        }
        console.log(`DEBUG: Order ${index + 1} - Best direct cost: ${bestDirectCost}`);
        
        // Extract service provider information (from nested links or direct field)
        let serviceProvider = 'N/A';
        if (order.bestDirectRateofferGidBuy) {
            // Extract service provider from rate offer GID (e.g., "BSL.TL_BNCH" -> "BNCH")
            const parts = order.bestDirectRateofferGidBuy.split('.');
            serviceProvider = parts.length > 1 ? parts[parts.length - 1].replace('TL_', '') : order.bestDirectRateofferGidBuy;
        } else if (order.servprov && order.servprov.links) {
            // Try to extract from servprov links if available
            const canonical = order.servprov.links.find(link => link.rel === 'canonical');
            if (canonical && canonical.href) {
                const parts = canonical.href.split('/');
                const gid = parts[parts.length - 1];
                serviceProvider = gid.split('.').pop() || gid;
            }
        }
        console.log(`DEBUG: Order ${index + 1} - Service provider: ${serviceProvider}`);

        const orderHtml = `
            <div class="border border-neutral-200 rounded-lg p-2 hover:bg-neutral-50 cursor-pointer transition-colors order-item" 
                 data-order-gid="${escapeHtml(orderReleaseId)}" 
                 onclick="selectOrder('${escapeHtml(orderReleaseId)}')">
                <div class="flex justify-between items-start mb-1">
                    <div class="flex-1 min-w-0">
                        <h4 class="text-xs font-medium text-neutral-900 truncate">${escapeHtml(orderName)}</h4>
                        <p class="text-xs text-neutral-500">ID: ${escapeHtml(orderReleaseId)}</p>
                    </div>
                    <div class="text-right flex-shrink-0 ml-2">
                        <p class="text-xs font-medium text-green-600">${escapeHtml(bestDirectCost)}</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-1 text-xs text-neutral-600">
                    <div>
                        <i class="fas fa-calendar text-neutral-400"></i>
                        <span class="ml-1">${formatOrderDate(latePickupDate)}</span>
                    </div>
                    <div>
                        <i class="fas fa-weight text-neutral-400"></i>
                        <span class="ml-1">${escapeHtml(totalWeight)}</span>
                    </div>
                    <div>
                        <i class="fas fa-cube text-neutral-400"></i>
                        <span class="ml-1">${escapeHtml(totalVolume)}</span>
                    </div>
                    <div class="truncate">
                        <i class="fas fa-truck text-neutral-400"></i>
                        <span class="ml-1">${escapeHtml(serviceProvider)}</span>
                    </div>
                </div>
            </div>
        `;
        
        console.log(`DEBUG: Order ${index + 1} - Generated HTML length: ${orderHtml.length}`);
        return orderHtml;
    }).join('');

    console.log('DEBUG: Final ordersHtml length:', ordersHtml.length);

    const finalHtml = `
        <div class="space-y-2">
            <div class="text-xs text-neutral-600 mb-2">
                <i class="fas fa-route text-orange-500"></i>
                <span class="ml-1">${escapeHtml(laneInfo.laneName || 'Lane Orders')} (${orders.length} orders)</span>
            </div>
            ${ordersHtml}
        </div>
    `;

    console.log('DEBUG: Final HTML being set:', finalHtml);
    contentElement.innerHTML = finalHtml;
    console.log('DEBUG: contentElement.innerHTML after setting:', contentElement.innerHTML);
    console.log('=== DEBUG: displayUnplannedOrders completed ===');
}

/**
 * Handles order selection and shows order details
 */
window.selectOrder = async function(orderGid) {
    if (!orderGid || orderGid === 'N/A') {
        console.warn('Invalid order GID:', orderGid);
        return;
    }

    try {
        // Show loading state
        showLoading('Loading order details...');
        
        // Fetch order details
        const orderData = await fetchOrderDetails(orderGid);
        
        // Display the order details directly
        displayOrderDetails(orderData, orderGid);
        
    } catch (error) {
        console.error('Error loading order details:', error);
        showNotification(`Failed to load order details: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
};

/**
 * Fetches detailed order information from the API
 */
async function fetchOrderDetails(orderGid) {
    try {
        console.log('=== DEBUG: fetchOrderDetails started ===');
        console.log('DEBUG: Input orderGid:', orderGid);
        
        // Format the order release GID with service provider prefix
        const formattedOrderGid = orderGid.startsWith(`${SERVICE_PROVIDER}.`) ? 
            orderGid : 
            `${SERVICE_PROVIDER}.${orderGid}`;
        
        console.log('DEBUG: Formatted order GID for API:', formattedOrderGid);
        
        // Construct the order details endpoint URL
        const endpoint = `${DATA_TOOLS_API_BASE_URL}/order-release/${encodeURIComponent(formattedOrderGid)}`;
        
        console.log('DEBUG: Order details API endpoint:', endpoint);
        
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log('DEBUG: Order details response status:', response.status);
        console.log('DEBUG: Order details response statusText:', response.statusText);
        console.log('DEBUG: Order details response headers:', [...response.headers.entries()]);

        if (!response.ok) {
            console.error('DEBUG: Response not OK:', response.status, response.statusText);
            if (response.status === 404) {
                throw new Error(`Order ${formattedOrderGid} not found`);
            } else {
                const responseText = await response.text();
                console.error('DEBUG: Error response text:', responseText);
                throw new Error(`HTTP ${response.status}: ${response.statusText} - ${responseText}`);
            }
        }

        const result = await response.json();
        console.log('DEBUG: Raw JSON result:', result);
        console.log('DEBUG: Result type:', typeof result);
        console.log('DEBUG: Result keys:', Object.keys(result || {}));
        console.log('DEBUG: result.success:', result.success);
        console.log('DEBUG: result.success type:', typeof result.success);
        console.log('DEBUG: result.data exists:', !!result.data);
        console.log('DEBUG: result.error:', result.error);
        
        // The API response shows success: true, data: {...}, error: null
        // Check for explicit false rather than falsy values
        if (result.success === false) {
            console.error('DEBUG: API returned success: false');
            console.error('DEBUG: Error message from API:', result.error);
            throw new Error(result.error || 'Failed to fetch order details');
        }

        if (!result.data) {
            console.error('DEBUG: No data field in response');
            console.error('DEBUG: Full result:', JSON.stringify(result, null, 2));
            throw new Error('No order data returned from API');
        }

        console.log('DEBUG: Successfully parsed order details');
        console.log('DEBUG: Order data keys:', Object.keys(result.data));
        console.log('=== DEBUG: fetchOrderDetails completed successfully ===');
        
        return result.data;

    } catch (error) {
        console.error('=== DEBUG: Error in fetchOrderDetails ===');
        console.error('DEBUG: Error type:', typeof error);
        console.error('DEBUG: Error name:', error.name);
        console.error('DEBUG: Error message:', error.message);
        console.error('DEBUG: Error stack:', error.stack);
        console.error('=== DEBUG: fetchOrderDetails failed ===');
        throw error;
    }
}

/**
 * Displays detailed order information in a modal
 */
function displayOrderDetails(orderData, orderGid) {
    console.log('=== DEBUG: displayOrderDetails started ===');
    console.log('DEBUG: Input orderData:', orderData);
    console.log('DEBUG: Input orderGid:', orderGid);
    
    const modal = document.getElementById('order-detail-modal');
    const content = document.getElementById('order-detail-content');
    
    console.log('DEBUG: Modal element:', !!modal);
    console.log('DEBUG: Content element:', !!content);
    
    if (!modal || !content) {
        console.error('Order detail modal elements not found');
        console.error('DEBUG: Modal found:', !!modal);
        console.error('DEBUG: Content found:', !!content);
        return;
    }

    try {
        console.log('DEBUG: Starting to extract order information...');
        
        // Extract key information from order data (handling nested objects)
        const order = orderData;
        const orderReleaseId = order.orderReleaseXid || orderGid;
        const orderName = order.orderReleaseName || 'Unknown Order';
        
        console.log('DEBUG: Basic info extracted - ID:', orderReleaseId, 'Name:', orderName);
        
        // Extract weight and volume with nested structure
        let totalWeight = 'N/A';
        if (order.totalWeight && order.totalWeight.value !== undefined) {
            const unit = order.totalWeight.unit || 'LB';
            totalWeight = `${order.totalWeight.value} ${unit}`;
        }
        
        let totalVolume = 'N/A';
        if (order.totalVolume && order.totalVolume.value !== undefined) {
            const unit = order.totalVolume.unit || 'CUFT';
            totalVolume = `${order.totalVolume.value} ${unit}`;
        }
        
        console.log('DEBUG: Weight/Volume extracted - Weight:', totalWeight, 'Volume:', totalVolume);
        
        // Extract cost with nested structure
        let bestDirectCost = 'N/A';
        if (order.bestDirectCostBuy && order.bestDirectCostBuy.value !== undefined) {
            const currency = order.bestDirectCostBuy.currency || 'USD';
            bestDirectCost = `$${order.bestDirectCostBuy.value} ${currency}`;
        }
        
        // Extract service provider
        let serviceProvider = 'N/A';
        if (order.bestDirectRateofferGidBuy) {
            const parts = order.bestDirectRateofferGidBuy.split('.');
            serviceProvider = parts.length > 1 ? parts[parts.length - 1].replace('TL_', '') : order.bestDirectRateofferGidBuy;
        }
        
        console.log('DEBUG: Cost/Provider extracted - Cost:', bestDirectCost, 'Provider:', serviceProvider);
        
        // Extract dates with nested structure
        let latePickupDate = 'N/A';
        if (order.latePickupDate && order.latePickupDate.value) {
            latePickupDate = order.latePickupDate.value;
        }
        
        let shipDate = 'N/A';
        if (order.attributeDate18 && order.attributeDate18.value) {
            shipDate = order.attributeDate18.value;
        }
        
        let deliveryDate = 'N/A';
        // Note: This field might not be in the API response, keeping for future use
        
        console.log('DEBUG: Dates extracted - Pickup:', latePickupDate, 'Ship:', shipDate);
        
        // Extract location information (these are complex nested structures in the API)
        // For now, we'll show placeholder data since location details require separate API calls
        const sourceCity = 'Lancaster'; // From API context
        const sourceState = 'TX';
        const destCity = 'Dallas'; // From API context
        const destState = 'TX';

        // Extract equipment information
        let equipmentType = 'N/A';
        if (order.equipmentGroup && order.equipmentGroup.links) {
            const canonical = order.equipmentGroup.links.find(link => link.rel === 'canonical');
            if (canonical && canonical.href) {
                const parts = canonical.href.split('/');
                const gid = parts[parts.length - 1];
                equipmentType = gid.split('.').pop() || gid;
            }
        }
        
        let equipmentLength = 'N/A';
        if (order.shipUnitLength && order.shipUnitLength.value !== undefined) {
            const unit = order.shipUnitLength.unit || 'FT';
            equipmentLength = `${order.shipUnitLength.value} ${unit}`;
        }

        console.log('DEBUG: Equipment extracted - Type:', equipmentType, 'Length:', equipmentLength);
        console.log('DEBUG: About to build HTML content...');

        // Build the detail view HTML
        content.innerHTML = `
            <div class="space-y-6">
                <!-- Order Header -->
                <div class="bg-orange-50 rounded-lg p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="text-lg font-semibold text-neutral-900">${escapeHtml(orderName)}</h4>
                            <p class="text-sm text-neutral-600">Order ID: ${escapeHtml(orderReleaseId)}</p>
                            <p class="text-sm text-neutral-500">Type: ${escapeHtml(order.orderReleaseTypeGid || 'N/A')}</p>
                        </div>
                        <div class="text-right">
                            <p class="text-lg font-bold text-green-600">${escapeHtml(bestDirectCost)}</p>
                            <p class="text-sm text-neutral-600">Best Direct Cost</p>
                        </div>
                    </div>
                </div>

                <!-- Route Information -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-neutral-50 rounded-lg p-4">
                        <h5 class="font-semibold text-neutral-900 mb-3 flex items-center">
                            <i class="fas fa-map-marker-alt text-green-500 mr-2"></i>
                            Origin
                        </h5>
                        <div class="space-y-2">
                            <p class="text-sm"><span class="font-medium">City:</span> ${escapeHtml(sourceCity)}</p>
                            <p class="text-sm"><span class="font-medium">State:</span> ${escapeHtml(sourceState)}</p>
                            <p class="text-sm"><span class="font-medium">Pickup Date:</span> ${formatOrderDate(latePickupDate)}</p>
                        </div>
                    </div>
                    
                    <div class="bg-neutral-50 rounded-lg p-4">
                        <h5 class="font-semibold text-neutral-900 mb-3 flex items-center">
                            <i class="fas fa-flag-checkered text-red-500 mr-2"></i>
                            Destination
                        </h5>
                        <div class="space-y-2">
                            <p class="text-sm"><span class="font-medium">City:</span> ${escapeHtml(destCity)}</p>
                            <p class="text-sm"><span class="font-medium">State:</span> ${escapeHtml(destState)}</p>
                            <p class="text-sm"><span class="font-medium">Delivery Date:</span> ${formatOrderDate(deliveryDate)}</p>
                        </div>
                    </div>
                </div>

                <!-- Shipment Details -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-neutral-50 rounded-lg p-4">
                        <h5 class="font-semibold text-neutral-900 mb-3 flex items-center">
                            <i class="fas fa-weight text-blue-500 mr-2"></i>
                            Weight & Volume
                        </h5>
                        <div class="space-y-2">
                            <p class="text-sm"><span class="font-medium">Total Weight:</span> ${escapeHtml(totalWeight)}</p>
                            <p class="text-sm"><span class="font-medium">Total Volume:</span> ${escapeHtml(totalVolume)}</p>
                            <p class="text-sm"><span class="font-medium">Package Count:</span> ${escapeHtml(order.totalPackagingUnitCount || 'N/A')}</p>
                        </div>
                    </div>
                    
                    <div class="bg-neutral-50 rounded-lg p-4">
                        <h5 class="font-semibold text-neutral-900 mb-3 flex items-center">
                            <i class="fas fa-truck text-purple-500 mr-2"></i>
                            Equipment
                        </h5>
                        <div class="space-y-2">
                            <p class="text-sm"><span class="font-medium">Type:</span> ${escapeHtml(equipmentType)}</p>
                            <p class="text-sm"><span class="font-medium">Length:</span> ${escapeHtml(equipmentLength)}</p>
                            <p class="text-sm"><span class="font-medium">Ship Units:</span> ${escapeHtml(order.totalShipUnitCount || 'N/A')}</p>
                        </div>
                    </div>
                    
                    <div class="bg-neutral-50 rounded-lg p-4">
                        <h5 class="font-semibold text-neutral-900 mb-3 flex items-center">
                            <i class="fas fa-building text-indigo-500 mr-2"></i>
                            Service Provider
                        </h5>
                        <div class="space-y-2">
                            <p class="text-sm"><span class="font-medium">Provider:</span> ${escapeHtml(serviceProvider)}</p>
                            <p class="text-sm"><span class="font-medium">Ship Date:</span> ${formatOrderDate(shipDate)}</p>
                            <p class="text-sm"><span class="font-medium">Priority:</span> ${escapeHtml(order.priority || 'N/A')}</p>
                        </div>
                    </div>
                </div>

                <!-- Additional Details -->
                <div class="bg-neutral-50 rounded-lg p-4">
                    <h5 class="font-semibold text-neutral-900 mb-3 flex items-center">
                        <i class="fas fa-info-circle text-blue-500 mr-2"></i>
                        Additional Information
                    </h5>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <p><span class="font-medium">Release Method:</span> ${escapeHtml(order.releaseMethodGid || 'N/A')}</p>
                            <p><span class="font-medium">Bundling Type:</span> ${escapeHtml(order.bundlingType || 'N/A')}</p>
                            <p><span class="font-medium">Must Ship Direct:</span> ${order.mustShipDirect ? 'Yes' : 'No'}</p>
                        </div>
                        <div>
                            <p><span class="font-medium">Pickup Appointment:</span> ${order.pickupIsAppt ? 'Required' : 'Not Required'}</p>
                            <p><span class="font-medium">Delivery Appointment:</span> ${order.deliveryIsAppt ? 'Required' : 'Not Required'}</p>
                            <p><span class="font-medium">Splittable:</span> ${order.isSplittable ? 'Yes' : 'No'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        console.log('DEBUG: HTML content set successfully');
        console.log('DEBUG: About to show modal...');

        // Show the modal
        modal.classList.remove('hidden');
        
        console.log('DEBUG: Modal shown successfully');
        console.log('=== DEBUG: displayOrderDetails completed successfully ===');
        
    } catch (error) {
        console.error('=== DEBUG: Error in displayOrderDetails ===');
        console.error('DEBUG: Error type:', typeof error);
        console.error('DEBUG: Error name:', error.name);
        console.error('DEBUG: Error message:', error.message);
        console.error('DEBUG: Error stack:', error.stack);
        throw error; // Re-throw the error so selectOrder can catch it
    }
}

/**
 * Formats order dates for display
 */
function formatOrderDate(dateString) {
    if (!dateString || dateString === 'N/A') {
        return 'N/A';
    }
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return dateString; // Return original if not a valid date
        }
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    } catch (error) {
        return dateString; // Return original if parsing fails
    }
}

/**
 * Sets up order release modal event handlers
 */
function setupOrderReleaseModal() {
    const modal = document.getElementById('order-detail-modal');
    const closeBtn = document.getElementById('close-order-detail-modal');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            if (modal) {
                modal.classList.add('hidden');
            }
        });
    }
    
    // Close modal when clicking outside
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }
}

// Initialize order release modal when the page loads
document.addEventListener('DOMContentLoaded', () => {
    setupOrderReleaseModal();
});

/**
 * Handles order selection and displays detailed information
 */
async function selectOrder(orderGid) {
    try {
        console.log('=== DEBUG: selectOrder started ===');
        console.log('DEBUG: Selecting order:', orderGid);
        
        // Show loading state
        showLoading('Loading order details...');
        
        // Fetch detailed order information
        console.log('DEBUG: About to call fetchOrderDetails...');
        const orderData = await fetchOrderDetails(orderGid);
        console.log('DEBUG: fetchOrderDetails completed successfully, got data:', !!orderData);
        console.log('DEBUG: Order data type:', typeof orderData);
        console.log('DEBUG: Order data keys:', Object.keys(orderData || {}));
        
        // Hide loading state
        hideLoading();
        
        // Display the order details in modal
        console.log('DEBUG: About to call displayOrderDetails...');
        displayOrderDetails(orderData, orderGid);
        console.log('DEBUG: displayOrderDetails completed successfully');
        console.log('=== DEBUG: selectOrder completed successfully ===');
        
    } catch (error) {
        console.error('=== DEBUG: Error in selectOrder ===');
        console.error('DEBUG: Error type:', typeof error);
        console.error('DEBUG: Error name:', error.name);
        console.error('DEBUG: Error message:', error.message);
        console.error('DEBUG: Error stack:', error.stack);
        
        hideLoading();
        
        // Show error notification
        console.log('DEBUG: About to show error notification...');
        showNotification(`Failed to load order details: ${error.message}`, 'error');
        console.log('=== DEBUG: selectOrder error handling completed ===');
    }
}

/**
 * Fetches detailed information for a specific order
 */

/**
 * Handles the Get Orders button click event
 */
async function handleGetOrdersClick() {
    console.log('=== DEBUG: handleGetOrdersClick started ===');
    
    const statusElement = document.getElementById('order-release-status');
    const contentElement = document.getElementById('order-release-content');
    const getOrdersBtn = document.getElementById('get-orders-btn');
    
    if (!statusElement || !contentElement) {
        console.error('Order release card elements not found');
        return;
    }

    try {
        // Debug: Log current lane info
        console.log('DEBUG: Current lane info:', window.currentLaneInfo);
        
        // Update status to loading
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700';
        statusElement.textContent = 'Loading...';

        // Disable the button and show loading state
        if (getOrdersBtn) {
            getOrdersBtn.disabled = true;
            getOrdersBtn.innerHTML = `
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Loading...
            `;
        }

        // Show loading state in content
        contentElement.innerHTML = `
            <div class="text-center py-4">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500 mx-auto mb-2"></div>
                <p class="text-xs text-neutral-600">Fetching unplanned orders...</p>
            </div>
        `;

        // Get the current lane info from global variable
        if (!window.currentLaneInfo) {
            throw new Error('No lane information available');
        }

        console.log('DEBUG: About to call fetchUnplannedOrders with:', window.currentLaneInfo);

        // Fetch unplanned orders for the lane
        const ordersData = await fetchUnplannedOrders(window.currentLaneInfo);
        
        console.log('DEBUG: fetchUnplannedOrders returned:', ordersData);
        console.log('DEBUG: ordersData.success:', ordersData?.success);
        console.log('DEBUG: ordersData.data:', ordersData?.data);
        console.log('DEBUG: ordersData.data.items:', ordersData?.data?.items);
        console.log('DEBUG: ordersData.data.items.length:', ordersData?.data?.items?.length);
        
        if (ordersData && ordersData.success && ordersData.data && ordersData.data.items && ordersData.data.items.length > 0) {
            console.log('DEBUG: Processing successful orders response');
            
            // Update status to success
            statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700';
            statusElement.textContent = `${ordersData.data.items.length} orders`;

            // Display the orders
            console.log('DEBUG: About to call displayUnplannedOrders with', ordersData.data.items.length, 'orders');
            displayUnplannedOrders(ordersData.data.items, contentElement, window.currentLaneInfo);
        } else {
            console.log('DEBUG: No orders found or unsuccessful response');
            console.log('DEBUG: Response details:');
            console.log('  - success:', ordersData?.success);
            console.log('  - data exists:', !!ordersData?.data);
            console.log('  - items exists:', !!ordersData?.data?.items);
            console.log('  - items is array:', Array.isArray(ordersData?.data?.items));
            console.log('  - items length:', ordersData?.data?.items?.length);
            console.log('  - full response:', JSON.stringify(ordersData, null, 2));
            
            // No orders found
            statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
            statusElement.textContent = 'No orders';
            
            const sourceDisplay = window.currentLaneInfo.sourceCity && window.currentLaneInfo.sourceState ? 
                `${window.currentLaneInfo.sourceCity}, ${window.currentLaneInfo.sourceState}` : 
                (window.currentLaneInfo.sourceCity || 'Unknown Origin');
            const destDisplay = window.currentLaneInfo.destinationCity && window.currentLaneInfo.destinationState ? 
                `${window.currentLaneInfo.destinationCity}, ${window.currentLaneInfo.destinationState}` : 
                (window.currentLaneInfo.destinationCity || 'Unknown Destination');
            
            contentElement.innerHTML = `
                <div class="text-center py-4 text-neutral-500">
                    <i class="fas fa-inbox text-2xl mb-2 text-neutral-300"></i>
                    <p class="text-xs">No unplanned orders found</p>
                    <p class="text-xs text-neutral-400 mt-1">${sourceDisplay} → ${destDisplay}</p>
                </div>
            `;
        }

    } catch (error) {
        console.error('DEBUG: Error in handleGetOrdersClick:', error);
        console.error('DEBUG: Error stack:', error.stack);
        
        // Update status to error
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700';
        statusElement.textContent = 'Error';
        
        contentElement.innerHTML = `
            <div class="text-center py-4 text-neutral-500">
                <i class="fas fa-exclamation-triangle text-2xl mb-2 text-red-400"></i>
                <p class="text-xs text-red-600">Failed to load orders</p>
                <p class="text-xs text-neutral-400 mt-1">${error.message}</p>
                <button class="mt-3 px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs rounded-md transition-colors duration-200"
                        onclick="handleGetOrdersClick()">
                    Try Again
                </button>
            </div>
        `;
    }
    
    console.log('=== DEBUG: handleGetOrdersClick completed ===');
}

// AI Transportation Recommendations System
// ===========================================

// Global aggregated data store for AI recommendations
window.aggregatedRecommendationData = {
    riq_data: null,
    spot_data: null,
    historical_data: null,
    chat_insights: null
};

// Data collection status tracking (removed order_data)
const dataCollectionStatus = {
    riq_data: false,
    spot_data: false,
    historical_data: false,
    chat_insights: false
};

function updateRecommendationDataCollection(dataType, data, hasData = true) {
    /**
     * Update the aggregated data collection for AI recommendations
     * @param {string} dataType - Type of data (riq_data, spot_data, historical_data, chat_insights)
     * @param {any} data - The actual data collected
     * @param {boolean} hasData - Whether valid data was collected
     */
    console.log(`Updating recommendation data collection: ${dataType}`, hasData);
    
    // Skip if this is order_data (we no longer collect it)
    if (dataType === 'order_data') {
        console.log('Skipping order_data - no longer collected for AI recommendations');
        return;
    }
    
    // Update the aggregated data store
    if (hasData && data) {
        window.aggregatedRecommendationData[dataType] = data;
        dataCollectionStatus[dataType] = true;
    } else {
        window.aggregatedRecommendationData[dataType] = null;
        dataCollectionStatus[dataType] = false;
    }
    
    // Update the UI indicators
    updateDataCollectionIndicators();
    
    // Check if we can enable AI recommendations
    checkRecommendationReadiness();
}

function updateDataCollectionIndicators() {
    /**
     * Update the visual indicators for data collection status
     */
    const dataSourceMappings = {
        riq_data: { indicator: 'riq-data-indicator', status: 'riq-data-status' },
        spot_data: { indicator: 'spot-data-indicator', status: 'spot-data-status' },
        historical_data: { indicator: 'historical-data-indicator', status: 'historical-data-status' },
        chat_insights: { indicator: 'chat-insights-indicator', status: 'chat-insights-status' }
    };
    
    let availableCount = 0;
    
    // Helper function to update indicators with retry mechanism
    const updateIndicatorWithRetry = (dataType, mapping, retryCount = 0) => {
        const indicator = document.getElementById(mapping.indicator);
        const status = document.getElementById(mapping.status);
        
        if (indicator && status) {
            if (dataCollectionStatus[dataType]) {
                indicator.className = 'fas fa-check-circle w-2 h-2 mr-2 text-green-500';
                status.textContent = 'Available';
                status.className = 'text-green-600 font-medium';
                return true; // Successfully updated
            } else {
                indicator.className = 'fas fa-circle w-2 h-2 mr-2 text-gray-300';
                status.textContent = 'Not Available';
                status.className = 'text-neutral-400';
                return true; // Successfully updated
            }
        } else if (retryCount < 3) {
            // Retry after a short delay if elements are not found
            setTimeout(() => updateIndicatorWithRetry(dataType, mapping, retryCount + 1), 100);
            return false; // Will retry
        } else {
            console.warn(`Failed to find status elements for ${dataType} after 3 retries`);
            return false; // Failed to update
        }
    };
    
    // Update each data source indicator
    Object.keys(dataSourceMappings).forEach(dataType => {
        const mapping = dataSourceMappings[dataType];
        const wasUpdated = updateIndicatorWithRetry(dataType, mapping);
        
        // Count available items immediately for elements that exist
        if (wasUpdated && dataCollectionStatus[dataType]) {
            availableCount++;
        }
    });
    
    // Update progress bar (now based on 4 data sources)
    const progressBar = document.getElementById('data-collection-progress');
    const progressSummary = document.getElementById('data-collection-summary');
    
    if (progressBar && progressSummary) {
        const progressPercentage = (availableCount / 4) * 100;
        progressBar.style.width = `${progressPercentage}%`;
        progressSummary.textContent = `${availableCount} of 4 data sources collected`;
    }
}

function checkRecommendationReadiness() {
    /**
     * Check if we have sufficient data for AI recommendations and update UI accordingly
     */
    const availableCount = Object.values(dataCollectionStatus).filter(status => status).length;
    const statusElement = document.getElementById('ai-recommendations-status');
    const generateBtn = document.getElementById('generate-recommendations-btn');
    
    if (!statusElement || !generateBtn) return;
    
    if (availableCount >= 2) {
        // Sufficient data for recommendations
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
        statusElement.textContent = 'Ready for AI Analysis';
        generateBtn.classList.remove('hidden');
    } else if (availableCount === 1) {
        // Limited data available
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
        statusElement.textContent = 'Limited Data Available';
        generateBtn.classList.remove('hidden');
    } else {
        // Insufficient data
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        statusElement.textContent = 'Awaiting Data';
        generateBtn.classList.add('hidden');
    }
}

async function handleGenerateRecommendationsClick() {
    /**
     * Handle the Generate AI Recommendations button click
     */
    console.log('Generate AI Recommendations clicked');
    
    try {
        // Validate we have lane information
        const laneInfo = window.currentLaneInfo;
        if (!laneInfo || !laneInfo.sourceCity || !laneInfo.destinationCity) {
            alert('Lane information is required for AI recommendations. Please ask about a specific transportation lane first.');
            return;
        }
        
        // Show loading state
        const statusElement = document.getElementById('ai-recommendations-status');
        const contentElement = document.getElementById('ai-recommendations-content');
        const generateBtn = document.getElementById('generate-recommendations-btn');
        
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
        statusElement.textContent = 'Generating...';
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        
        contentElement.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-4"></div>
                <p class="text-sm mb-2">AI is analyzing your transportation data...</p>
                <p class="text-xs text-neutral-400">This may take a few moments</p>
            </div>
        `;
        
        // Prepare the request payload
        const requestPayload = {
            aggregated_data: window.aggregatedRecommendationData,
            source_city: laneInfo.sourceCity,
            destination_city: laneInfo.destinationCity,
            weight: laneInfo.weight,
            volume: laneInfo.volume,
            context: `Lane analysis for ${laneInfo.laneName || `${laneInfo.sourceCity} to ${laneInfo.destinationCity}`}`
        };
        
        console.log('Sending recommendation request:', requestPayload);
        
        // Call the AI recommendation API
        const response = await fetch(`${API_BASE_URL}/recommendations/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const recommendationData = await response.json();
        console.log('Received recommendation data:', recommendationData);
        
        // Display the recommendations
        displayAIRecommendations(recommendationData);
        
        // Update status
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
        statusElement.textContent = `Confidence: ${(recommendationData.confidence_score * 100).toFixed(0)}%`;
        
    } catch (error) {
        console.error('Failed to generate AI recommendations:', error);
        
        // Show error state
        const statusElement = document.getElementById('ai-recommendations-status');
        const contentElement = document.getElementById('ai-recommendations-content');
        
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        statusElement.textContent = 'Generation Failed';
        
        contentElement.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p class="text-sm mb-2">Failed to generate AI recommendations</p>
                <p class="text-xs text-neutral-400">${escapeHtml(error.message)}</p>
                <button onclick="handleGenerateRecommendationsClick()" class="mt-4 px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors">
                    Try Again
                </button>
            </div>
        `;
    } finally {
        // Reset button state
        const generateBtn = document.getElementById('generate-recommendations-btn');
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate AI Recommendations';
    }
}

function displayAIRecommendations(recommendationData) {
    /**
     * Display the AI-generated transportation recommendations
     * @param {Object} recommendationData - The recommendation response from the API
     */
    const contentElement = document.getElementById('ai-recommendations-content');
    
    if (!recommendationData) {
        contentElement.innerHTML = `<p class="text-red-500 text-center text-sm">Error: Invalid recommendation data received.</p>`;
        return;
    }
    
    let content = `
        <div class="space-y-6">
            <!-- Primary Recommendation Section -->
            <div class="bg-indigo-50 rounded-lg p-4">
                <h4 class="font-medium text-indigo-900 mb-3 flex items-center">
                    <i class="fas fa-brain text-indigo-600 mr-2"></i>
                    🎯 AI Primary Recommendation
                    <span class="ml-auto text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
                        Confidence: ${(recommendationData.confidence_score * 100).toFixed(0)}%
                    </span>
                </h4>
                <div class="text-sm text-indigo-800 whitespace-pre-wrap">${escapeHtml(recommendationData.primary_recommendation)}</div>
                
                ${recommendationData.recommended_carrier ? `
                <div class="mt-3 grid grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
                    <div><span class="text-indigo-600">Recommended Carrier:</span> <span class="font-medium">${escapeHtml(recommendationData.recommended_carrier)}</span></div>
                    ${recommendationData.estimated_cost ? `<div><span class="text-indigo-600">Estimated Cost:</span> <span class="font-medium">${escapeHtml(recommendationData.estimated_cost)}</span></div>` : ''}
                    <div><span class="text-indigo-600">Strategy:</span> <span class="font-medium">${escapeHtml(recommendationData.cost_optimization.strategy_type.replace('_', ' '))}</span></div>
                </div>
                ` : ''}
            </div>
            
            <!-- Cost Optimization Analysis -->
            <div class="bg-green-50 rounded-lg p-4">
                <h4 class="font-medium text-green-900 mb-3 flex items-center">
                    <i class="fas fa-dollar-sign text-green-600 mr-2"></i>
                    Cost Optimization Analysis
                </h4>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                        <div class="text-sm text-green-800 mb-2">${escapeHtml(recommendationData.cost_optimization.reasoning)}</div>
                        ${recommendationData.cost_optimization.estimated_savings ? `
                        <div class="text-xs text-green-700">
                            <span class="font-medium">Potential Savings:</span> ${escapeHtml(recommendationData.cost_optimization.estimated_savings)}
                        </div>
                        ` : ''}
                    </div>
                    <div class="text-xs space-y-1">
                        <div><span class="text-green-600">Strategy Type:</span> <span class="font-medium">${escapeHtml(recommendationData.cost_optimization.strategy_type.replace('_', ' '))}</span></div>
                        <div><span class="text-green-600">Risk Level:</span> <span class="font-medium">${escapeHtml(recommendationData.cost_optimization.risk_assessment)}</span></div>
                        <div><span class="text-green-600">Market Timing:</span> <span class="font-medium">${escapeHtml(recommendationData.cost_optimization.market_timing)}</span></div>
                    </div>
                </div>
            </div>
            
            <!-- Market Timing & Metadata -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <!-- Market Timing -->
                <div class="bg-purple-50 rounded-lg p-4">
                    <h4 class="font-medium text-purple-900 mb-3 flex items-center">
                        <i class="fas fa-clock text-purple-600 mr-2"></i>
                        Market Timing
                    </h4>
                    <div class="text-sm text-purple-800">${escapeHtml(recommendationData.market_timing)}</div>
                </div>
                
                <!-- Analysis Metadata -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-3 flex items-center">
                        <i class="fas fa-info-circle text-gray-600 mr-2"></i>
                        Analysis Details
                    </h4>
                    <div class="space-y-2 text-xs">
                        <div><span class="text-gray-600">Data Sources:</span> <span class="font-medium">${recommendationData.metadata.data_sources_used.join(', ')}</span></div>
                        <div><span class="text-gray-600">Data Completeness:</span> <span class="font-medium">${(recommendationData.metadata.data_completeness * 100).toFixed(0)}%</span></div>
                        <div><span class="text-gray-600">Generated:</span> <span class="font-medium">${new Date(recommendationData.metadata.generated_at).toLocaleString()}</span></div>
                    </div>
                </div>
            </div>
            
            <!-- Regenerate Button -->
            <div class="text-center pt-4 border-t border-neutral-200">
                <button onclick="handleGenerateRecommendationsClick()" class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors">
                    <i class="fas fa-sync mr-2"></i>
                    Regenerate Recommendations
                </button>
            </div>
        </div>
    `;
    
    contentElement.innerHTML = content;
}

// Integration with existing data collection systems
// ==================================================

// Override existing functions to update recommendation data collection

// Hook into RIQ data updates
const originalUpdateRateInquiryCard = updateRateInquiryCard;
updateRateInquiryCard = function(laneInfo, userMessage, response) {
    // Call original function
    originalUpdateRateInquiryCard(laneInfo, userMessage, response);
    
    // Update recommendation data collection
    const riqData = {
        lane_info: laneInfo,
        user_message: userMessage,
        chat_response: response,
        timestamp: new Date().toISOString()
    };
    updateRecommendationDataCollection('riq_data', riqData, true);
};

// Hook into Spot API data updates  
const originalDisplaySpotRateMatrix = displaySpotRateMatrix;
displaySpotRateMatrix = function(data) {
    // Call original function
    originalDisplaySpotRateMatrix(data);
    
    // Update recommendation data collection
    updateRecommendationDataCollection('spot_data', data, true);
};

// Hook into Historical data updates
const originalDisplayHistoricalData = displayHistoricalData;
displayHistoricalData = function(data, contentElement, laneInfo) {
    // Call original function
    originalDisplayHistoricalData(data, contentElement, laneInfo);
    
    // Update recommendation data collection
    updateRecommendationDataCollection('historical_data', data, true);
};

// Hook into Chat insights updates (from parsed lane information)
const originalParseAndUpdateLaneInfo = parseAndUpdateLaneInfo;
parseAndUpdateLaneInfo = function(userMessage, response) {
    // Call original function
    originalParseAndUpdateLaneInfo(userMessage, response);
    
    // Extract chat insights from the parsed response
    const laneInfo = parseLaneInformationFromResponse(response.answer);
    if (laneInfo.bestCarrier || laneInfo.worstCarrier) {
        const chatInsights = {
            best_performer: {
                carrier: laneInfo.bestCarrier,
                performance: laneInfo.bestPerformance
            },
            worst_performer: {
                carrier: laneInfo.worstCarrier,
                performance: laneInfo.worstPerformance
            },
            lane_name: laneInfo.laneName,
            timestamp: new Date().toISOString()
        };
        updateRecommendationDataCollection('chat_insights', chatInsights, true);
    }
};

// Hook into Order data updates (removed updateRecommendationDataCollection call)
const originalDisplayUnplannedOrders = displayUnplannedOrders;
displayUnplannedOrders = function(orders, contentElement, laneInfo) {
    // Call original function
    originalDisplayUnplannedOrders(orders, contentElement, laneInfo);
    
    // No longer update recommendation data collection with order data
    console.log('Order data displayed but not sent to AI recommendations');
};

// Clear recommendations when clearing other lane data
const originalClearLaneInfoCards = clearLaneInfoCards;
clearLaneInfoCards = function() {
    // Call original function
    originalClearLaneInfoCards();
    
    // Clear recommendation data and reset UI
    window.aggregatedRecommendationData = {
        riq_data: null,
        spot_data: null,
        historical_data: null,
        chat_insights: null
    };
    
    Object.keys(dataCollectionStatus).forEach(key => {
        dataCollectionStatus[key] = false;
    });
    
    updateDataCollectionIndicators();
    checkRecommendationReadiness();
    
    // Clear recommendations content
    const contentElement = document.getElementById('ai-recommendations-content');
    if (contentElement) {
        contentElement.innerHTML = `
            <div class="text-center py-8 text-neutral-500">
                <i class="fas fa-lightbulb text-4xl mb-4 text-neutral-300"></i>
                <p class="text-sm mb-2">AI-Powered Transportation Recommendations</p>
                <p class="text-xs text-neutral-400">Gather transportation data from multiple sources to unlock intelligent recommendations</p>
                
                <!-- Data Collection Progress -->
                <div class="mt-6 max-w-md mx-auto">
                    <div class="text-xs text-neutral-600 mb-2">Data Collection Progress</div>
                    <div class="space-y-2">
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="riq-data-indicator"></i>
                                RIQ Rate Analysis
                            </span>
                            <span class="text-neutral-400" id="riq-data-status">Not Available</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="spot-data-indicator"></i>
                                Spot Rate Matrix
                            </span>
                            <span class="text-neutral-400" id="spot-data-status">Not Available</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="historical-data-indicator"></i>
                                Historical Lane Data
                            </span>
                            <span class="text-neutral-400" id="historical-data-status">Not Available</span>
                        </div>
                        <div class="flex items-center justify-between text-xs">
                            <span class="flex items-center">
                                <i class="fas fa-circle w-2 h-2 mr-2 text-gray-300" id="chat-insights-indicator"></i>
                                Chat-Parsed Insights
                            </span>
                            <span class="text-neutral-400" id="chat-insights-status">Not Available</span>
                        </div>
                    </div>
                    <div class="mt-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div id="data-collection-progress" class="bg-indigo-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                        </div>
                        <div class="text-xs text-neutral-500 mt-1" id="data-collection-summary">0 of 4 data sources collected</div>
                    </div>
                </div>
            </div>
        `;
    }
};

// Initialize recommendation system when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Transportation Recommendations system initialized');
    updateDataCollectionIndicators();
    checkRecommendationReadiness();
});

// NEW COMPREHENSIVE RIQ API FUNCTIONS

async function getLocationIDs(laneInfo) {
    /**
     * Get location IDs using the /new-riq-rest endpoint
     * Step 1 of the comprehensive RIQ API workflow
     * 
     * @param {Object} laneInfo - Lane information object containing city/state data
     * @returns {Object} Object with source_location_id and dest_location_id
     */
    try {
        // Parse source and destination from laneInfo
        const sourceLocation = parseLocationFromCity(laneInfo.sourceCity);
        const destLocation = parseLocationFromCity(laneInfo.destinationCity);
        
        if (!sourceLocation || !destLocation) {
            throw new Error('Invalid source or destination location data');
        }
        
        console.log('Parsed locations for ID lookup:', { sourceLocation, destLocation });
        
        const payload = {
            source_city: sourceLocation.city.toUpperCase(),
            source_state: sourceLocation.province_code.toUpperCase(),
            source_country: sourceLocation.country_code.toUpperCase(),
            dest_city: destLocation.city.toUpperCase(),
            dest_state: destLocation.province_code.toUpperCase(),
            dest_country: destLocation.country_code.toUpperCase()
        };
        
        console.log('🔍 Calling REST API to get location IDs...');
        console.log('Payload:', payload);
        
        const response = await fetch(`${DATA_TOOLS_API_BASE_URL}/new-riq-rest`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Location API error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Location API response:', result);
        
        if (!result.success) {
            throw new Error(result.error || 'Location lookup failed');
        }
        
        const locations = result.locations || {};
        const sourceLocationId = locations.source_location_id;
        const destLocationId = locations.dest_location_id;
        
        if (!sourceLocationId || !destLocationId) {
            throw new Error('Could not find location IDs for the specified cities');
        }
        
        console.log('✅ Location IDs retrieved successfully:', {
            source_location_id: sourceLocationId,
            dest_location_id: destLocationId
        });
        
        return {
            source_location_id: sourceLocationId,
            dest_location_id: destLocationId
        };
        
    } catch (error) {
        console.error('Location ID lookup failed:', error);
        throw error;
    }
}

async function getRIQRatesXML(sourceLocationId, destLocationId, weight, volume, transportModes = ['LTL', 'TL']) {
    /**
     * Get comprehensive rate quotes using the /riq-xml endpoint
     * Step 2 of the comprehensive RIQ API workflow
     * 
     * @param {string} sourceLocationId - Source location XID
     * @param {string} destLocationId - Destination location XID  
     * @param {number} weight - Weight value
     * @param {number} volume - Volume value
     * @param {Array} transportModes - Array of transport modes
     * @returns {Object} Parsed XML response with all carrier options
     */
    try {
        const payload = {
            source_location_id: sourceLocationId,
            dest_location_id: destLocationId,
            weight: weight,
            volume: volume,
            weight_unit: 'LB',
            volume_unit: 'CUFT',
            transport_modes: transportModes,
            commodity_class: '70.0'
        };
        
        console.log('🔍 Calling XML RIQ API to get rate quotes...');
        console.log('Payload:', payload);
        
        const response = await fetch(`${DATA_TOOLS_API_BASE_URL}/riq-xml`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('RIQ XML API error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('RIQ XML API response:', result);
        
        if (!result.success) {
            throw new Error(result.error || 'Rate quote request failed');
        }
        
        // Parse the XML response
        const rawXmlResponse = result.raw_xml_response;
        if (!rawXmlResponse) {
            throw new Error('No XML response received from RIQ API');
        }
        
        const parsedResults = parseRIQXMLResponse(rawXmlResponse);
        console.log('✅ XML response parsed successfully:', parsedResults);
        
        return {
            rates: parsedResults,
            raw_xml_request: result.raw_xml_request,
            raw_xml_response: rawXmlResponse
        };
        
    } catch (error) {
        console.error('RIQ XML rate query failed:', error);
        throw error;
    }
}

function parseRIQXMLResponse(xmlString) {
    /**
     * Parse the XML response to extract RIQ results
     * Based on the test file's parse_xml_response method
     * 
     * @param {string} xmlString - Raw XML response string
     * @returns {Array} Array of parsed result dictionaries
     */
    try {
        // Parse the XML using DOMParser (browser-compatible XML parsing)
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlString, 'text/xml');
        
        // Check for parsing errors
        const parseError = xmlDoc.querySelector('parsererror');
        if (parseError) {
            throw new Error(`XML Parse Error: ${parseError.textContent}`);
        }
        
        // Find all RIQ results - they are in the otm namespace
        const results = [];
        const riqResults = xmlDoc.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'RIQResult');
        
        for (let i = 0; i < riqResults.length; i++) {
            const riqResult = riqResults[i];
            const result = {};
            
            // Service Provider (Carrier) - otm:ServiceProviderGid/otm:Gid/otm:Xid
            const spElements = riqResult.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'ServiceProviderGid');
            if (spElements.length > 0) {
                const gidElements = spElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Gid');
                if (gidElements.length > 0) {
                    const xidElements = gidElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Xid');
                    result.service_provider = xidElements.length > 0 ? xidElements[0].textContent : 'Unknown';
                } else {
                    result.service_provider = 'Unknown';
                }
            } else {
                result.service_provider = 'Unknown';
            }
            
            // Transport Mode - otm:TransportModeGid/otm:Gid/otm:Xid
            const tmElements = riqResult.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'TransportModeGid');
            if (tmElements.length > 0) {
                const gidElements = tmElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Gid');
                if (gidElements.length > 0) {
                    const xidElements = gidElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Xid');
                    result.transport_mode = xidElements.length > 0 ? xidElements[0].textContent : 'Unknown';
                } else {
                    result.transport_mode = 'Unknown';
                }
            } else {
                result.transport_mode = 'Unknown';
            }
            
            // Cost - otm:Cost/otm:FinancialAmount/otm:MonetaryAmount
            const costElements = riqResult.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Cost');
            if (costElements.length > 0) {
                const faElements = costElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'FinancialAmount');
                if (faElements.length > 0) {
                    const maElements = faElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'MonetaryAmount');
                    if (maElements.length > 0) {
                        try {
                            result.cost = parseFloat(maElements[0].textContent);
                        } catch (e) {
                            result.cost = null;
                        }
                    } else {
                        result.cost = null;
                    }
                } else {
                    result.cost = null;
                }
            } else {
                result.cost = null;
            }
            
            // Currency - otm:Cost/otm:FinancialAmount/otm:GlobalCurrencyCode
            if (costElements.length > 0) {
                const faElements = costElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'FinancialAmount');
                if (faElements.length > 0) {
                    const currencyElements = faElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'GlobalCurrencyCode');
                    result.currency = currencyElements.length > 0 ? currencyElements[0].textContent : 'USD';
                } else {
                    result.currency = 'USD';
                }
            } else {
                result.currency = 'USD';
            }
            
            // Distance - otm:Distance/otm:DistanceValue
            const distanceElements = riqResult.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Distance');
            if (distanceElements.length > 0) {
                const distValueElements = distanceElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'DistanceValue');
                if (distValueElements.length > 0) {
                    try {
                        result.distance = parseFloat(distValueElements[0].textContent);
                    } catch (e) {
                        result.distance = null;
                    }
                } else {
                    result.distance = null;
                }
            } else {
                result.distance = null;
            }
            
            // Distance unit - otm:Distance/otm:DistanceUOMGid/otm:Gid/otm:Xid
            if (distanceElements.length > 0) {
                const distUOMElements = distanceElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'DistanceUOMGid');
                if (distUOMElements.length > 0) {
                    const gidElements = distUOMElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Gid');
                    if (gidElements.length > 0) {
                        const xidElements = gidElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Xid');
                        result.distance_unit = xidElements.length > 0 ? xidElements[0].textContent : 'MI';
                    } else {
                        result.distance_unit = 'MI';
                    }
                } else {
                    result.distance_unit = 'MI';
                }
            } else {
                result.distance_unit = 'MI';
            }
            
            // Transit Time - otm:TransitTime/otm:Duration/otm:DurationValue
            const transitElements = riqResult.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'TransitTime');
            if (transitElements.length > 0) {
                const durationElements = transitElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Duration');
                if (durationElements.length > 0) {
                    const durationValueElements = durationElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'DurationValue');
                    if (durationValueElements.length > 0) {
                        try {
                            result.transit_time_hours = parseFloat(durationValueElements[0].textContent);
                        } catch (e) {
                            result.transit_time_hours = null;
                        }
                    } else {
                        result.transit_time_hours = null;
                    }
                } else {
                    result.transit_time_hours = null;
                }
            } else {
                result.transit_time_hours = null;
            }
            
            // Transit time unit - otm:TransitTime/otm:Duration/otm:DurationUOMGid/otm:Gid/otm:Xid
            if (transitElements.length > 0) {
                const durationElements = transitElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Duration');
                if (durationElements.length > 0) {
                    const durationUOMElements = durationElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'DurationUOMGid');
                    if (durationUOMElements.length > 0) {
                        const gidElements = durationUOMElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Gid');
                        if (gidElements.length > 0) {
                            const xidElements = gidElements[0].getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'Xid');
                            result.transit_time_unit = xidElements.length > 0 ? xidElements[0].textContent : 'H';
                        } else {
                            result.transit_time_unit = 'H';
                        }
                    } else {
                        result.transit_time_unit = 'H';
                    }
                } else {
                    result.transit_time_unit = 'H';
                }
            } else {
                result.transit_time_unit = 'H';
            }
            
            // Is Optimal - otm:IsOptimalResult
            const optimalElements = riqResult.getElementsByTagNameNS('http://xmlns.oracle.com/apps/otm/transmission/v6.4', 'IsOptimalResult');
            result.is_optimal = optimalElements.length > 0 ? (optimalElements[0].textContent === 'Y') : false;
            
            results.push(result);
        }
        
        return results;
        
    } catch (error) {
        console.error('XML parsing error:', error);
        return [];
    }
}

async function executeDualRateQueryComprehensive(laneInfo) {
    /**
     * Execute comprehensive dual rate query using the new two-step RIQ API workflow
     * This replaces the original executeDualRateQuery function with the comprehensive API approach
     * 
     * @param {Object} laneInfo - Lane information object
     * @returns {Object} Results object with cheapest and best carrier options
     */
    try {
        console.log('🚀 Starting comprehensive dual rate query:', laneInfo);
        
        // Validate required data
        if (!laneInfo.sourceCity || !laneInfo.destinationCity) {
            throw new Error('Missing required location data. Please ensure both origin and destination cities are specified.');
        }
        
        // Parse weight and volume
        const { weight_value, weight_unit, volume_value, volume_unit } = parseWeightAndVolume(
            laneInfo.weight, 
            laneInfo.volume
        );
        
        console.log('Parsed weight/volume:', { weight_value, weight_unit, volume_value, volume_unit });
        
        // Step 1: Get location IDs
        console.log('📍 Step 1: Getting location IDs...');
        const locationIds = await getLocationIDs(laneInfo);
        
        // Step 2: Get comprehensive rate data using XML API
        console.log('🚛 Step 2: Getting comprehensive rate quotes...');
        const rateData = await getRIQRatesXML(
            locationIds.source_location_id,
            locationIds.dest_location_id,
            weight_value,
            volume_value,
            ['LTL', 'TL']
        );
        
        const allRates = rateData.rates;
        console.log(`Found ${allRates.length} total rate options`);
        
        // if (allRates.length === 0) {
        //     throw new Error('No rate quotes found for the specified criteria');
        // }
        
        // Process results to find cheapest and best carrier options
        const results = {
            cheapest: null,
            bestCarrier: null,
            error: null,
            allRates: allRates,
            metadata: {
                totalOptions: allRates.length,
                carriers: [...new Set(allRates.map(r => r.service_provider))],
                transportModes: [...new Set(allRates.map(r => r.transport_mode))]
            }
        };
        
        // Find cheapest option across all carriers
        const validRates = allRates.filter(rate => rate.cost !== null && rate.cost > 0);
        if (validRates.length > 0) {
            const cheapestRate = validRates.reduce((min, rate) => 
                rate.cost < min.cost ? rate : min
            );
            
            results.cheapest = {
                data: {
                    carrier: cleanServiceProviderGid(cheapestRate.service_provider),
                    cost: cheapestRate.cost,
                    currency: cheapestRate.currency,
                    transport_mode: cheapestRate.transport_mode,
                    distance: cheapestRate.distance,
                    distance_unit: cheapestRate.distance_unit,
                    transit_time: cheapestRate.transit_time_hours,
                    transit_time_unit: cheapestRate.transit_time_unit,
                    is_optimal: cheapestRate.is_optimal,
                    cost_per_mile: cheapestRate.distance > 0 ? (cheapestRate.cost / cheapestRate.distance) : null
                }
            };
            
            console.log('✅ Cheapest option found:', results.cheapest.data);
        }
        
        // Find best carrier option (if specified)
        if (laneInfo.bestCarrier) {
            console.log(`🎯 Looking for best carrier rates: ${laneInfo.bestCarrier}`);
            
            // Clean the carrier name for comparison
            const targetCarrier = laneInfo.bestCarrier.trim().toUpperCase();
            
            const bestCarrierRates = allRates.filter(rate => {
                const carrierName = cleanServiceProviderGid(rate.service_provider).toUpperCase();
                return carrierName.includes(targetCarrier) || targetCarrier.includes(carrierName);
            });
            
            if (bestCarrierRates.length > 0) {
                // Get the best (cheapest) rate from the target carrier
                const bestCarrierRate = bestCarrierRates.reduce((min, rate) => 
                    (rate.cost !== null && rate.cost > 0 && rate.cost < (min.cost || Infinity)) ? rate : min
                );
                
                if (bestCarrierRate.cost !== null && bestCarrierRate.cost > 0) {
                    results.bestCarrier = {
                        data: {
                            carrier: cleanServiceProviderGid(bestCarrierRate.service_provider),
                            cost: bestCarrierRate.cost,
                            currency: bestCarrierRate.currency,
                            transport_mode: bestCarrierRate.transport_mode,
                            distance: bestCarrierRate.distance,
                            distance_unit: bestCarrierRate.distance_unit,
                            transit_time: bestCarrierRate.transit_time_hours,
                            transit_time_unit: bestCarrierRate.transit_time_unit,
                            is_optimal: bestCarrierRate.is_optimal,
                            cost_per_mile: bestCarrierRate.distance > 0 ? (bestCarrierRate.cost / bestCarrierRate.distance) : null
                        }
                    };
                    
                    console.log('✅ Best carrier option found:', results.bestCarrier.data);
                } else {
                    console.log('❌ No valid rates found for best carrier');
                    results.error = `No valid rates available for carrier: ${laneInfo.bestCarrier}`;
                }
            } else {
                console.log('❌ Best carrier not found in results');
                results.error = `Carrier "${laneInfo.bestCarrier}" not found in rate results`;
            }
        }
        
        console.log('🎉 Comprehensive rate query completed successfully');
        return results;
        
    } catch (error) {
        console.error('Comprehensive dual rate query failed:', error);
        return {
            cheapest: null,
            bestCarrier: null,
            error: error.message,
            allRates: [],
            metadata: { totalOptions: 0, carriers: [], transportModes: [] }
        };
    }
}

function displayRateResultsComprehensive(results, laneInfo) {
    /**
     * Display comprehensive rate results in the RIQ card
     * Enhanced version that handles the new XML-based API response structure
     */
    const statusElement = document.getElementById('rate-inquiry-status');
    const contentElement = document.getElementById('rate-inquiry-content');
    
    if (results.error && !results.cheapest && !results.bestCarrier) {
        // Complete failure
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800';
        statusElement.textContent = 'Error';
        
        contentElement.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                <h5 class="font-medium text-red-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-exclamation-triangle text-red-600 mr-2"></i>
                    Rate Query Failed
                </h5>
                <p class="text-xs text-red-700">${results.error}</p>
            </div>
        `;
        return;
    }
    
    // Success status
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
    statusElement.textContent = 'Comprehensive Results';
    
    let content = '<div class="space-y-3">';
    
    // // Display summary statistics
    // if (results.metadata && results.metadata.totalOptions > 0) {
    //     content += `
    //        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
    //             <h5 class="font-medium text-blue-800 mb-2 flex items-center text-sm">
    //                 <i class="fas fa-chart-bar text-blue-600 mr-2"></i>
    //                 Query Summary
    //             </h5>
    //             <div class="grid grid-cols-3 gap-2 text-xs">
    //                 <div><span class="text-neutral-600">Total Options:</span> <span class="font-medium">${results.metadata.totalOptions}</span></div>
    //                 <div><span class="text-neutral-600">Carriers:</span> <span class="font-medium">${results.metadata.carriers.length}</span></div>
    //                 <div><span class="text-neutral-600">Modes:</span> <span class="font-medium">${results.metadata.transportModes.join(', ')}</span></div>
    //             </div>
    //         </div>
    //     `;
    // } 
    
    // Display cheapest rate
    if (results.cheapest?.data) {
        const cheapest = results.cheapest.data;
        const costStr = cheapest.cost ? `${cheapest.currency} ${cheapest.cost.toLocaleString()}` : 'N/A';
        const transitStr = cheapest.transit_time ? `${cheapest.transit_time.toFixed(1)} ${cheapest.transit_time_unit || 'hours'}` : 'N/A';
        const distanceStr = cheapest.distance ? `${cheapest.distance.toFixed(1)} ${cheapest.distance_unit}` : 'N/A';
        const costPerMileStr = cheapest.cost_per_mile ? `${cheapest.currency} ${cheapest.cost_per_mile.toFixed(2)}/${cheapest.distance_unit}` : 'N/A';
        
        content += `
            <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <h5 class="font-medium text-green-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-dollar-sign text-green-600 mr-2"></i>
                    Cheapest Option ${cheapest.is_optimal ? '✨' : ''}
                </h5>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div><span class="text-neutral-600">Total Cost:</span> <span class="font-medium text-green-700">${costStr}</span></div>
                    <div><span class="text-neutral-600">Cost/Mile:</span> <span class="font-medium">${costPerMileStr}</span></div>
                    <div><span class="text-neutral-600">Carrier:</span> <span class="font-medium">${cheapest.carrier}</span></div>
                    <div><span class="text-neutral-600">Mode:</span> <span class="font-medium">${cheapest.transport_mode}</span></div>
                    <div><span class="text-neutral-600">Distance:</span> <span class="font-medium">${distanceStr}</span></div>
                    <div><span class="text-neutral-600">Transit:</span> <span class="font-medium">${transitStr}</span></div>
                </div>
            </div>
        `;
    }
    
    // Display best carrier rate (if available)
    if (results.bestCarrier?.data && laneInfo.bestCarrier) {
        const bestCarrier = results.bestCarrier.data;
        const costStr = bestCarrier.cost ? `${bestCarrier.currency} ${bestCarrier.cost.toLocaleString()}` : 'N/A';
        const transitStr = bestCarrier.transit_time ? `${bestCarrier.transit_time.toFixed(1)} ${bestCarrier.transit_time_unit || 'hours'}` : 'N/A';
        const distanceStr = bestCarrier.distance ? `${bestCarrier.distance.toFixed(1)} ${bestCarrier.distance_unit}` : 'N/A';
        const costPerMileStr = bestCarrier.cost_per_mile ? `${bestCarrier.currency} ${bestCarrier.cost_per_mile.toFixed(2)}/${bestCarrier.distance_unit}` : 'N/A';
        
        content += `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <h5 class="font-medium text-blue-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-star text-blue-600 mr-2"></i>
                    Best Performer (${laneInfo.bestCarrier}) ${bestCarrier.is_optimal ? '✨' : ''}
                </h5>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div><span class="text-neutral-600">Total Cost:</span> <span class="font-medium text-blue-700">${costStr}</span></div>
                    <div><span class="text-neutral-600">Cost/Mile:</span> <span class="font-medium">${costPerMileStr}</span></div>
                    <div><span class="text-neutral-600">Carrier:</span> <span class="font-medium">${bestCarrier.carrier}</span></div>
                    <div><span class="text-neutral-600">Mode:</span> <span class="font-medium">${bestCarrier.transport_mode}</span></div>
                    <div><span class="text-neutral-600">Distance:</span> <span class="font-medium">${distanceStr}</span></div>
                    <div><span class="text-neutral-600">Transit:</span> <span class="font-medium">${transitStr}</span></div>
                </div>
            </div>
        `;
        
        // // Add comparison if both rates available
        // if (results.cheapest?.data) {
        //     const cheapestCost = results.cheapest.data.cost || 0;
        //     const bestCost = bestCarrier.cost || 0;
        //     const difference = bestCost - cheapestCost;
        //     const percentDiff = cheapestCost > 0 ? ((difference / cheapestCost) * 100).toFixed(1) : 0;
            
        //     content += `
        //         <div class="bg-neutral-50 border border-neutral-200 rounded-lg p-3">
        //             <h5 class="font-medium text-neutral-800 mb-2 flex items-center text-sm">
        //                 <i class="fas fa-balance-scale text-neutral-600 mr-2"></i>
        //                 Rate Comparison
        //             </h5>
        //             <p class="text-xs text-neutral-700">
        //                 ${difference >= 0 
        //                     ? `Best performer costs ${bestCarrier.currency} ${Math.abs(difference).toLocaleString()} more (+${percentDiff}%) than cheapest option` 
        //                     : `Best performer costs ${bestCarrier.currency} ${Math.abs(difference).toLocaleString()} less (-${Math.abs(percentDiff)}%) than cheapest option`
        //                 }
        //             </p>
        //         </div>
        //     `;
        // }
    }
    
    // Show any partial errors or best carrier unavailable message
    if (results.error && (results.cheapest || results.bestCarrier)) {
        const isCarrierUnavailable = results.error.includes('not found in rate results') || results.error.includes('No valid rates available');
        const bgColor = isCarrierUnavailable ? 'bg-blue-50 border-blue-200' : 'bg-yellow-50 border-yellow-200';
        const textColor = isCarrierUnavailable ? 'text-blue-800' : 'text-yellow-800';
        const iconColor = isCarrierUnavailable ? 'text-blue-600' : 'text-yellow-600';
        const icon = isCarrierUnavailable ? 'fa-info-circle' : 'fa-exclamation-triangle';
        
        content += `
            <div class="${bgColor} rounded-lg p-3">
                <h5 class="font-medium ${textColor} mb-2 flex items-center text-sm">
                    <i class="fas ${icon} ${iconColor} mr-2"></i>
                    ${isCarrierUnavailable ? 'Best Carrier Rate Unavailable' : 'Partial Results'}
                </h5>
                <p class="text-xs ${textColor.replace('800', '700')}">${results.error}</p>
            </div>
        `;
    }
    
    content += '</div>';
    contentElement.innerHTML = content;
}

document.addEventListener('DOMContentLoaded', function() {
    const collapseButton = document.getElementById('collapse-chat-btn');
    const chatTarget = document.getElementById('chat-messages');
    
    collapseButton.addEventListener('click', function() {
        if (chatTarget.classList.contains('collapsed')) {
            chatTarget.classList.remove('collapsed');
            collapseButton.textContent = 'Collapse Chat';
            // Optionally adjust other elements, e.g., resize siblings if needed
        } else {
            chatTarget.classList.add('collapsed');
            collapseButton.textContent = 'Expand Chat';
            // You can add more logic here to move/resize other elements if required
        }
    });
});

// Hook into RIQ rate results display to capture actual rate data
const originalDisplayRateResultsComprehensive = displayRateResultsComprehensive;
displayRateResultsComprehensive = function(results, laneInfo) {
    // Call original function
    originalDisplayRateResultsComprehensive(results, laneInfo);
    
    // Update recommendation data collection with actual rate results
    const riqData = {
        rate_results: results,
        lane_info: laneInfo,
        timestamp: new Date().toISOString()
    };
    updateRecommendationDataCollection('riq_data', riqData, true);
};

// Spot Matrix Modal Functions
function openSpotMatrixModal() {
    const modal = document.getElementById('spot-matrix-modal');
    const content = document.getElementById('spot-matrix-content');
    
    // Check if we have spot rate data available in recommendations
    if (window.aggregatedRecommendationData && window.aggregatedRecommendationData.spot_data) {
        displaySpotMatrixInModal(window.aggregatedRecommendationData.spot_data);
    } else if (window.currentLaneInfo) {
        // If we have lane info but no spot data, try to fetch it
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

function closeSpotMatrixModal() {
    document.getElementById('spot-matrix-modal').classList.add('hidden');
}

async function fetchSpotMatrixForModal() {
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
        
        const data = await fetchSpotRateMatrix(laneInfo, shipmentDate);
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

function displaySpotMatrixInModal(data) {
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
