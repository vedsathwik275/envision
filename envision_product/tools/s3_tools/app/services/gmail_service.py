"""
Gmail API service for interacting with Gmail.

This module provides functions for authenticating with the Gmail API
and retrieving emails and attachments.
"""
from typing import Dict, List, Optional
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings
from ..utils.attachment_utils import is_target_attachment, is_supported_file_type


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(self, credentials: Credentials):
        """
        Initialize the Gmail service with credentials.
        
        Args:
            credentials: OAuth2 credentials for Gmail API
        """
        self.credentials = credentials
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def list_emails_with_attachments(self, max_results: int = 20, filter_by_subject: bool = True) -> List[Dict]:
        """
        List emails with CSV or JSON attachments.
        
        Args:
            max_results: Maximum number of emails to return
            filter_by_subject: Whether to filter emails by subject patterns
            
        Returns:
            List of email information dictionaries
            
        Raises:
            HttpError: If an API error occurs
        """
        try:
            # Build the query for emails with attachments
            query = 'has:attachment filename:(*.csv OR *.json)'
            
            # Add subject filters if enabled
            if filter_by_subject and settings.target_subjects:
                subject_filters = []
                for subject_pattern in settings.target_subjects:
                    subject_filters.append(f'subject:"{subject_pattern}"')
                
                if subject_filters:
                    subject_query = ' OR '.join(subject_filters)
                    query = f'{query} AND ({subject_query})'
            
            # Query for emails with attachments
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get more details for each message
            emails_with_attachments = []
            for message in messages:
                details = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                # Extract subject
                headers = details.get('payload', {}).get('headers', [])
                subject = next(
                    (header['value'] for header in headers if header['name'] == 'Subject'),
                    'No Subject'
                )
                
                # Extract sender
                from_header = next(
                    (header['value'] for header in headers if header['name'] == 'From'),
                    'Unknown Sender'
                )
                
                # Extract date
                date_header = next(
                    (header['value'] for header in headers if header['name'] == 'Date'),
                    ''
                )
                
                # Check if subject matches any target patterns
                is_target_subject = any(pattern.lower() in subject.lower() for pattern in settings.target_subjects)
                
                # Find all attachments recursively
                attachments = self._find_all_attachments(details.get('payload', {}))
                
                # Check if any attachment is a target attachment
                has_target_attachments = any(
                    attachment.get('is_target_file', False) for attachment in attachments
                )
                
                emails_with_attachments.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': from_header,
                    'date': date_header,
                    'has_target_attachments': has_target_attachments,
                    'is_target_subject': is_target_subject
                })
            
            return emails_with_attachments
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def get_email_attachments(self, message_id: str) -> List[Dict]:
        """
        Get attachments for a specific email.
        
        Args:
            message_id: ID of the email
            
        Returns:
            List of attachment information dictionaries
            
        Raises:
            HttpError: If an API error occurs
        """
        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Find all attachments recursively
            return self._find_all_attachments(message.get('payload', {}))
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def _find_all_attachments(self, payload: Dict) -> List[Dict]:
        """
        Recursively find all attachments in a message payload.
        
        Args:
            payload: Message payload or part
            
        Returns:
            List of attachment information dictionaries
        """
        attachments = []
        
        # Check if current part is an attachment
        if (payload.get('filename') and 
            payload.get('body', {}).get('attachmentId') and 
            is_supported_file_type(payload.get('filename'))):
            
            filename = payload.get('filename')
            attachments.append({
                'id': payload['body']['attachmentId'],
                'filename': filename,
                'mime_type': payload.get('mimeType', 'application/octet-stream'),
                'size': payload['body'].get('size', 0),
                'is_target_file': is_target_attachment(filename)
            })
        
        # Check parts recursively
        for part in payload.get('parts', []):
            attachments.extend(self._find_all_attachments(part))
        
        return attachments
    
    def get_attachment_data(self, message_id: str, attachment_id: str) -> Dict:
        """
        Get data for a specific attachment.
        
        Args:
            message_id: ID of the email
            attachment_id: ID of the attachment
            
        Returns:
            Dictionary with attachment data and metadata
            
        Raises:
            HttpError: If an API error occurs
        """
        try:
            # Get message details to find attachment metadata
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Find attachment info by recursively searching through all parts
            attachment_info = self._find_attachment_part(message.get('payload', {}), attachment_id)
            
            if not attachment_info:
                # If not found, try to get attachment directly without metadata
                try:
                    attachment = self.service.users().messages().attachments().get(
                        userId='me',
                        messageId=message_id,
                        id=attachment_id
                    ).execute()
                    
                    # Decode attachment data
                    file_data = base64.urlsafe_b64decode(attachment.get('data', ''))
                    
                    # Return with minimal info since we couldn't find the part
                    return {
                        'filename': 'attachment',
                        'mime_type': 'application/octet-stream',
                        'size': len(file_data),
                        'data': file_data
                    }
                except Exception as e:
                    print(f"Failed to get attachment directly: {e}")
                    raise ValueError("Attachment not found")
            
            # Get attachment data
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            # Decode attachment data
            file_data = base64.urlsafe_b64decode(attachment.get('data', ''))
            
            return {
                'filename': attachment_info.get('filename', 'attachment'),
                'mime_type': attachment_info.get('mimeType', 'application/octet-stream'),
                'size': len(file_data),
                'data': file_data
            }
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def _find_attachment_part(self, payload: Dict, attachment_id: str) -> Optional[Dict]:
        """
        Recursively search for an attachment part with the given ID.
        
        Args:
            payload: Message payload or part
            attachment_id: ID of the attachment to find
            
        Returns:
            Dict or None: The attachment part if found, None otherwise
        """
        # Check if current part has the attachment ID
        if payload.get('body', {}).get('attachmentId') == attachment_id:
            return payload
        
        # Check parts recursively
        parts = payload.get('parts', [])
        for part in parts:
            result = self._find_attachment_part(part, attachment_id)
            if result:
                return result
        
        return None 