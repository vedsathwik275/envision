# Email Attachment Processing Tool - Todo List

## Project Setup
- [x] Create project directory structure
- [x] Initialize FastAPI application
- [x] Create requirements.txt with dependencies:
  - fastapi
  - uvicorn
  - google-auth
  - google-api-python-client
  - boto3
  - python-dotenv
  - pytest
  - httpx (for testing)
- [x] Configure environment variables for credentials

## Phase 1: API Development & Gmail Integration
- [ ] Set up Gmail API authentication
  - [ ] Configure OAuth 2.0 credentials
  - [ ] Implement credential management
  - [ ] Create secure storage for tokens
- [ ] Implement email listing endpoint
  - [ ] Create `/api/emails` GET endpoint
  - [ ] Add filtering for CSV/JSON attachments
  - [ ] Extract email subjects and metadata
- [ ] Implement attachment listing endpoint
  - [ ] Create `/api/emails/{message_id}/attachments` GET endpoint
  - [ ] Extract attachment metadata
  - [ ] Filter for target attachments
- [ ] Implement attachment download endpoint
  - [ ] Create `/api/emails/{message_id}/attachments/{attachment_id}` GET endpoint
  - [ ] Add proper error handling for missing emails/attachments
  - [ ] Set up streaming response for downloads
- [ ] Create target attachment identification function
  - [ ] Define list of target filenames
  - [ ] Implement filename matching logic

## Phase 1: Testing
- [ ] Write tests for Gmail API authentication
- [ ] Write tests for email listing functionality
- [ ] Write tests for attachment listing functionality
- [ ] Write tests for attachment download functionality
- [ ] Test file integrity of downloaded attachments

## Phase 2: S3 Integration
- [ ] Configure S3 bucket
  - [ ] Create bucket with appropriate permissions
  - [ ] Set up IAM roles and policies
- [ ] Implement S3 upload functionality
  - [ ] Create upload_to_s3 function
  - [ ] Add metadata generation
  - [ ] Implement error handling for upload failures
- [ ] Create S3 upload endpoint
  - [ ] Implement `/api/emails/{message_id}/attachments/{attachment_id}/upload` POST endpoint
  - [ ] Add proper response model with UploadResponse
  - [ ] Include metadata in response

## Phase 2: Testing
- [ ] Test S3 bucket configuration and credentials
- [ ] Test file uploads to S3
- [ ] Test metadata storage and retrieval
- [ ] Test combined Gmail-to-S3 workflow
- [ ] Verify file integrity in S3

## Phase 3: Integration & Future Improvements
- [ ] Implement combined processing endpoint
  - [ ] Create `/api/process-attachments` POST endpoint
  - [ ] Add batch processing functionality
  - [ ] Include statistics in response
- [ ] Connect with existing frontend
- [ ] Implement automated scheduling
- [ ] Add error handling and retry logic
- [ ] Create logging and monitoring system

## Security Improvements (For Production)
- [ ] Encryption
  - [ ] Implement server-side encryption for S3 bucket
  - [ ] Enable SSL/TLS for all data transfers
- [ ] Authentication & Authorization
  - [ ] Implement robust OAuth scope limitations
  - [ ] Use IAM roles with least privilege for S3 access
  - [ ] Implement API authentication
- [ ] Data Protection
  - [ ] Sanitize filenames before storage
  - [ ] Implement virus scanning for attachments
  - [ ] Set up bucket policies to prevent public access
- [ ] Monitoring & Auditing
  - [ ] Implement CloudTrail for S3 activity monitoring
  - [ ] Set up alerts for unusual access patterns
  - [ ] Create audit logs for all processing activities

## Documentation
- [ ] Create API documentation
- [x] Write deployment instructions
- [x] Document configuration options
- [ ] Create user guide for frontend integration
