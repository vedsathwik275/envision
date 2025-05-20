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
import os

from ..config import settings
from ..utils.attachment_utils import is_target_attachment, is_supported_file_type, get_extension_from_mime_type


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
    
    def get_attachment_data(self, message_id: str, attachment_id: str, expected_filename: Optional[str] = None, expected_mime_type: Optional[str] = None) -> Dict:
        """
        Get data for a specific attachment.
        
        Args:
            message_id: ID of the email
            attachment_id: ID of the attachment
            expected_filename: Optional client-provided filename
            expected_mime_type: Optional client-provided MIME type
            
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
            
            # Get attachment data first, as we need it regardless
            try:
                attachment_data_response = self.service.users().messages().attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=attachment_id
                ).execute()
                file_data = base64.urlsafe_b64decode(attachment_data_response.get('data', ''))
            except HttpError as e:
                # This means the attachmentId itself is invalid or data is inaccessible
                print(f"Failed to get attachment data directly for id {attachment_id}: {e}")
                raise ValueError("Attachment data not found or inaccessible")

            # filename and mime_type are temps within this block
            filename_to_use = "attachment"
            mimetype_to_use = "application/octet-stream"

            if expected_filename and expected_mime_type: # Both client hints are present
                print(f"DEBUG GmailService: Client provided expected_filename: '{expected_filename}', raw expected_mime_type: '{expected_mime_type}'")
                
                filename_to_use = expected_filename
                
                # Normalize client-provided expected_mime_type for common shorthands
                normalized_client_mime_shorthand = expected_mime_type.lower().strip()
                if normalized_client_mime_shorthand == 'csv':
                    mimetype_to_use = 'text/csv'
                elif normalized_client_mime_shorthand == 'json':
                    mimetype_to_use = 'application/json'
                # Add other common shorthands if desired, e.g.:
                # elif normalized_client_mime_shorthand == 'pdf':
                #     mimetype_to_use = 'application/pdf'
                # elif normalized_client_mime_shorthand == 'txt':
                #     mimetype_to_use = 'text/plain'
                else:
                    # If not a known shorthand, assume it might be a full MIME type or one that
                    # get_extension_from_mime_type can handle directly. Use original value.
                    mimetype_to_use = expected_mime_type
                
                print(f"DEBUG GmailService: Using filename_to_use: '{filename_to_use}', mimetype_to_use (post-client-normalization): '{mimetype_to_use}'")

            elif attachment_info: # No client hints, but found metadata in email part
                filename_to_use = attachment_info.get('filename', filename_to_use)
                mimetype_to_use = attachment_info.get('mimeType', mimetype_to_use)
                print(f"DEBUG GmailService: Found attachment_info. Raw filename from part: '{filename_to_use}', Raw mime_type from part: '{mimetype_to_use}'")
            else:
                # If _find_attachment_part didn't find detailed metadata, and no client override
                # Log this situation. We already have file_data.
                print(f"DEBUG GmailService: attachment_info is None for attachmentId: {attachment_id}. Using default filename/mime_type before refinement.")

            # Store these for clarity in subsequent logic and final return
            effective_filename_from_part = filename_to_use
            effective_mimetype_from_part = mimetype_to_use

            # Refine filename based on MIME type
            # Initialize current_ext, it will be updated if filename is specific
            current_ext = ""
            if not effective_filename_from_part or effective_filename_from_part.lower() == "attachment":
                base_name = "downloaded_attachment"
            else:
                base_name, current_ext = os.path.splitext(effective_filename_from_part)
            
            print(f"DEBUG GmailService: Before derivation: base_name='{base_name}', current_ext='{current_ext}', effective_mimetype_from_part='{effective_mimetype_from_part}'")
            derived_extension = get_extension_from_mime_type(effective_mimetype_from_part)
            print(f"DEBUG GmailService: Derived extension: '{derived_extension}' for mime_type: '{effective_mimetype_from_part}'")
            
            final_filename = effective_filename_from_part

            if derived_extension:
                if effective_filename_from_part.lower() == "attachment" or not current_ext:
                    final_filename = base_name + derived_extension
                elif current_ext.lower() != derived_extension.lower():
                    final_filename = base_name + derived_extension
                    print(f"DEBUG GmailService: Corrected extension for {base_name} from {current_ext} to {derived_extension} based on MIME type {effective_mimetype_from_part}")
            elif not current_ext and effective_filename_from_part.lower() != "attachment":
                pass # final_filename is already effective_filename_from_part (specific name, no extension, no derived extension)
            elif effective_filename_from_part.lower() == "attachment": # Generic name, no derived extension
                final_filename = "downloaded_file"

            print(f"DEBUG GmailService: Final filename determined: '{final_filename}'")

            return {
                'filename': final_filename,
                'mime_type': effective_mimetype_from_part, # Return the mime_type used for decisions
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
            Optional[Dict]: The part containing the attachment, or None if not found.
        """
        if payload.get('body', {}).get('attachmentId') == attachment_id:
            # Ensure the found part has filename and mimeType, even if empty strings
            # so .get() in the caller doesn't unexpectedly fail if keys are missing
            # Defaulting them here if absent is not ideal as it masks true absence,
            # but the caller uses .get() with defaults anyway.
            # The main goal is to return the part if ID matches.
            return payload
        
        # Check parts recursively
        parts = payload.get('parts', [])
        for part in parts:
            result = self._find_attachment_part(part, attachment_id)
            if result:
                return result
        
        return None 