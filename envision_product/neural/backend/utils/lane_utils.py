#!/usr/bin/env python3
"""
Lane Handling Utility for Envision Neural API.

This module provides standardized functions for lane identification and matching,
as well as helper functions for lane-based filtering. These utilities ensure consistent
handling of lanes across different parts of the application, regardless of field naming
conventions or capitalization.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union

logger = logging.getLogger(__name__)

# Define common field name variations
SOURCE_CITY_FIELDS = [
    "source_city", "SOURCE CITY", "SOURCE", "src", "SRC", "source", "origin", "ORIGIN"
]

DESTINATION_CITY_FIELDS = [
    "destination_city", "DESTINATION CITY", "DESTINATION", "dest", "DEST", "dst", "DST", 
    "destination", "DEST CITY", "dest_city"
]

ORDER_TYPE_FIELDS = [
    "order_type", "ORDER TYPE", "type", "TYPE", "shipment_type", "SHIPMENT_TYPE"
]

CARRIER_FIELDS = [
    "carrier", "CARRIER", "carrier_name", "CARRIER_NAME"
]

def normalize_city_name(city: str) -> str:
    """
    Normalize a city name to ensure consistent matching.
    
    Args:
        city: The city name to normalize
        
    Returns:
        Normalized city name (uppercase with special characters removed)
    """
    if not city:
        return ""
    
    # Convert to uppercase for case-insensitive matching
    normalized = city.strip().upper()
    
    # Remove special characters that might affect matching
    for char in [',', '.', '-', '_', '(', ')', '/']:
        normalized = normalized.replace(char, ' ')
    
    # Normalize whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized

def get_value_from_dict_with_variations(data: Dict[str, Any], field_variations: List[str]) -> Optional[str]:
    """
    Get a value from a dictionary by trying multiple field name variations.
    
    Args:
        data: The dictionary to search
        field_variations: List of possible field names to try
        
    Returns:
        The value if found, or None
    """
    for field in field_variations:
        if field in data:
            value = data[field]
            if value is not None:
                return str(value)
    return None

def get_lane_components(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Extract standardized lane components from a data dictionary.
    
    Args:
        data: Dictionary containing lane data
        
    Returns:
        Tuple of (source_city, destination_city, carrier, order_type)
    """
    source_city = get_value_from_dict_with_variations(data, SOURCE_CITY_FIELDS)
    destination_city = get_value_from_dict_with_variations(data, DESTINATION_CITY_FIELDS)
    carrier = get_value_from_dict_with_variations(data, CARRIER_FIELDS)
    order_type = get_value_from_dict_with_variations(data, ORDER_TYPE_FIELDS)
    
    # Normalize city names if present
    if source_city:
        source_city = normalize_city_name(source_city)
    if destination_city:
        destination_city = normalize_city_name(destination_city)
    
    return source_city, destination_city, carrier, order_type

def get_lane_id(data: Dict[str, Any], include_carrier: bool = True, include_order_type: bool = True) -> str:
    """
    Generate a standardized lane ID from data.
    
    Args:
        data: Dictionary containing lane data
        include_carrier: Whether to include carrier in the lane ID
        include_order_type: Whether to include order type in the lane ID
        
    Returns:
        Standardized lane ID string
    """
    source_city, destination_city, carrier, order_type = get_lane_components(data)
    
    if not source_city or not destination_city:
        return ""
    
    lane_id_parts = [source_city, destination_city]
    
    if include_carrier and carrier:
        lane_id_parts.append(carrier)
    
    if include_order_type and order_type:
        lane_id_parts.append(order_type)
    
    return "_".join(lane_id_parts)

def is_lane_match(
    data: Dict[str, Any],
    source_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    carrier: Optional[str] = None,
    order_type: Optional[str] = None
) -> bool:
    """
    Check if data matches the specified lane criteria.
    
    Args:
        data: Dictionary containing lane data
        source_city: Source city to match (optional)
        destination_city: Destination city to match (optional)
        carrier: Carrier to match (optional)
        order_type: Order type to match (optional)
        
    Returns:
        True if data matches all provided criteria, False otherwise
    """
    # Extract standardized components from data
    data_source, data_dest, data_carrier, data_order_type = get_lane_components(data)
    
    # Match each specified criterion
    if source_city and (not data_source or normalize_city_name(source_city) != data_source):
        return False
    
    if destination_city and (not data_dest or normalize_city_name(destination_city) != data_dest):
        return False
    
    if carrier and (not data_carrier or carrier.upper() != data_carrier.upper()):
        return False
    
    if order_type and (not data_order_type or order_type.upper() != data_order_type.upper()):
        return False
    
    return True

def filter_by_lane(
    data_list: List[Dict[str, Any]],
    source_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    carrier: Optional[str] = None,
    order_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter a list of dictionaries by lane criteria.
    
    Args:
        data_list: List of dictionaries to filter
        source_city: Source city to match (optional)
        destination_city: Destination city to match (optional)
        carrier: Carrier to match (optional)
        order_type: Order type to match (optional)
        
    Returns:
        Filtered list of dictionaries
    """
    if not data_list:
        return []
    
    # If no filters provided, return the original list
    if not any([source_city, destination_city, carrier, order_type]):
        return data_list
    
    # Normalize filter parameters if provided
    norm_source = normalize_city_name(source_city) if source_city else None
    norm_dest = normalize_city_name(destination_city) if destination_city else None
    
    result = []
    for item in data_list:
        if is_lane_match(
            data=item,
            source_city=norm_source,
            destination_city=norm_dest,
            carrier=carrier,
            order_type=order_type
        ):
            result.append(item)
    
    return result

def standardize_lane_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize lane-related fields in a dictionary to use consistent field names.
    
    Args:
        data: Dictionary containing lane data
        
    Returns:
        Dictionary with standardized field names
    """
    result = dict(data)  # Create a copy to avoid modifying the original
    
    # Extract values using variations
    source_city = get_value_from_dict_with_variations(data, SOURCE_CITY_FIELDS)
    destination_city = get_value_from_dict_with_variations(data, DESTINATION_CITY_FIELDS)
    carrier = get_value_from_dict_with_variations(data, CARRIER_FIELDS)
    order_type = get_value_from_dict_with_variations(data, ORDER_TYPE_FIELDS)
    
    # Add standardized fields if values were found
    if source_city:
        result['source_city'] = source_city
    
    if destination_city:
        result['destination_city'] = destination_city
    
    if carrier:
        result['carrier'] = carrier
    
    if order_type:
        result['order_type'] = order_type
    
    return result

def batch_standardize_lane_fields(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Standardize lane fields for a list of dictionaries.
    
    Args:
        data_list: List of dictionaries to standardize
        
    Returns:
        List of dictionaries with standardized fields
    """
    return [standardize_lane_fields(item) for item in data_list]

def group_by_lane(
    data_list: List[Dict[str, Any]],
    include_carrier: bool = True,
    include_order_type: bool = False
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group data by lane.
    
    Args:
        data_list: List of dictionaries to group
        include_carrier: Whether to include carrier in the lane grouping
        include_order_type: Whether to include order type in the lane grouping
        
    Returns:
        Dictionary with lane IDs as keys and lists of matching items as values
    """
    result = {}
    
    for item in data_list:
        lane_id = get_lane_id(
            item, 
            include_carrier=include_carrier, 
            include_order_type=include_order_type
        )
        
        if not lane_id:
            continue
        
        if lane_id not in result:
            result[lane_id] = []
        
        result[lane_id].append(item)
    
    return result 