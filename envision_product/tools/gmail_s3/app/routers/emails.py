"""
Router for email-related endpoints.

This module provides API endpoints for listing emails, retrieving attachments,
and downloading attachment data.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import io

from ..models.schemas import EmailInfo, AttachmentInfo, UploadResponse
from ..services.auth_service import AuthService
from ..services.gmail_service import GmailService
from ..services.s3_service import S3Service
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

# Dependency to get S3 service
def get_s3_service():
    """
    Get S3 service instance.
    
    Returns:
        S3Service instance
    
    Raises:
        HTTPException: If S3 service cannot be initialized (e.g., due to config issues).
    """
    try:
        return S3Service()
    except ValueError as e:
        # Raised by S3Service __init__ if config is missing
        raise HTTPException(status_code=500, detail=f"S3 Service initialization failed: {str(e)}")


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

@router.post("/{message_id}/attachments/{attachment_id}/upload", response_model=UploadResponse)
async def upload_attachment_to_s3(
    message_id: str,
    attachment_id: str,
    expected_filename: Optional[str] = Query(None, description="Client-provided expected filename, typically from list_attachments"),
    expected_mime_type: Optional[str] = Query(None, description="Client-provided expected MIME type, typically from list_attachments"),
    gmail_service: GmailService = Depends(get_gmail_service),
    s3_service: S3Service = Depends(get_s3_service)
):
    """
    Download a specific attachment from Gmail and upload it to S3.

    Args:
        message_id: ID of the email.
        attachment_id: ID of the attachment.
        expected_filename: Optional. Client-provided expected filename to ensure correct data retrieval.
        expected_mime_type: Optional. Client-provided expected MIME type.
        gmail_service: Gmail service instance.
        s3_service: S3 service instance.

    Returns:
        UploadResponse: Information about the S3 upload.
    """
    try:
        # 1. Get attachment data from Gmail, using client hints if provided
        print(f"Attempting to get attachment data for message_id: {message_id}, attachment_id: {attachment_id}, expected_filename: {expected_filename}, expected_mime_type: {expected_mime_type}")
        attachment_data = gmail_service.get_attachment_data(
            message_id, 
            attachment_id,
            expected_filename=expected_filename,
            expected_mime_type=expected_mime_type
        )
        
        original_filename = attachment_data['filename']
        file_bytes = attachment_data['data']
        mime_type = attachment_data['mime_type']
        file_size = attachment_data['size']

        print(f"Retrieved attachment: {original_filename}, MIME: {mime_type}, Size: {file_size}")

        # Define the S3 object key (filename in S3). 
        # You might want to prefix with message_id or a date structure for organization.
        # For now, using original filename but could be made more unique.
        s3_object_key = f"attachments/{message_id}/{original_filename}" 

        # 2. Upload to S3
        print(f"Uploading {s3_object_key} to S3 bucket: {s3_service.s3_bucket_name}")
        upload_result = s3_service.upload_to_s3(
            file_data=file_bytes,
            filename=s3_object_key, # This is the key in S3
            content_type=mime_type
        )
        print(f"Successfully uploaded to S3. URL: {upload_result['s3_url']}, Object Key: {upload_result['object_key']}")

        # 3. Construct and return UploadResponse
        return UploadResponse(
            success=True,
            filename=original_filename, # The original attachment filename
            s3_location=upload_result['s3_url'],
            metadata={
                "object_key": upload_result['object_key'],
                "content_type": mime_type,
                "size_bytes": str(file_size),
                "original_attachment_id": attachment_id,
                "email_message_id": message_id
            }
        )

    except ValueError as e:
        # Specific errors like attachment not found from GmailService
        raise HTTPException(status_code=404, detail=str(e))
    except NoCredentialsError as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload Failed: AWS Credentials Error - {str(e)}")
    except PartialCredentialsError as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload Failed: AWS Partial Credentials Error - {str(e)}")
    except ClientError as e:
        # Catching Boto3 specific client errors
        error_message = e.response.get('Error', {}).get('Message', str(e))
        raise HTTPException(status_code=500, detail=f"S3 Upload Failed: {error_message}")
    except Exception as e:
        # Catch-all for other unexpected errors
        print(f"Unhandled error during S3 upload: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 