/**
 * Chat functionality
 * Message sending/receiving, Chat UI updates, Response formatting, Chat connection status
 */

import { makeAPIRequest, updateConnectionStatus } from './api-client.js';
import { escapeHtml, showNotification } from './utils.js';

/**
 * Load chat view and setup
 */
export function loadChatView() {
    handleKBSelection();
}

/**
 * Handle knowledge base selection for chat
 */
export function handleKBSelection() {
    const chatKBSelect = document.getElementById('chat-kb-select');
    const kbId = chatKBSelect?.value;
    
    if (kbId && window.knowledgeBases) {
        const selectedKB = window.knowledgeBases.find(kb => kb.id === kbId);
        if (selectedKB && selectedKB.status === 'ready') {
            enableChat();
            window.currentKBId = kbId;
        } else {
            disableChat('Selected knowledge base is not ready');
        }
    } else {
        disableChat('Please select a knowledge base');
    }
}

/**
 * Update chat connection status
 * @param {boolean} connected - Connection status
 */
export function updateChatConnectionStatus(connected) {
    updateConnectionStatus(connected);
}

/**
 * Enable chat interface
 */
export function enableChat() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    
    if (chatInput) {
        chatInput.disabled = false;
        chatInput.placeholder = 'Ask a question about your documents...';
    }
    
    if (sendBtn) {
        sendBtn.disabled = false;
    }
}

/**
 * Disable chat interface
 * @param {string} reason - Reason for disabling
 */
export function disableChat(reason) {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    
    if (chatInput) {
        chatInput.disabled = true;
        chatInput.placeholder = reason;
    }
    
    if (sendBtn) {
        sendBtn.disabled = true;
    }
}

/**
 * Send message to chat
 */
export async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput?.value.trim();
    
    if (!message || !window.currentKBId) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    const typingId = Date.now();
    addChatMessage('', 'assistant', { typing: true, id: typingId });
    
    try {
        const response = await makeAPIRequest('/chat', {
            method: 'POST',
            body: JSON.stringify({
                message: message,
                knowledge_base_id: window.currentKBId
            })
        });
        
        // Remove typing indicator
        const typingElement = document.querySelector(`[data-message-id="${typingId}"]`);
        if (typingElement) {
            typingElement.remove();
        }
        
        // Add assistant response
        addChatMessage(response.answer, 'assistant', {
            sources: response.sources,
            processing_time: response.processing_time
        });
        
        // Parse and update lane information for transportation-related queries
        if (window.parseAndUpdateLaneInfo) {
            window.parseAndUpdateLaneInfo(message, response);
        }
        
    } catch (error) {
        // Remove typing indicator
        const typingElement = document.querySelector(`[data-message-id="${typingId}"]`);
        if (typingElement) {
            typingElement.remove();
        }
        
        console.error('Chat error:', error);
        addChatMessage('Sorry, I encountered an error processing your request. Please try again.', 'assistant', {
            error: true
        });
        showNotification('Failed to send message: ' + error.message, 'error');
    }
}

/**
 * Add message to chat display
 * @param {string} content - Message content
 * @param {string} sender - Message sender ('user' or 'assistant')
 * @param {Object} metadata - Additional message metadata
 */
export function addChatMessage(content, sender, metadata = null) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
    
    if (metadata?.id) {
        messageDiv.setAttribute('data-message-id', metadata.id);
    }
    
    const messageContent = document.createElement('div');
    messageContent.className = `max-w-4xl p-4 rounded-lg ${
        sender === 'user' 
            ? 'bg-primary-600 text-white' 
            : 'bg-white border border-neutral-200'
    }`;
    
    if (metadata?.typing) {
        messageContent.innerHTML = `
            <div class="flex items-center space-x-1">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span class="text-neutral-500 text-sm ml-2">AI is thinking...</span>
            </div>
        `;
    } else if (sender === 'user') {
        messageContent.innerHTML = `<div class="whitespace-pre-wrap">${escapeHtml(content)}</div>`;
    } else {
        // Assistant message with formatting
        const formattedContent = formatRAGResponse(content);
        messageContent.innerHTML = formattedContent;
        
        // Add sources if available
        if (metadata?.sources && metadata.sources.length > 0) {
            const sourcesHtml = formatSources(metadata.sources);
            messageContent.innerHTML += sourcesHtml;
        }
        
        // Add processing time if available
        if (metadata?.processing_time) {
            messageContent.innerHTML += `
                <div class="mt-3 pt-3 border-t border-neutral-100 text-xs text-neutral-500">
                    Response time: ${metadata.processing_time.toFixed(2)}s
                </div>
            `;
        }
        
        // Add error styling if needed
        if (metadata?.error) {
            messageContent.className += ' border-red-200 bg-red-50';
        }
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Format RAG response content
 * @param {string} content - Raw response content
 * @returns {string} Formatted HTML content
 */
export function formatRAGResponse(content) {
    if (!content) return '';
    
    // Escape HTML first
    let formatted = escapeHtml(content);
    
    // Convert markdown-style formatting
    // Bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre class="bg-neutral-100 p-3 rounded-lg mt-2 mb-2 overflow-x-auto"><code>$1</code></pre>');
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="bg-neutral-100 px-1 py-0.5 rounded text-sm">$1</code>');
    
    // Lists
    formatted = formatted.replace(/^\* (.+)$/gm, '<li class="ml-4">• $1</li>');
    formatted = formatted.replace(/(<li class="ml-4">.*<\/li>)/s, '<ul class="my-2">$1</ul>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Headings
    formatted = formatted.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>');
    formatted = formatted.replace(/^## (.+)$/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>');
    formatted = formatted.replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>');
    
    return `<div class="prose prose-sm max-w-none">${formatted}</div>`;
}

/**
 * Format sources section
 * @param {Array} sources - Array of source documents
 * @returns {string} Formatted sources HTML
 */
export function formatSources(sources) {
    if (!sources || sources.length === 0) return '';
    
    let sourcesHtml = `
        <div class="mt-4 pt-4 border-t border-neutral-100">
            <details class="group">
                <summary class="flex items-center justify-between cursor-pointer text-sm font-medium text-neutral-700 hover:text-neutral-900">
                    <span class="flex items-center">
                        <i class="fas fa-book text-neutral-400 mr-2"></i>
                        Sources (${sources.length})
                    </span>
                    <i class="fas fa-chevron-down text-neutral-400 group-open:rotate-180 transition-transform"></i>
                </summary>
                <div class="mt-3 space-y-2">
    `;
    
    sources.forEach((source, index) => {
        sourcesHtml += `
            <div class="bg-neutral-50 rounded-lg p-3 text-sm">
                <div class="font-medium text-neutral-800 mb-1">
                    ${escapeHtml(source.metadata?.title || source.metadata?.filename || `Source ${index + 1}`)}
                </div>
                <div class="text-neutral-600 text-xs mb-2">
                    Score: ${source.score ? source.score.toFixed(3) : 'N/A'} | 
                    Page: ${source.metadata?.page || 'N/A'}
                </div>
                <div class="text-neutral-700 max-h-20 overflow-hidden">
                    ${escapeHtml(source.content).substring(0, 200)}${source.content.length > 200 ? '...' : ''}
                </div>
            </div>
        `;
    });
    
    sourcesHtml += `
                </div>
            </details>
        </div>
    `;
    
    return sourcesHtml;
}

/**
 * Clear chat messages
 */
export function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }
    
    // Clear lane info cards as well
    if (window.clearLaneInfoCards) {
        window.clearLaneInfoCards();
    }
    
    showNotification('Chat cleared', 'info');
} 