# Email Attachment Processing Tool - Proof of Concept

## Overview

This document outlines a proof of concept for an automated tool built with Python FastAPI that extracts specific CSV and JSON attachments from incoming emails and uploads them to an Amazon S3 bucket. The tool identifies target files based on predefined attachment names and stores relevant metadata alongside the files.

## System Architecture

```
┌─────────────┐    ┌───────────────┐    ┌────────────────┐
│  Gmail API  │───▶│ API Endpoint  │───▶│ Amazon S3      │
│             │    │ for Attachment│    │ Bucket         │
│             │    │ Processing    │    │                │
└─────────────┘    └───────────────┘    └────────────────┘
                          ▲
                          │
                   ┌──────────────┐
                   │ Existing     │
                   │ Frontend     │
                   │ (Future)     │
                   └──────────────┘
```

## Core Functionality

1. **API First Approach**: Build standalone API endpoints for all attachment processing functionality
2. **Email Monitoring**: Access new emails using Gmail API through API endpoints
3. **Attachment Identification**: Identify specific CSV/JSON attachments by filename
4. **Two-Phase Testing**:
   - Phase 1: Test downloading Gmail attachments locally
   - Phase 2: Test direct upload to S3 bucket
5. **Metadata Tracking**: Record timestamps and file metadata

## Technical Components

### 1. Email Service Integration

The solution will utilize the Gmail API with Python to:
- Authenticate using OAuth 2.0
- Query for new unread emails containing attachments
- Filter emails based on attachment filename patterns

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_emails_with_attachments(credentials):
    """Get emails with CSV or JSON attachments."""
    service = build('gmail', 'v1', credentials=credentials)
    
    # Query for emails with attachments
    results = service.users().messages().list(
        userId='me',
        q='has:attachment filename:(*.csv OR *.json)'
    ).execute()
    
    messages = results.get('messages', [])
    return messages
```

### 2. Attachment Processing

```python
import base64

def process_attachments(credentials, message_id):
    """Process attachments from a specific email."""
    service = build('gmail', 'v1', credentials=credentials)
    
    # Get message details
    message = service.users().messages().get(
        userId='me',
        id=message_id
    ).execute()
    
    # Get message payload parts
    payload = message.get('payload', {})
    parts = payload.get('parts', [])
    
    # Filter for attachments and only CSV/JSON files
    attachment_parts = [
        part for part in parts 
        if part.get('filename') and (
            part.get('filename').endswith('.csv') or 
            part.get('filename').endswith('.json')
        )
    ]
    
    attachments = []
    for part in attachment_parts:
        filename = part.get('filename')
        
        # Check if filename matches our target list
        if is_target_attachment(filename):
            attachment_id = part.get('body', {}).get('attachmentId')
            
            # Get attachment data
            attachment = service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            # Decode attachment data
            file_data = base64.urlsafe_b64decode(attachment.get('data'))
            
            attachments.append({
                'filename': filename,
                'data': file_data,
                'mime_type': part.get('mimeType')
            })
    
    return attachments

def is_target_attachment(filename):
    """Check if the filename is in our target list."""
    target_filenames = [
        'daily_metrics.csv',
        'user_data.json',
        'transaction_log.csv'
        # Add more target filenames as needed
    ]
    
    return filename in target_filenames
```

### 3. S3 Integration

```python
import boto3
from datetime import datetime

def upload_to_s3(file_data, filename, bucket_name):
    """Upload file to S3 bucket with metadata."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    
    # Prepare metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'content-type': 'text/csv' if filename.endswith('.csv') else 'application/json',
        'size': str(len(file_data))
    }
    
    # Upload to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"attachments/{filename}",
        Body=file_data,
        ContentType=metadata['content-type'],
        Metadata=metadata
    )
    
    # Get the S3 URL
    location = f"s3://{bucket_name}/attachments/{filename}"
    
    print(f"Uploaded {filename} to S3 with metadata: {metadata}")
    return location, metadata
```

### 4. API Implementation with FastAPI

```python
from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import io
import base64

app = FastAPI(title="Email Attachment Processor API")

# For simplicity in POC, we're assuming auth is handled elsewhere
# In a real app, you would integrate proper OAuth flow
def get_credentials():
    # This would be replaced with actual OAuth flow
    # For POC, we could load from env vars or config file
    return Credentials.from_authorized_user_info(
        {
            "token": "YOUR_ACCESS_TOKEN",
            "refresh_token": "YOUR_REFRESH_TOKEN",
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )

class UploadResponse(BaseModel):
    success: bool
    filename: str
    s3_location: str
    metadata: dict

# Phase 1: Gmail API Endpoints

@app.get("/api/emails")
def list_emails(credentials: Credentials = Depends(get_credentials)):
    """List emails with CSV or JSON attachments."""
    service = build('gmail', 'v1', credentials=credentials)
    
    # Query for emails with attachments
    results = service.users().messages().list(
        userId='me',
        q='has:attachment filename:(*.csv OR *.json)'
    ).execute()
    
    messages = results.get('messages', [])
    
    # Get more details for each message
    emails_with_attachments = []
    for message in messages:
        details = service.users().messages().get(
            userId='me',
            id=message['id']
        ).execute()
        
        # Extract subject
        headers = details.get('payload', {}).get('headers', [])
        subject = next(
            (header['value'] for header in headers if header['name'] == 'Subject'),
            'No Subject'
        )
        
        # Extract attachment info
        has_target_attachments = False
        parts = details.get('payload', {}).get('parts', [])
        for part in parts:
            if part.get('filename') and is_target_attachment(part.get('filename')):
                has_target_attachments = True
                break
        
        emails_with_attachments.append({
            'id': message['id'],
            'subject': subject,
            'has_target_attachments': has_target_attachments
        })
    
    return emails_with_attachments

@app.get("/api/emails/{message_id}/attachments")
def list_attachments(message_id: str, credentials: Credentials = Depends(get_credentials)):
    """List attachments for a specific email."""
    service = build('gmail', 'v1', credentials=credentials)
    
    # Get message details
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Email not found: {str(e)}")
    
    # Extract attachment info
    attachments = []
    parts = message.get('payload', {}).get('parts', [])
    
    for part in parts:
        if part.get('filename') and part.get('body', {}).get('attachmentId'):
            attachments.append({
                'id': part['body']['attachmentId'],
                'filename': part['filename'],
                'mime_type': part['mimeType'],
                'size': part['body'].get('size', 0),
                'is_target_file': is_target_attachment(part['filename'])
            })
    
    return attachments

@app.get("/api/emails/{message_id}/attachments/{attachment_id}")
def download_attachment(
    message_id: str, 
    attachment_id: str, 
    credentials: Credentials = Depends(get_credentials)
):
    """Download a specific attachment (Phase 1 testing)."""
    service = build('gmail', 'v1', credentials=credentials)
    
    # Get message details to find attachment metadata
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Email not found: {str(e)}")
    
    # Find attachment info
    parts = message.get('payload', {}).get('parts', [])
    attachment_info = None
    for part in parts:
        if part.get('body', {}).get('attachmentId') == attachment_id:
            attachment_info = part
            break
    
    if not attachment_info:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Get attachment data
    try:
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Attachment data not found: {str(e)}")
    
    # Decode attachment data
    file_data = base64.urlsafe_b64decode(attachment.get('data', ''))
    
    # Set up streaming response
    filename = attachment_info.get('filename', 'attachment')
    mime_type = attachment_info.get('mimeType', 'application/octet-stream')
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=mime_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# Phase 2: S3 Integration Endpoints

@app.post("/api/emails/{message_id}/attachments/{attachment_id}/upload", response_model=UploadResponse)
def upload_attachment(
    message_id: str, 
    attachment_id: str,
    credentials: Credentials = Depends(get_credentials)
):
    """Upload a specific attachment to S3 (Phase 2 testing)."""
    service = build('gmail', 'v1', credentials=credentials)
    
    # Get message details
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Email not found: {str(e)}")
    
    # Find attachment info
    parts = message.get('payload', {}).get('parts', [])
    attachment_info = None
    for part in parts:
        if part.get('body', {}).get('attachmentId') == attachment_id:
            attachment_info = part
            break
    
    if not attachment_info:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Get attachment data
    try:
        attachment = service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Attachment data not found: {str(e)}")
    
    # Decode attachment data
    file_data = base64.urlsafe_b64decode(attachment.get('data', ''))
    filename = attachment_info.get('filename', 'attachment')
    
    # Upload to S3
    bucket_name = "your-s3-bucket-name"  # This would be configured via env vars
    try:
        s3_location, metadata = upload_to_s3(file_data, filename, bucket_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
    
    return UploadResponse(
        success=True,
        filename=filename,
        s3_location=s3_location,
        metadata=metadata
    )

# Future endpoint for integrated functionality (Phase 3)
@app.post("/api/process-attachments")
def process_all_attachments():
    """Process all matching emails and attachments (Future implementation)."""
    # This endpoint will be implemented in Phase 3
    # Will combine email fetching, attachment processing, and S3 upload
    return {"status": "Not implemented yet"}

def is_target_attachment(filename):
    """Check if the filename is in our target list."""
    target_filenames = [
        'daily_metrics.csv',
        'user_data.json',
        'transaction_log.csv'
        # Add more target filenames as needed
    ]
    
    return filename in target_filenames
```
```

## API Endpoints

The backend will expose the following API endpoints:

```
// Phase 1: Download attachment testing
GET /api/emails
- Returns a list of emails with attachments matching criteria

GET /api/emails/:messageId/attachments
- Returns list of attachments for a specific email

GET /api/emails/:messageId/attachments/:attachmentId
- Downloads a specific attachment

// Phase 2: S3 integration
POST /api/emails/:messageId/attachments/:attachmentId/upload
- Uploads a specific attachment to S3 bucket

// Combined functionality (for future integration)
POST /api/process-attachments
- Process all matching emails, extract attachments and upload to S3
- Returns statistics about processed attachments
```

## Implementation Plan

### Phase 1: API Development & Gmail Integration
- Set up Gmail API authentication
- Create API endpoints for email and attachment retrieval
- Implement email filtering and attachment extraction
- Test downloading attachments locally

### Phase 2: S3 Integration
- Configure S3 bucket and upload functionality
- Create API endpoint for S3 uploads
- Test direct upload from Gmail to S3
- Implement metadata tracking

### Phase 3: Integration (Future)
- Connect with existing frontend
- Implement automated scheduling
- Add error handling and retry logic
- Create logging and monitoring system

## Security Considerations (Future Improvements)

While not required for the initial POC, these security improvements should be implemented for production:

1. **Encryption**:
   - Implement server-side encryption for S3 bucket
   - Enable SSL/TLS for all data transfers

2. **Authentication & Authorization**:
   - Implement robust OAuth scope limitations
   - Use IAM roles with least privilege for S3 access
   - Implement API authentication

3. **Data Protection**:
   - Sanitize filenames before storage
   - Implement virus scanning for attachments
   - Set up bucket policies to prevent public access

4. **Monitoring & Auditing**:
   - Implement CloudTrail for S3 activity monitoring
   - Set up alerts for unusual access patterns
   - Create audit logs for all processing activities

## Testing Strategy

### Phase 1: Gmail API Testing
1. Test authentication with Gmail API
2. Test listing emails with CSV/JSON attachments
3. Test retrieving attachment metadata
4. Test downloading specific attachments
5. Validate the file integrity of downloaded attachments

#### Sample Test Cases
```python
# Example test for listing emails with attachments
def test_list_emails(test_client):
    response = test_client.get("/api/emails")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # More assertions...

# Example test for downloading attachments
def test_download_attachment(test_client):
    message_id = "test_message_id"
    attachment_id = "test_attachment_id"
    
    response = test_client.get(f"/api/emails/{message_id}/attachments/{attachment_id}")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    assert "attachment" in response.headers["content-disposition"]
    # Validate file content...
```

### Phase 2: S3 Integration Testing
1. Test S3 bucket configuration and credentials
2. Test uploading files to S3
3. Test retrieving metadata from S3
4. Test the combined Gmail-to-S3 workflow

#### Sample Test Cases
```python
# Example test for S3 upload
def test_upload_to_s3(test_client):
    message_id = "test_message_id"
    attachment_id = "test_attachment_id"
    
    response = test_client.post(f"/api/emails/{message_id}/attachments/{attachment_id}/upload")
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert "s3_location" in result
    assert "metadata" in result
    # Verify S3 object existence...
```

## Conclusions

This proof of concept provides a structured API-first approach for processing email attachments and storing them in S3 using Python FastAPI. The implementation is divided into two key phases:

1. **Phase 1**: Building and testing the Gmail API integration with endpoints for listing emails and downloading attachments locally
2. **Phase 2**: Adding S3 integration to upload the attachments directly to cloud storage

By focusing solely on the API development first, this approach allows for thorough testing of each component independently before integration with the existing frontend. The separation of Gmail API functionality and S3 upload functionality makes the system modular and easier to maintain.

The FastAPI framework provides several advantages for this implementation:
- Type validation with Pydantic models
- Automatic OpenAPI documentation
- Asynchronous request handling
- Easy testing with pytest and the FastAPI test client

The phased implementation also provides clear checkpoints to validate functionality before proceeding to the next stage. This allows for a methodical development process where each component can be thoroughly tested before moving on.

The design allows for future integration with the existing frontend and enhancements in security, automation, and reliability as the tool matures. The modular approach also makes it easier to add features like:
- Scheduled email processing
- Additional file format support
- Enhanced metadata extraction
- Security hardening

With this proof of concept, you'll have a solid foundation for building the email attachment processing tool that fits seamlessly into your existing workflow while maintaining flexibility for future enhancements.