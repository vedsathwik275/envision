/**
 * Utility functions used across modules
 * Common helper functions for the RAG chatbot application
 */

/**
 * Escape HTML characters to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
export function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Format date string for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show notification to user
 * @param {string} message - Notification message
 * @param {string} type - Notification type (info, success, error, warning)
 */
export function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out translate-x-full opacity-0`;
    
    // Set colors based on type
    const colors = {
        info: 'bg-blue-500 text-white',
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-black'
    };
    
    notification.className += ` ${colors[type] || colors.info}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="flex-1">${escapeHtml(message)}</div>
            <button class="ml-2 text-current hover:opacity-70" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full', 'opacity-0');
        notification.classList.add('translate-x-0', 'opacity-100');
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

/**
 * Clean city name by removing common suffixes
 * @param {string} cityName - City name to clean
 * @returns {string} Cleaned city name
 */
export function cleanCityName(cityName) {
    if (!cityName) return '';
    return cityName.replace(/\s+(city|City|CITY)$/, '').trim();
}

/**
 * Capitalize location string properly
 * @param {string} locationString - Location string to capitalize
 * @returns {string} Properly capitalized location
 */
export function capitalizeLocation(locationString) {
    if (!locationString) return '';
    
    return locationString
        .split(' ')
        .map(word => {
            // Handle special cases
            if (word.toLowerCase() === 'of') return 'of';
            if (word.toLowerCase() === 'the') return 'the';
            if (word.toLowerCase() === 'and') return 'and';
            
            // Capitalize first letter of each word
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        })
        .join(' ');
}

/**
 * Parse location from city string
 * @param {string} cityString - City string with potential state/country info
 * @returns {Object} Parsed location object
 */
export function parseLocationFromCity(cityString) {
    if (!cityString) return { city: '', state: '', country: 'US' };
    
    let city = cityString.trim();
    let state = '';
    let country = 'US';
    
    // Handle formats like "City, State" or "City, State, Country"
    const parts = city.split(',').map(part => part.trim());
    
    if (parts.length >= 2) {
        city = parts[0];
        state = parts[1];
        
        if (parts.length >= 3) {
            country = parts[2];
        }
    }
    
    return {
        city: capitalizeLocation(cleanCityName(city)),
        state: state.toUpperCase(),
        country: country.toUpperCase()
    };
}

/**
 * Parse weight and volume from strings
 * @param {string} weightStr - Weight string
 * @param {string} volumeStr - Volume string
 * @returns {Object} Parsed weight and volume object
 */
export function parseWeightAndVolume(weightStr, volumeStr) {
    const weightMatch = weightStr ? weightStr.match(/(\d+(?:\.\d+)?)\s*(\w+)/i) : null;
    const volumeMatch = volumeStr ? volumeStr.match(/(\d+(?:\.\d+)?)\s*(\w+)/i) : null;
    
    return {
        weight: {
            value: weightMatch ? parseFloat(weightMatch[1]) : 0,
            unit: weightMatch ? weightMatch[2].toLowerCase() : 'lbs'
        },
        volume: {
            value: volumeMatch ? parseFloat(volumeMatch[1]) : 0,
            unit: volumeMatch ? volumeMatch[2].toLowerCase() : 'cu ft'
        }
    };
}

/**
 * Build location object for API calls
 * @param {string} city - City name
 * @param {string} state - State code
 * @param {string} country - Country code (default: 'US')
 * @returns {Object} Location object
 */
export function buildLocationObject(city, state, country = 'US') {
    return {
        city: capitalizeLocation(cleanCityName(city)),
        state: state.toUpperCase(),
        country: country.toUpperCase()
    };
}

/**
 * Build item object for API calls
 * @param {number} weightValue - Weight value
 * @param {string} weightUnit - Weight unit
 * @param {number} volumeValue - Volume value
 * @param {string} volumeUnit - Volume unit
 * @returns {Object} Item object
 */
export function buildItemObject(weightValue, weightUnit, volumeValue, volumeUnit) {
    return {
        weight: {
            value: parseFloat(weightValue) || 0,
            unit: weightUnit || 'lbs'
        },
        volume: {
            value: parseFloat(volumeValue) || 0,
            unit: volumeUnit || 'cu ft'
        }
    };
}

/**
 * Format order date for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export function formatOrderDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return 'Invalid Date';
    }
}

/**
 * Clean service provider GID
 * @param {string} servprovGid - Service provider GID
 * @returns {string} Cleaned GID
 */
export function cleanServiceProviderGid(servprovGid) {
    if (!servprovGid) return '';
    
    // Remove BSL. prefix if present
    return servprovGid.replace(/^BSL\./, '');
} 