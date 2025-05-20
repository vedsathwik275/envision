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
- [x] Set up Gmail API authentication
  - [x] Configure OAuth 2.0 credentials
  - [x] Implement credential management
  - [x] Create secure storage for tokens
- [x] Implement email listing endpoint
  - [x] Create `/api/emails` GET endpoint
  - [x] Add filtering for CSV/JSON attachments
  - [x] Extract email subjects and metadata
- [x] Implement attachment listing endpoint
  - [x] Create `/api/emails/{message_id}/attachments` GET endpoint
  - [x] Extract attachment metadata
  - [x] Filter for target attachments
- [x] Implement attachment download endpoint
  - [x] Create `/api/emails/{message_id}/attachments/{attachment_id}` GET endpoint
  - [x] Add proper error handling for missing emails/attachments
  - [x] Set up streaming response for downloads
- [x] Create target attachment identification function
  - [x] Define list of target filenames
  - [x] Implement filename matching logic

## Phase 1: Testing
- [ ] Write tests for Gmail API authentication
- [ ] Write tests for email listing functionality
- [ ] Write tests for attachment listing functionality
- [ ] Write tests for attachment download functionality
- [ ] Test file integrity of downloaded attachments

## Phase 2: S3 Integration
- [x] Configure S3 bucket
  - [x] Create bucket with appropriate permissions
  - [x] Set up IAM roles and policies
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
- [x] Create API documentation
- [x] Write deployment instructions
- [x] Document configuration options
- [ ] Create user guide for frontend integration

## Next Steps
- [ ] Add unit tests for utility functions
- [ ] Create test fixtures for Gmail API interactions
- [ ] Implement S3 upload functionality
- [ ] Create combined processing endpoint
