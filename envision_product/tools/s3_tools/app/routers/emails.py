"""
Router for email-related endpoints.

This module provides API endpoints for listing emails, retrieving attachments,
and downloading attachment data.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import io

from ..models.schemas import EmailInfo, AttachmentInfo
from ..services.auth_service import AuthService
from ..services.gmail_service import GmailService
from ..utils.attachment_utils import get_content_type

router = APIRouter(prefix="/api/emails", tags=["emails"])

# Dependency to get credentials
def get_credentials():
    """
    Get OAuth2 credentials for Gmail API.
    
    Returns:
        OAuth2 credentials
    
    Raises:
        HTTPException: If credentials are not available
    """
    auth_service = AuthService()
    credentials = auth_service.get_credentials()
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please authorize with Gmail API.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return credentials

# Dependency to get Gmail service
def get_gmail_service(credentials=Depends(get_credentials)):
    """
    Get Gmail service instance.
    
    Args:
        credentials: OAuth2 credentials
        
    Returns:
        GmailService instance
    """
    return GmailService(credentials)


@router.get("/", response_model=List[EmailInfo])
async def list_emails(
    max_results: Optional[int] = Query(20, description="Maximum number of emails to return"),
    filter_by_subject: bool = Query(True, description="Whether to filter emails by subject patterns"),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """
    List emails with CSV or JSON attachments.
    
    Args:
        max_results: Maximum number of emails to return
        filter_by_subject: Whether to filter emails by subject patterns
        gmail_service: Gmail service instance
        
    Returns:
        List of email information
    """
    try:
        emails = gmail_service.list_emails_with_attachments(
            max_results=max_results,
            filter_by_subject=filter_by_subject
        )
        
        # Convert to EmailInfo model
        return [
            EmailInfo(
                id=email['id'],
                subject=email['subject'],
                from_=email.get('from', 'Unknown Sender'),
                date=email.get('date', ''),
                has_target_attachments=email['has_target_attachments'],
                is_target_subject=email.get('is_target_subject', False)
            )
            for email in emails
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list emails: {str(e)}"
        )


@router.get("/{message_id}/attachments", response_model=List[AttachmentInfo])
async def list_attachments(
    message_id: str,
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """
    List attachments for a specific email.
    
    Args:
        message_id: ID of the email
        gmail_service: Gmail service instance
        
    Returns:
        List of attachment information
    """
    try:
        attachments = gmail_service.get_email_attachments(message_id)
        
        # Convert to AttachmentInfo model
        return [
            AttachmentInfo(
                id=attachment['id'],
                filename=attachment['filename'],
                mime_type=attachment['mime_type'],
                size=attachment['size'],
                is_target_file=attachment['is_target_file']
            )
            for attachment in attachments
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list attachments: {str(e)}"
        )


@router.get("/{message_id}/attachments/{attachment_id}")
async def download_attachment(
    message_id: str,
    attachment_id: str,
    expected_filename: Optional[str] = Query(None, description="Client-provided expected filename, typically from list_attachments"),
    expected_mime_type: Optional[str] = Query(None, description="Client-provided expected MIME type, typically from list_attachments"),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """
    Download a specific attachment.
    
    Args:
        message_id: ID of the email
        attachment_id: ID of the attachment
        expected_filename: Client-provided expected filename, typically from list_attachments
        expected_mime_type: Client-provided expected MIME type, typically from list_attachments
        gmail_service: Gmail service instance
        
    Returns:
        Streaming response with attachment data
    """
    try:
        attachment = gmail_service.get_attachment_data(
            message_id, 
            attachment_id,
            expected_filename=expected_filename, 
            expected_mime_type=expected_mime_type
        )
        
        # Set up streaming response
        return StreamingResponse(
            io.BytesIO(attachment['data']),
            media_type=attachment['mime_type'],
            headers={
                "Content-Disposition": f"attachment; filename={attachment['filename']}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download attachment: {str(e)}"
        ) 