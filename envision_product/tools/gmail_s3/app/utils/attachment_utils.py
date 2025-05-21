"""
Utility functions for working with email attachments.
"""
from typing import List, Optional
import mimetypes

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


def get_extension_from_mime_type(mime_type: str) -> Optional[str]:
    """
    Guess file extension from MIME type.

    Args:
        mime_type: The MIME type string.

    Returns:
        Optional[str]: The guessed file extension (e.g., '.csv') or None.
    """
    if not mime_type:
        return None
    
    # Explicitly handle variations of text/csv first for robustness
    # to ensure it always yields .csv if the MIME type is for CSV.
    cleaned_mime_type = mime_type.lower().strip()
    if cleaned_mime_type == 'text/csv':
        return '.csv'
    
    # Common direct mappings for frequently used types for more reliability
    common_extensions = {
        'text/csv': '.csv',
        'application/json': '.json',
        'application/pdf': '.pdf',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-excel': '.xls',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'text/plain': '.txt',
    }
    
    extension = common_extensions.get(cleaned_mime_type)
    if extension:
        return extension
        
    # Fallback to mimetypes module
    extension = mimetypes.guess_extension(cleaned_mime_type, strict=False)
    return extension 