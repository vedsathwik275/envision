// Configuration
const API_BASE_URL = 'http://localhost:8004/api/v1';
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

    // Chat functionality
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    sendBtn.addEventListener('click', sendMessage);
    clearChatBtn.addEventListener('click', clearChat);
    
    chatKBSelect.addEventListener('change', handleKBSelection);

    // Close modals on backdrop click
    createKBModal.addEventListener('click', (e) => {
        if (e.target === createKBModal) closeCreateKBModal();
    });
    
    uploadDocModal.addEventListener('click', (e) => {
        if (e.target === uploadDocModal) closeUploadDocModal();
    });
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
        populateKBSelects();
        updateDashboardStats();
    } catch (error) {
        console.error('Failed to load knowledge bases:', error);
        knowledgeBases = [];
    }
}

function populateKBSelects() {
    const selects = [chatKBSelect, document.getElementById('upload-kb-select')];
    
    selects.forEach(select => {
        if (!select) return;
        
        // Clear existing options except the first one
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        knowledgeBases.forEach(kb => {
            const option = document.createElement('option');
            option.value = kb.id;
            option.textContent = `${kb.name} (${kb.status})`;
            select.appendChild(option);
        });
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
    card.className = 'border border-neutral-200 rounded-xl p-6 hover:shadow-md transition-shadow bg-white';
    
    const statusColor = getStatusColor(kb.status);
    
    card.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex-1">
                <h4 class="font-semibold text-neutral-900">${escapeHtml(kb.name)}</h4>
                <p class="text-sm text-neutral-600 mt-1">${escapeHtml(kb.description || 'No description')}</p>
                <div class="flex items-center mt-3 space-x-4 text-xs text-neutral-500">
                    <span class="inline-flex items-center px-2 py-1 rounded-full ${statusColor}">${kb.status}</span>
                    <span><i class="fas fa-file-alt mr-1"></i>${kb.document_count || 0} documents</span>
                    <span><i class="fas fa-clock mr-1"></i>${formatDate(kb.created_at)}</span>
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
    uploadDocModal.classList.add('hidden');
    document.getElementById('upload-doc-form').reset();
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

// Chat Functions
function loadChatView() {
    populateKBSelects();
}

function handleKBSelection() {
    const selectedKBId = chatKBSelect.value;
    const selectedKBInfo = document.getElementById('selected-kb-info');
    
    if (selectedKBId) {
        const kb = knowledgeBases.find(k => k.id === selectedKBId);
        if (kb) {
            document.getElementById('selected-kb-name').textContent = kb.name;
            document.getElementById('selected-kb-description').textContent = kb.description || 'No description';
            document.getElementById('selected-kb-status').textContent = kb.status;
            document.getElementById('selected-kb-status').className = `inline-flex items-center px-2 py-1 rounded-full ${getStatusColor(kb.status)}`;
            
            selectedKBInfo.classList.remove('hidden');
            
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
        selectedKBInfo.classList.add('hidden');
        currentKBId = null;
        disableChat('Please select a knowledge base');
        updateChatConnectionStatus(false);
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
}

function disableChat(reason) {
    chatInput.disabled = true;
    sendBtn.disabled = true;
    chatInput.placeholder = reason;
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !currentKBId) return;
    
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // Disable chat while processing
    enableChat();
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    try {
        const response = await makeAPIRequest(`/knowledge_bases/${currentKBId}/chat`, {
            method: 'POST',
            body: JSON.stringify({
                query: message
            })
        });
        
        addChatMessage(response.answer, 'assistant', response);
    } catch (error) {
        addChatMessage('Sorry, I encountered an error processing your question. Please try again.', 'assistant');
        showNotification(`Chat error: ${error.message}`, 'error');
    } finally {
        // Re-enable chat
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
    }
}

function addChatMessage(content, sender, metadata = null) {
    const messagesContainer = chatMessages;
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3';
    
    const isUser = sender === 'user';
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="flex-shrink-0 w-8 h-8 ${isUser ? 'bg-neutral-600' : 'bg-primary-500'} rounded-full flex items-center justify-center">
            <i class="fas ${isUser ? 'fa-user' : 'fa-robot'} text-white text-sm"></i>
        </div>
        <div class="flex-1">
            <div class="${isUser ? 'bg-neutral-600 text-white' : 'bg-neutral-100'} rounded-lg p-3">
                <p class="${isUser ? 'text-white' : 'text-neutral-800'}">${escapeHtml(content)}</p>
                ${metadata && metadata.sources ? `
                    <div class="mt-2 pt-2 border-t border-neutral-200">
                        <p class="text-xs text-neutral-600 mb-1">Sources:</p>
                        <div class="text-xs text-neutral-500">
                            ${metadata.sources.slice(0, 3).map(source => `<span class="inline-block bg-neutral-200 rounded px-2 py-1 mr-1 mb-1">${escapeHtml(source)}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
            <p class="text-xs text-neutral-500 mt-1">${timestamp}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function clearChat() {
    const welcomeMessage = chatMessages.querySelector('.flex.items-start.space-x-3');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage.cloneNode(true));
    }
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
