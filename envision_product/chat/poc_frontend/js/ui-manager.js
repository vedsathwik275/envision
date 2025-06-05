/**
 * UI state management
 * Sidebar expansion/collapse, navigation handling, page title updates, loading states
 */

import { CONFIG } from './config.js';

// Global UI state
export let currentView = 'dashboard';

/**
 * Setup navigation event listeners
 */
export function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = link.getAttribute('data-section');
            const viewName = targetSection === 'knowledge-bases' ? 'knowledgeBases' : targetSection;
            navigateTo(viewName);
        });
    });
}

/**
 * Setup sidebar functionality
 */
export function setupSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarToggleCollapsed = document.getElementById('sidebar-toggle-collapsed');
    const sidebarToggleIcon = document.getElementById('sidebar-toggle-icon');
    const mainContent = document.getElementById('main-content');
    const header = document.getElementById('header');
    
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

/**
 * Expand the sidebar
 */
export function expandSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const header = document.getElementById('header');
    
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

/**
 * Collapse the sidebar
 */
export function collapseSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const header = document.getElementById('header');
    
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

/**
 * Navigate to a specific view
 * @param {string} view - View name to navigate to
 */
export function navigateTo(view) {
    const navItems = document.querySelectorAll('.nav-link');
    
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
        // Will be handled by knowledge-base module
        window.loadKnowledgeBasesView && window.loadKnowledgeBasesView();
    } else if (view === 'chat') {
        // Will be handled by chat-system module
        window.loadChatView && window.loadChatView();
    }
}

/**
 * Update page title based on current view
 * @param {string} view - Current view name
 */
export function updatePageTitle(view) {
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    
    const titles = {
        dashboard: { title: 'Dashboard', subtitle: 'RAG Chatbot Management' },
        knowledgeBases: { title: 'Knowledge Bases', subtitle: 'Manage your document collections' },
        chat: { title: 'Chat', subtitle: 'Ask questions about your documents' }
    };
    
    const config = titles[view] || titles.dashboard;
    pageTitle.textContent = config.title;
    pageSubtitle.textContent = config.subtitle;
}

/**
 * Show loading overlay
 * @param {string} text - Loading text to display
 */
export function showLoading(text = 'Processing...') {
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    
    if (loadingText) {
        loadingText.textContent = text;
    }
    
    if (loadingOverlay) {
        loadingOverlay.classList.remove('hidden');
    }
}

/**
 * Hide loading overlay
 */
export function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (loadingOverlay) {
        loadingOverlay.classList.add('hidden');
    }
}

/**
 * Get current view
 * @returns {string} Current view name
 */
export function getCurrentView() {
    return currentView;
}

/**
 * Set current view
 * @param {string} view - View name to set
 */
export function setCurrentView(view) {
    currentView = view;
}

/**
 * Update dashboard statistics
 */
export function updateDashboardStats() {
    const kbCountElement = document.getElementById('kb-count');
    const readyKbElement = document.getElementById('ready-kb-count');
    const docCountElement = document.getElementById('doc-count');
    
    if (kbCountElement && window.knowledgeBases) {
        kbCountElement.textContent = window.knowledgeBases.length;
    }
    
    if (readyKbElement && window.knowledgeBases) {
        const readyCount = window.knowledgeBases.filter(kb => kb.status === 'ready').length;
        readyKbElement.textContent = readyCount;
    }
    
    if (docCountElement && window.knowledgeBases) {
        const totalDocs = window.knowledgeBases.reduce((sum, kb) => sum + (kb.document_count || 0), 0);
        docCountElement.textContent = totalDocs;
    }
} 