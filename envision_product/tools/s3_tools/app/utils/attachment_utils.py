"""
Utility functions for working with email attachments.
"""
from typing import List

from ..config import settings


def is_target_attachment(filename: str) -> bool:
    """
    Check if a filename is in the target list.
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the filename is in the target list, False otherwise
    """
    # Check if any target filename is contained within the attachment filename
    # This is more flexible than exact matching
    return any(target.lower() in filename.lower() for target in settings.target_filenames)


def is_supported_file_type(filename: str) -> bool:
    """
    Check if a file is a supported type (CSV or JSON).
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the file is a supported type, False otherwise
    """
    return filename.lower().endswith(('.csv', '.json'))


def get_content_type(filename: str) -> str:
    """
    Get the content type for a filename.
    
    Args:
        filename: The filename to check
        
    Returns:
        str: The content type for the file
    """
    if filename.lower().endswith('.csv'):
        return 'text/csv'
    elif filename.lower().endswith('.json'):
        return 'application/json'
    else:
        return 'application/octet-stream'


def get_target_filenames() -> List[str]:
    """
    Get the list of target filenames from settings.
    
    Returns:
        List[str]: The list of target filenames
    """
    return settings.target_filenames 