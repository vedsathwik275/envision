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
        
        // Parse lane information from the message and update cards
        parseAndUpdateLaneInfo(message, response);
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
    
    // Handle sources section if present
    if (sourcesContent) {
        result += `
            <div class="mt-6 pt-4 border-t border-gray-200">
                <h4 class="text-sm font-medium text-gray-900 mb-3">Sources</h4>
                <div class="space-y-2">
        `;
        
        // Parse individual sources
        const sourceLines = sourcesContent.split('\n').filter(line => line.trim());
        let currentSource = '';
        let sourceNumber = 0;
        
        for (const line of sourceLines) {
            if (/^\s*\d+\./.test(line)) {
                if (currentSource) {
                    // Close previous source
                    result += '</div></div>';
                }
                sourceNumber++;
                const sourceMatch = line.match(/^\s*\d+\.\s*(.+)$/);
                if (sourceMatch) {
                    currentSource = sourceMatch[1];
                    result += `
                        <div class="bg-gray-50 rounded-lg p-3">
                            <div class="flex items-start">
                                <span class="flex-shrink-0 w-5 h-5 bg-gray-200 text-gray-700 text-xs font-medium rounded flex items-center justify-center mr-2 mt-0.5">${sourceNumber}</span>
                                <div class="min-w-0 flex-1">
                                    <p class="text-sm text-gray-700 font-medium">${currentSource}</p>
                    `;
                }
            } else if (line.includes('└─')) {
                const detailMatch = line.match(/└─\s*(.+)$/);
                if (detailMatch) {
                    result += `<p class="text-xs text-gray-500 font-mono mt-1 bg-gray-100 rounded px-2 py-1">${detailMatch[1]}</p>`;
                }
            }
        }
        
        if (currentSource) {
            result += '</div></div>';
        }
        
        result += '</div></div>';
    }
    
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
}

// Function to clear lane information cards
function clearLaneInfoCards() {
    // Reset Rate Inquiry Card
    const rateInquiryStatus = document.getElementById('rate-inquiry-status');
    const rateInquiryContent = document.getElementById('rate-inquiry-content');
    
    rateInquiryStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
    rateInquiryStatus.textContent = 'No data';
    
    rateInquiryContent.innerHTML = `
        <div class="text-center py-8 text-neutral-500">
            <i class="fas fa-search text-4xl mb-4 text-neutral-300"></i>
            <p>Ask about lane rates to see parsed information here</p>
            <p class="text-sm mt-2">Example: "What's the best rate from Los Angeles to Chicago?"</p>
        </div>
    `;
    
    // Reset Spot API Card
    const spotAPIStatus = document.getElementById('spot-api-status');
    const spotAPIContent = document.getElementById('spot-api-content');
    
    spotAPIStatus.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
    spotAPIStatus.textContent = 'No data';
    
    spotAPIContent.innerHTML = `
        <div class="text-center py-8 text-neutral-500">
            <i class="fas fa-analytics text-4xl mb-4 text-neutral-300"></i>
            <p>Ask about carrier performance or spot rates to see analysis here</p>
            <p class="text-sm mt-2">Example: "Show carrier performance for Dallas to Miami"</p>
        </div>
    `;
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
    const laneInfo = parseLaneInformation(userMessage);
    
    // Check if we have any meaningful lane information
    const hasLaneInfo = laneInfo.sourceCity || laneInfo.destinationCity || 
                       laneInfo.weight || laneInfo.volume || laneInfo.equipmentType || 
                       laneInfo.carrierName || laneInfo.serviceType;
    
    if (hasLaneInfo) {
        // Determine if this is a rate inquiry or spot API request
        const isRateInquiry = isRateInquiryPrompt(userMessage);
        const isSpotAPI = isSpotAPIPrompt(userMessage);
        
        // Update cards based on query type
        if (isRateInquiry) {
            updateRateInquiryCard(laneInfo, userMessage, response);
        } else if (isSpotAPI) {
            updateSpotAPICard(laneInfo, userMessage, response);
        } else if (laneInfo.sourceCity && laneInfo.destinationCity) {
            // If we have lane info but unclear intent, show both cards
            updateRateInquiryCard(laneInfo, userMessage, response);
            updateSpotAPICard(laneInfo, userMessage, response);
        }
    }
}

function parseLaneInformation(message) {
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
        requestType: null
    };
    
    // Parse cities (from X to Y, X-Y, between X and Y)
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
        const match = message.match(pattern);
        if (match) {
            laneInfo.sourceCity = cleanCityName(match[1]);
            laneInfo.destinationCity = cleanCityName(match[2]);
            break;
        }
    }
    
    // Additional city parsing for specific formats like "Elwood to Miami"
    if (!laneInfo.sourceCity && !laneInfo.destinationCity) {
        const simplePattern = /\b([A-Z][a-zA-Z\s]{2,})\s+to\s+([A-Z][a-zA-Z\s]{2,})\b/;
        const simpleMatch = message.match(simplePattern);
        if (simpleMatch) {
            laneInfo.sourceCity = cleanCityName(simpleMatch[1]);
            laneInfo.destinationCity = cleanCityName(simpleMatch[2]);
        }
    }
    
    // Parse weight (lbs, pounds, kg, tons)
    const weightMatch = message.match(/(\d+(?:,\d{3})*(?:\.\d+)?)\s*(lbs?|pounds?|kg|tons?|#)/i);
    if (weightMatch) {
        laneInfo.weight = `${weightMatch[1]} ${weightMatch[2] === '#' ? 'lbs' : weightMatch[2]}`;
    }
    
    // Parse volume (cuft, cubic feet, cbm)
    const volumeMatch = message.match(/(\d+(?:,\d{3})*(?:\.\d+)?)\s*(cuft|cubic\s*feet?|cbm|cubic\s*meters?|ft3|m3)/i);
    if (volumeMatch) {
        laneInfo.volume = `${volumeMatch[1]} ${volumeMatch[2]}`;
    }
    
    // Parse zip codes
    const zipMatch = message.match(/\b(\d{5}(?:-\d{4})?)\b/);
    if (zipMatch) {
        laneInfo.zipCode = zipMatch[1];
    }
    
    // Parse states (both abbreviations and full names)
    const stateMatch = message.match(/\b([A-Z]{2})\b/);
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
        if (pattern.test(message)) {
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
        const match = message.match(pattern);
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
        if (pattern.test(message)) {
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
    
    // Update status
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800';
    statusElement.textContent = 'Active';
    
    // Build content
    let content = `
        <div class="space-y-4">
            <div class="bg-blue-50 rounded-lg p-4">
                <h4 class="font-medium text-blue-900 mb-3">Lane Details</h4>
                <div class="grid grid-cols-2 gap-3 text-sm">
    `;
    
    if (laneInfo.sourceCity) {
        content += `<div><span class="text-neutral-600">From:</span> <span class="font-medium">${laneInfo.sourceCity}</span></div>`;
    }
    if (laneInfo.destinationCity) {
        content += `<div><span class="text-neutral-600">To:</span> <span class="font-medium">${laneInfo.destinationCity}</span></div>`;
    }
    if (laneInfo.weight) {
        content += `<div><span class="text-neutral-600">Weight:</span> <span class="font-medium">${laneInfo.weight}</span></div>`;
    }
    if (laneInfo.volume) {
        content += `<div><span class="text-neutral-600">Volume:</span> <span class="font-medium">${laneInfo.volume}</span></div>`;
    }
    if (laneInfo.equipmentType) {
        content += `<div><span class="text-neutral-600">Equipment:</span> <span class="font-medium">${laneInfo.equipmentType}</span></div>`;
    }
    if (laneInfo.serviceType) {
        content += `<div><span class="text-neutral-600">Service:</span> <span class="font-medium">${laneInfo.serviceType}</span></div>`;
    }
    if (laneInfo.zipCode) {
        content += `<div><span class="text-neutral-600">Zip Code:</span> <span class="font-medium">${laneInfo.zipCode}</span></div>`;
    }
    if (laneInfo.state) {
        content += `<div><span class="text-neutral-600">State:</span> <span class="font-medium">${laneInfo.state}</span></div>`;
    }
    
    content += `
                </div>
            </div>
            <div class="bg-white border border-blue-200 rounded-lg p-4">
                <h5 class="font-medium text-neutral-900 mb-2 flex items-center">
                    <i class="fas fa-quote-left text-blue-500 mr-2"></i>
                    Original Query
                </h5>
                <p class="text-sm text-neutral-600 bg-neutral-50 rounded-lg p-3">${escapeHtml(userMessage)}</p>
            </div>
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h5 class="font-medium text-yellow-800 mb-2 flex items-center">
                    <i class="fas fa-clock text-yellow-600 mr-2"></i>
                    Next Steps
                </h5>
                <p class="text-sm text-yellow-700">Ready to request rate quote from RIQ API with parsed parameters.</p>
            </div>
        </div>
    `;
    
    contentElement.innerHTML = content;
}

function updateSpotAPICard(laneInfo, userMessage, response) {
    const statusElement = document.getElementById('spot-api-status');
    const contentElement = document.getElementById('spot-api-content');
    
    // Update status
    statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800';
    statusElement.textContent = 'Analyzing';
    
    // Build content
    let content = `
        <div class="space-y-4">
            <div class="bg-green-50 rounded-lg p-4">
                <h4 class="font-medium text-green-900 mb-3">Analysis Parameters</h4>
                <div class="grid grid-cols-2 gap-3 text-sm">
    `;
    
    if (laneInfo.sourceCity) {
        content += `<div><span class="text-neutral-600">Origin:</span> <span class="font-medium">${laneInfo.sourceCity}</span></div>`;
    }
    if (laneInfo.destinationCity) {
        content += `<div><span class="text-neutral-600">Destination:</span> <span class="font-medium">${laneInfo.destinationCity}</span></div>`;
    }
    if (laneInfo.carrierName) {
        content += `<div><span class="text-neutral-600">Carrier:</span> <span class="font-medium">${laneInfo.carrierName}</span></div>`;
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
    
    // Add analysis type based on keywords
    let analysisType = 'General Analysis';
    if (userMessage.toLowerCase().includes('performance')) {
        analysisType = 'Carrier Performance';
    } else if (userMessage.toLowerCase().includes('spot')) {
        analysisType = 'Spot Market Analysis';
    } else if (userMessage.toLowerCase().includes('capacity')) {
        analysisType = 'Capacity Analysis';
    } else if (userMessage.toLowerCase().includes('rate')) {
        analysisType = 'Rate Analysis';
    }
    
    content += `<div><span class="text-neutral-600">Type:</span> <span class="font-medium">${analysisType}</span></div>`;
    content += `<div><span class="text-neutral-600">Status:</span> <span class="font-medium text-green-600">Ready for API Call</span></div>`;
    
    content += `
                </div>
            </div>
            <div class="bg-white border border-green-200 rounded-lg p-4">
                <h5 class="font-medium text-neutral-900 mb-2 flex items-center">
                    <i class="fas fa-search text-green-500 mr-2"></i>
                    Query Analysis
                </h5>
                <p class="text-sm text-neutral-600 bg-neutral-50 rounded-lg p-3">${escapeHtml(userMessage)}</p>
            </div>
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h5 class="font-medium text-purple-800 mb-2 flex items-center">
                    <i class="fas fa-chart-line text-purple-600 mr-2"></i>
                    API Integration
                </h5>
                <p class="text-sm text-purple-700">Ready to query Spot API for ${analysisType.toLowerCase()} data.</p>
            </div>
        </div>
    `;
    
    contentElement.innerHTML = content;
}
