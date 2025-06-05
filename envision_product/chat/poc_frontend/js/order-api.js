/**
 * Order release API operations
 * Order detail fetching, order selection and display
 */

import { callDataToolsAPI } from './api-client.js';
import { escapeHtml, showNotification } from './utils.js';

/**
 * Update order release card
 */
export async function updateOrderReleaseCard(laneInfo, userMessage, response) {
    console.log('📦 Updating order release card...', laneInfo);
    
    const statusElement = document.getElementById('order-release-status');
    const contentElement = document.getElementById('order-release-content');
    
    if (statusElement) {
        statusElement.className = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800';
        statusElement.textContent = 'Ready';
    }
    
    if (contentElement && laneInfo) {
        contentElement.innerHTML = `
            <div class="bg-orange-50 border border-orange-200 rounded-lg p-3">
                <h5 class="font-medium text-orange-800 mb-2 flex items-center text-sm">
                    <i class="fas fa-shipping-fast text-orange-600 mr-2"></i>
                    Order Release Available
                </h5>
                <div class="text-xs text-orange-700 mb-3">
                    Lane: ${escapeHtml(laneInfo.laneName || 'Unknown')}
                </div>
                <button onclick="handleGetOrdersClick()" class="bg-orange-600 text-white px-3 py-1 text-sm rounded-lg hover:bg-orange-700 transition-colors">
                    Get Orders
                </button>
            </div>
        `;
    }
}

/**
 * Select an order and get detailed information
 */
export async function selectOrder(orderGid) {
    console.log('📋 Selecting order:', orderGid);
    
    try {
        const response = await callDataToolsAPI(`/order-release/${orderGid}`, {});
        console.log('Order details:', response);
        showNotification(`Order ${orderGid} details loaded`, 'success');
        return response;
    } catch (error) {
        console.error('Failed to get order details:', error);
        showNotification(`Failed to load order ${orderGid} details`, 'error');
    }
}

/**
 * Handle get orders click - fetch unplanned orders for the lane
 */
export async function handleGetOrdersClick() {
    console.log('🚚 Getting orders...');
    showNotification('Loading orders...', 'info');
    
    if (window.currentLaneInfo) {
        try {
            const payload = {
                origin_city: window.currentLaneInfo.sourceCity || '',
                destination_city: window.currentLaneInfo.destinationCity || ''
            };
            
            const response = await callDataToolsAPI('/order-release/unplanned-orders', payload);
            console.log('Unplanned orders response:', response);
            showNotification('Orders loaded successfully', 'success');
            return response;
        } catch (error) {
            console.error('Failed to fetch orders:', error);
            showNotification('Failed to load orders', 'error');
        }
    } else {
        showNotification('No lane information available for order search', 'warning');
    }
}

/**
 * Assign global functions
 */
function assignGlobalFunctions() {
    window.updateOrderReleaseCard = updateOrderReleaseCard;
    window.selectOrder = selectOrder;
    window.handleGetOrdersClick = handleGetOrdersClick;
}

assignGlobalFunctions();
export { assignGlobalFunctions }; 