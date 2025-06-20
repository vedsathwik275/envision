/**
 * Knowledge base CRUD operations
 * Document upload functionality, KB processing and status management, Default KB management
 */

import { makeAPIRequest } from './api-client.js';
import { CONFIG } from './config.js';
import { showNotification, escapeHtml, formatDate } from './utils.js';
import { showLoading, hideLoading, updateDashboardStats } from './ui-manager.js';
import { closeCreateKBModal, closeUploadDocModal } from './modal-manager.js';

// Global knowledge base state
export let knowledgeBases = [];
export let currentKBId = null;

/**
 * Load knowledge bases from API
 */
export async function loadKnowledgeBases() {
    try {
        const data = await makeAPIRequest('/knowledge_bases/');
        knowledgeBases = data;
        window.knowledgeBases = knowledgeBases; // Keep global reference
        
        // Update dashboard statistics when knowledge bases are loaded
        updateDashboardStats();
        
        return knowledgeBases;
    } catch (error) {
        console.error('Failed to load knowledge bases:', error);
        showNotification('Failed to load knowledge bases', 'error');
        return [];
    }
}

/**
 * Populate KB select dropdowns
 */
export function populateKBSelects() {
    const selects = document.querySelectorAll('#chat-kb-select, #upload-kb-select');
    
    selects.forEach(select => {
        if (!select) return;
        
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select a knowledge base...</option>';
        
        knowledgeBases.forEach(kb => {
            const option = document.createElement('option');
            option.value = kb.id;
            option.textContent = kb.name;
            if (kb.status !== 'ready') {
                option.disabled = true;
                option.textContent += ` (${kb.status})`;
            }
            select.appendChild(option);
        });
        
        // Restore previous selection if it still exists
        if (currentValue && Array.from(select.options).some(opt => opt.value === currentValue)) {
            select.value = currentValue;
        }
        
        // Set default KB if available
        const defaultKBId = getDefaultKB();
        if (defaultKBId && !currentValue) {
            select.value = defaultKBId;
        }
    });
}

/**
 * Load knowledge bases view
 */
export async function loadKnowledgeBasesView() {
    console.log('🔄 Loading knowledge bases view...');
    await loadKnowledgeBases();
    console.log(`📊 Loaded ${knowledgeBases.length} knowledge bases:`, knowledgeBases);
    renderKnowledgeBases();
    console.log('✅ Knowledge bases view rendered');
}

/**
 * Render knowledge bases list
 */
export function renderKnowledgeBases() {
    const container = document.getElementById('kb-list');
    if (!container) {
        console.error('❌ kb-list container not found!');
        return;
    }
    console.log(`🎨 Rendering ${knowledgeBases.length} knowledge bases in container:`, container);
    
    if (knowledgeBases.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-neutral-500">
                <i class="fas fa-database text-6xl mb-4 text-neutral-300"></i>
                <h3 class="text-xl font-semibold mb-2">No Knowledge Bases</h3>
                <p class="text-neutral-400 mb-6">Create your first knowledge base to get started</p>
                <button onclick="openCreateKBModal()" class="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors">
                    <i class="fas fa-plus mr-2"></i>Create Knowledge Base
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = knowledgeBases.map(kb => createKnowledgeBaseCard(kb)).join('');
    
    // Add event listeners to implement radio-button-like behavior for default checkboxes
    setupDefaultCheckboxBehavior();
}

/**
 * Setup radio-button-like behavior for default knowledge base checkboxes
 */
function setupDefaultCheckboxBehavior() {
    const defaultCheckboxes = document.querySelectorAll('.default-kb-checkbox');
    
    defaultCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                // Uncheck all other default checkboxes
                defaultCheckboxes.forEach(otherCheckbox => {
                    if (otherCheckbox !== this) {
                        otherCheckbox.checked = false;
                    }
                });
            }
        });
    });
}

/**
 * Create knowledge base card HTML
 * @param {Object} kb - Knowledge base object
 * @returns {string} HTML string for the card
 */
export function createKnowledgeBaseCard(kb) {
    const statusColor = getStatusColor(kb.status);
    const isDefaultKB = getDefaultKB() === kb.id;
    
    // Apply gold styling to the entire card if it's the default KB
    const cardClasses = isDefaultKB 
        ? "bg-yellow-50 rounded-lg shadow-sm border-2 border-yellow-400 p-6" 
        : "bg-white rounded-lg shadow-sm border border-neutral-200 p-6";
    
    return `
        <div class="${cardClasses}">
            <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                        <h3 class="text-lg font-semibold text-neutral-900">${escapeHtml(kb.name)}</h3>
                        ${isDefaultKB ? '<span class="bg-yellow-200 text-yellow-800 text-xs font-medium px-2 py-1 rounded-full">Default</span>' : ''}
                    </div>
                    <p class="text-sm text-neutral-600 mb-3">${escapeHtml(kb.description || 'No description provided')}</p>
                    <div class="flex items-center gap-4 text-sm text-neutral-500">
                        <span><i class="fas fa-calendar mr-1"></i>${formatDate(kb.created_at)}</span>
                        <span><i class="fas fa-file mr-1"></i>${kb.document_count || 0} documents</span>
                    </div>
                </div>
                <div class="flex flex-col items-end gap-2">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColor}">
                        ${kb.status === 'processing' ? '<i class="fas fa-spinner fa-spin mr-1"></i>' : ''}
                        ${kb.status}
                    </span>
                    <label class="flex items-center text-sm text-neutral-600 cursor-pointer">
                        <input type="checkbox" 
                               class="default-kb-checkbox h-4 w-4 mr-2 rounded border-neutral-300" 
                               ${isDefaultKB ? 'checked' : ''} 
                               onchange="handleDefaultKBChange('${kb.id}', this)">
                        Set as default knowledge base
                    </label>
                </div>
            </div>
            
            <div class="flex gap-2">
                <button onclick="uploadToKB('${kb.id}')" class="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors">
                    <i class="fas fa-upload mr-1"></i>Upload Docs
                </button>
                <button onclick="processKB('${kb.id}')" class="px-3 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors" ${kb.status === 'processing' ? 'disabled' : ''}>
                    <i class="fas fa-cog mr-1"></i>Process
                </button>
                <button onclick="startChatWithKB('${kb.id}')" class="px-3 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors" ${kb.status !== 'ready' ? 'disabled' : ''}>
                    <i class="fas fa-comments mr-1"></i>Chat
                </button>
            </div>
        </div>
    `;
}

/**
 * Get status color class for knowledge base status
 * @param {string} status - KB status
 * @returns {string} CSS class for status color
 */
export function getStatusColor(status) {
    return CONFIG.STATUS_COLORS[status] || CONFIG.STATUS_COLORS.default;
}

/**
 * Handle create KB form submission
 * @param {Event} e - Form submit event
 */
export async function handleCreateKB(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const kbData = {
        name: formData.get('name'),
        description: formData.get('description')
    };
    
    try {
        showLoading('Creating knowledge base...');
        await makeAPIRequest('/knowledge_bases/', {
            method: 'POST',
            body: JSON.stringify(kbData)
        });
        
        showNotification('Knowledge base created successfully', 'success');
        closeCreateKBModal();
        await loadKnowledgeBases();
        renderKnowledgeBases();
        populateKBSelects();
        e.target.reset();
    } catch (error) {
        console.error('Failed to create knowledge base:', error);
        showNotification('Failed to create knowledge base: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Handle upload document form submission
 * @param {Event} e - Form submit event
 */
export async function handleUploadDocument(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const kbId = formData.get('kb_id');
    const files = formData.getAll('files');
    
    if (!kbId) {
        showNotification('Please select a knowledge base', 'warning');
        return;
    }
    
    if (files.length === 0) {
        showNotification('Please select at least one file', 'warning');
        return;
    }
    
    try {
        showLoading('Uploading documents...');
        
        // Upload each file
        for (const file of files) {
            const uploadData = new FormData();
            uploadData.append('file', file);
            
            await fetch(`${CONFIG.API_BASE_URL}/knowledge_bases/${kbId}/documents`, {
                method: 'POST',
                body: uploadData
            });
        }
        
        showNotification(`Successfully uploaded ${files.length} document(s)`, 'success');
        closeUploadDocModal();
        await loadKnowledgeBases();
        renderKnowledgeBases();
        e.target.reset();
    } catch (error) {
        console.error('Failed to upload documents:', error);
        showNotification('Failed to upload documents: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Upload documents to specific KB
 * @param {string} kbId - Knowledge base ID
 */
export function uploadToKB(kbId) {
    const uploadKBSelect = document.getElementById('upload-kb-select');
    if (uploadKBSelect) {
        uploadKBSelect.value = kbId;
    }
    
    // This will be handled by modal manager
    window.openUploadDocModal && window.openUploadDocModal();
}

/**
 * Process knowledge base
 * @param {string} kbId - Knowledge base ID
 */
export async function processKB(kbId) {
    try {
        showLoading('Processing knowledge base...');
        await makeAPIRequest(`/knowledge_bases/${kbId}/process`, {
            method: 'POST'
        });
        
        showNotification('Knowledge base processing started', 'success');
        await loadKnowledgeBases();
        renderKnowledgeBases();
        populateKBSelects();
    } catch (error) {
        console.error('Failed to process knowledge base:', error);
        showNotification('Failed to process knowledge base: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Start chat with specific KB
 * @param {string} kbId - Knowledge base ID
 */
export function startChatWithKB(kbId) {
    const chatKBSelect = document.getElementById('chat-kb-select');
    if (chatKBSelect) {
        chatKBSelect.value = kbId;
        currentKBId = kbId;
        window.currentKBId = kbId; // Keep global reference
        
        // Trigger change event to enable chat
        chatKBSelect.dispatchEvent(new Event('change'));
    }
    
    // Navigate to chat view - this will be handled by UI manager
    window.navigateTo && window.navigateTo('chat');
}

/**
 * Set default KB
 * @param {string} kbId - Knowledge base ID
 */
export function setDefaultKB(kbId) {
    localStorage.setItem('defaultKnowledgeBaseId', kbId);
}

/**
 * Get default KB
 * @returns {string|null} Default KB ID
 */
export function getDefaultKB() {
    return localStorage.getItem('defaultKnowledgeBaseId');
}

/**
 * Clear default KB
 */
export function clearDefaultKB() {
    localStorage.removeItem('defaultKnowledgeBaseId');
}

/**
 * Handle default KB change
 * @param {string} kbId - Knowledge base ID
 * @param {HTMLInputElement} checkbox - Checkbox element
 */
export function handleDefaultKBChange(kbId, checkbox) {
    if (checkbox.checked) {
        setDefaultKB(kbId);
    } else {
        clearDefaultKB();
    }
}

/**
 * Get knowledge bases list
 * @returns {Array} Array of knowledge bases
 */
export function getKnowledgeBases() {
    return knowledgeBases;
}

/**
 * Get current KB ID
 * @returns {string|null} Current KB ID
 */
export function getCurrentKBId() {
    return currentKBId;
}

/**
 * Set current KB ID
 * @param {string} kbId - KB ID to set
 */
export function setCurrentKBId(kbId) {
    currentKBId = kbId;
    window.currentKBId = kbId;
}

/**
 * Assign knowledge base functions to window object for global access
 */
function assignGlobalFunctions() {
    window.loadKnowledgeBasesView = loadKnowledgeBasesView;
    window.loadKnowledgeBases = loadKnowledgeBases;
    window.renderKnowledgeBases = renderKnowledgeBases;
    window.populateKBSelects = populateKBSelects;
    window.uploadToKB = uploadToKB;
    window.processKB = processKB;
    window.startChatWithKB = startChatWithKB;
    window.handleDefaultKBChange = handleDefaultKBChange;
    window.handleCreateKB = handleCreateKB;
    window.handleUploadDocument = handleUploadDocument;
    window.getKnowledgeBases = getKnowledgeBases;
    window.getCurrentKBId = getCurrentKBId;
    window.setCurrentKBId = setCurrentKBId;
    window.setDefaultKB = setDefaultKB;
    window.getDefaultKB = getDefaultKB;
    window.clearDefaultKB = clearDefaultKB;
}

// Auto-assign functions when module loads
assignGlobalFunctions(); 