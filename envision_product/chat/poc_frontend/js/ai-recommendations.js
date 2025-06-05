/**
 * AI recommendation system
 * Data collection status tracking, recommendation generation, aggregated data management
 */

import { makeAPIRequest } from './api-client.js';
import { showNotification } from './utils.js';

/**
 * Handle generate recommendations click
 */
export async function handleGenerateRecommendationsClick() {
    console.log('🤖 Generating AI recommendations...');
    showNotification('Generating AI recommendations...', 'info');
    
    // Check if we have sufficient data
    const aggregatedData = window.aggregatedRecommendationData;
    
    if (aggregatedData) {
        const hasData = Object.values(aggregatedData).some(item => item.hasData);
        
        if (hasData) {
            try {
                const payload = {
                    aggregated_data: aggregatedData,
                    lane_info: window.currentLaneInfo
                };
                
                const response = await makeAPIRequest('/recommendations/generate', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                
                console.log('AI recommendations response:', response);
                showNotification('AI recommendations generated successfully', 'success');
                return response;
            } catch (error) {
                console.error('Failed to generate AI recommendations:', error);
                showNotification('Failed to generate AI recommendations', 'error');
            }
        } else {
            showNotification('Insufficient data for comprehensive recommendations. Please perform more analyses first.', 'warning');
        }
    } else {
        showNotification('No data available for recommendations', 'warning');
    }
}

/**
 * Reset AI recommendations panel
 */
export function resetAIRecommendationsPanel() {
    const recommendationsElement = document.getElementById('ai-recommendations-content');
    if (recommendationsElement) {
        recommendationsElement.innerHTML = '';
    }
    
    // Reset aggregated data
    if (window.aggregatedRecommendationData) {
        Object.keys(window.aggregatedRecommendationData).forEach(key => {
            window.aggregatedRecommendationData[key] = { hasData: false, data: null };
        });
    }
}

/**
 * Update recommendation data collection status
 */
export function updateRecommendationDataCollection(dataType, data, hasData = true) {
    console.log(`📊 Updating recommendation data collection: ${dataType}`, { hasData, data });
    
    if (window.aggregatedRecommendationData) {
        window.aggregatedRecommendationData[dataType] = { hasData, data };
    }
}

/**
 * Assign global functions
 */
function assignGlobalFunctions() {
    window.handleGenerateRecommendationsClick = handleGenerateRecommendationsClick;
    window.resetAIRecommendationsPanel = resetAIRecommendationsPanel;
    window.updateRecommendationDataCollection = updateRecommendationDataCollection;
}

assignGlobalFunctions();
export { assignGlobalFunctions }; 