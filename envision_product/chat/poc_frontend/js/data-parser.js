/**
 * Data parsing utilities
 * Lane information parsing, location parsing, weight/volume parsing, carrier mapping
 */

import { cleanCityName, capitalizeLocation, parseLocationFromCity, buildLocationObject, buildItemObject } from './utils.js';

/**
 * Parse and update lane information from chat response
 * @param {string} userMessage - User's message
 * @param {Object} response - Chat response object
 */
export function parseAndUpdateLaneInfo(userMessage, response) {
    const laneInfo = parseLaneInformationFromResponse(response.answer);
    
    if (laneInfo && (laneInfo.sourceCity || laneInfo.destinationCity)) {
        // Store the extracted lane information globally
        window.currentLaneInfo = laneInfo;
        console.log('Lane information extracted:', laneInfo);
        
        // Check what type of prompt this is and update appropriate cards
        if (isRateInquiryPrompt(userMessage)) {
            if (window.updateRateInquiryCard) {
                window.updateRateInquiryCard(laneInfo, userMessage, response);
            }
        }
        
        if (isSpotAPIPrompt(userMessage)) {
            if (window.updateSpotAPICard) {
                window.updateSpotAPICard(laneInfo, userMessage, response);
            }
        }
        
        // Always try to update historical data and order release cards if they don't conflict
        if (window.updateHistoricalDataCard) {
            window.updateHistoricalDataCard(laneInfo, userMessage, response);
        }
        
        if (window.updateOrderReleaseCard) {
            window.updateOrderReleaseCard(laneInfo, userMessage, response);
        }
    }
}

/**
 * Parse lane information from response text
 * @param {string} answer - AI response text
 * @returns {Object|null} Parsed lane information
 */
export function parseLaneInformationFromResponse(answer) {
    if (!answer || typeof answer !== 'string') return null;
    
    const laneInfo = {};
    
    // Extract origin/source information
    const originPatterns = [
        /origin[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /from[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /source[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /pickup[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /starting[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i
    ];
    
    for (const pattern of originPatterns) {
        const match = answer.match(pattern);
        if (match) {
            const location = parseLocationFromCity(match[1].trim());
            laneInfo.sourceCity = location.city;
            laneInfo.sourceState = location.state;
            laneInfo.sourceCountry = location.country;
            break;
        }
    }
    
    // Extract destination information
    const destinationPatterns = [
        /destination[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /to[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /delivery[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /drop[:\s]*off[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i,
        /ending[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)/i
    ];
    
    for (const pattern of destinationPatterns) {
        const match = answer.match(pattern);
        if (match) {
            const location = parseLocationFromCity(match[1].trim());
            laneInfo.destinationCity = location.city;
            laneInfo.destinationState = location.state;
            laneInfo.destinationCountry = location.country;
            break;
        }
    }
    
    // Extract weight information
    const weightPatterns = [
        /weight[:\s]+(\d+(?:\.\d+)?)\s*(\w+)/i,
        /(\d+(?:\.\d+)?)\s*(lbs?|pounds?|tons?|kg|kilograms?)/i,
        /weighs?\s+(\d+(?:\.\d+)?)\s*(\w+)/i
    ];
    
    for (const pattern of weightPatterns) {
        const match = answer.match(pattern);
        if (match) {
            laneInfo.weight = `${match[1]} ${match[2]}`;
            break;
        }
    }
    
    // Extract volume/capacity information
    const volumePatterns = [
        /volume[:\s]+(\d+(?:\.\d+)?)\s*(\w+)/i,
        /(\d+(?:\.\d+)?)\s*(cubic\s*feet|cu\s*ft|cf)/i,
        /capacity[:\s]+(\d+(?:\.\d+)?)\s*(\w+)/i
    ];
    
    for (const pattern of volumePatterns) {
        const match = answer.match(pattern);
        if (match) {
            laneInfo.volume = `${match[1]} ${match[2]}`;
            break;
        }
    }
    
    // Extract equipment type
    const equipmentPatterns = [
        /equipment[:\s]+([^\n,]+)/i,
        /trailer[:\s]+([^\n,]+)/i,
        /(dry\s*van|refrigerated|flatbed|step\s*deck|lowboy)/i
    ];
    
    for (const pattern of equipmentPatterns) {
        const match = answer.match(pattern);
        if (match) {
            laneInfo.equipmentType = match[1].trim();
            break;
        }
    }
    
    // Extract service type
    const servicePatterns = [
        /service[:\s]+([^\n,]+)/i,
        /(LTL|TL|less\s*than\s*truckload|truckload|full\s*truckload)/i
    ];
    
    for (const pattern of servicePatterns) {
        const match = answer.match(pattern);
        if (match) {
            laneInfo.serviceType = match[1].trim();
            break;
        }
    }
    
    // Extract carrier preference if mentioned
    const carrierPatterns = [
        /carrier[:\s]+([^\n,]+)/i,
        /using[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i,
        /with[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+carrier/i
    ];
    
    for (const pattern of carrierPatterns) {
        const match = answer.match(pattern);
        if (match) {
            laneInfo.preferredCarrier = match[1].trim();
            break;
        }
    }
    
    // Create lane name
    if (laneInfo.sourceCity && laneInfo.destinationCity) {
        const sourceDisplay = laneInfo.sourceState ? 
            `${laneInfo.sourceCity}, ${laneInfo.sourceState}` : 
            laneInfo.sourceCity;
        const destDisplay = laneInfo.destinationState ? 
            `${laneInfo.destinationCity}, ${laneInfo.destinationState}` : 
            laneInfo.destinationCity;
        
        laneInfo.laneName = `${sourceDisplay} → ${destDisplay}`;
    }
    
    // Return null if no meaningful information was extracted
    if (!laneInfo.sourceCity && !laneInfo.destinationCity && !laneInfo.weight && !laneInfo.volume) {
        return null;
    }
    
    return laneInfo;
}

/**
 * Check if message is a rate inquiry prompt
 * @param {string} message - User message
 * @returns {boolean} True if rate inquiry
 */
export function isRateInquiryPrompt(message) {
    const rateKeywords = [
        'rate', 'rates', 'quote', 'quotes', 'pricing', 'price', 'cost', 'costs',
        'freight rate', 'shipping rate', 'transportation rate', 'trucking rate',
        'how much', 'what does it cost', 'price to ship', 'cost to transport'
    ];
    
    return rateKeywords.some(keyword => 
        message.toLowerCase().includes(keyword.toLowerCase())
    );
}

/**
 * Check if message is a spot API prompt
 * @param {string} message - User message
 * @returns {boolean} True if spot API related
 */
export function isSpotAPIPrompt(message) {
    const spotKeywords = [
        'spot', 'spot rate', 'spot market', 'spot price', 'market rate',
        'current market', 'spot analysis', 'market analysis', 'daily rates',
        'market conditions', 'spot pricing'
    ];
    
    return spotKeywords.some(keyword => 
        message.toLowerCase().includes(keyword.toLowerCase())
    );
}

/**
 * Map carrier name to service provider GID
 * @param {string} carrierName - Carrier name
 * @returns {string} Service provider GID
 */
export function mapCarrierToServprovGid(carrierName) {
    if (!carrierName) return '';
    
    // Clean up the carrier name
    const cleanName = carrierName.trim().toUpperCase();
    
    // Common carrier mappings
    const carrierMappings = {
        'FEDEX': 'BSL.FEDEX_FREIGHT',
        'FEDEX FREIGHT': 'BSL.FEDEX_FREIGHT',
        'UPS': 'BSL.UPS_FREIGHT',
        'UPS FREIGHT': 'BSL.UPS_FREIGHT',
        'XPO': 'BSL.XPO_LOGISTICS',
        'XPO LOGISTICS': 'BSL.XPO_LOGISTICS',
        'OLD DOMINION': 'BSL.OLD_DOMINION',
        'SAIA': 'BSL.SAIA_LTL_FREIGHT',
        'ESTES': 'BSL.ESTES_EXPRESS',
        'ABF': 'BSL.ABF_FREIGHT',
        'YELLOW': 'BSL.YELLOW_FREIGHT',
        'SCHNEIDER': 'BSL.SCHNEIDER_NATIONAL',
        'JB HUNT': 'BSL.JB_HUNT',
        'SWIFT': 'BSL.SWIFT_TRANSPORTATION',
        'WERNER': 'BSL.WERNER_ENTERPRISES'
    };
    
    // Check for exact match first
    if (carrierMappings[cleanName]) {
        return carrierMappings[cleanName];
    }
    
    // Check for partial matches
    for (const [key, value] of Object.entries(carrierMappings)) {
        if (cleanName.includes(key) || key.includes(cleanName)) {
            return value;
        }
    }
    
    // If no mapping found, return a formatted GID
    const formattedName = cleanName.replace(/\s+/g, '_').replace(/[^A-Z0-9_]/g, '');
    return `BSL.${formattedName}`;
}

/**
 * Parse weight and volume from strings with custom logic
 * @param {string} weightStr - Weight string
 * @param {string} volumeStr - Volume string  
 * @returns {Object} Parsed values
 */
export function parseWeightAndVolumeLocal(weightStr, volumeStr) {
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
 * @param {Object} laneInfo - Lane information
 * @param {string} type - 'source' or 'destination'
 * @returns {Object} Location object
 */
export function buildLocationFromLaneInfo(laneInfo, type) {
    const city = type === 'source' ? laneInfo.sourceCity : laneInfo.destinationCity;
    const state = type === 'source' ? laneInfo.sourceState : laneInfo.destinationState;
    const country = type === 'source' ? (laneInfo.sourceCountry || 'US') : (laneInfo.destinationCountry || 'US');
    
    return buildLocationObject(city, state, country);
}

/**
 * Build item object from lane info for API calls
 * @param {Object} laneInfo - Lane information
 * @returns {Object} Item object
 */
export function buildItemFromLaneInfo(laneInfo) {
    const { weight, volume } = parseWeightAndVolumeLocal(laneInfo.weight, laneInfo.volume);
    return buildItemObject(weight.value, weight.unit, volume.value, volume.unit);
}

/**
 * Extract numerical values from strings
 * @param {string} str - String containing numbers
 * @returns {number} Extracted number or 0
 */
export function extractNumber(str) {
    if (!str) return 0;
    const match = str.match(/(\d+(?:\.\d+)?)/);
    return match ? parseFloat(match[1]) : 0;
}

/**
 * Extract unit from strings
 * @param {string} str - String containing unit
 * @returns {string} Extracted unit or default
 */
export function extractUnit(str) {
    if (!str) return '';
    const match = str.match(/\d+(?:\.\d+)?\s*(\w+)/);
    return match ? match[1] : '';
}

/**
 * Validate lane information completeness
 * @param {Object} laneInfo - Lane information object
 * @returns {Object} Validation result
 */
export function validateLaneInfo(laneInfo) {
    const errors = [];
    const warnings = [];
    
    if (!laneInfo.sourceCity) {
        errors.push('Source city is required');
    }
    
    if (!laneInfo.destinationCity) {
        errors.push('Destination city is required');
    }
    
    if (!laneInfo.weight && !laneInfo.volume) {
        warnings.push('Weight or volume information is recommended for accurate quotes');
    }
    
    return {
        isValid: errors.length === 0,
        errors,
        warnings
    };
} 