# Gmail to S3 Integration - Todo List

## Overview
This document outlines the tasks required to integrate the Gmail to S3 API with the Envision Neural POC frontend. The integration will allow users to fetch CSV attachments from Gmail and upload them to the Envision Neural backend.

## Implementation Plan

### Phase 1: Setup and Basic UI (Envision Neural Frontend)

- [x] **`script.js`**: Add `GMAIL_S3_API_BASE_URL` constant
- [x] **`index.html`**: Add "Fetch Attachment from Email" button to the file upload section
- [x] **`index.html`**: Add HTML structure for the email/attachment selection modal (initially hidden)
- [x] **`styles.css`**: Add basic styling for the new button and modal to match the existing UI
- [x] **Create `gmail_login.html`**:
  - [x] Add "Login with Gmail" button
  - [x] Add basic script to call the Gmail API's `/auth/login` endpoint and redirect
  - [x] Add placeholder message for post-authentication (e.g., "Login successful, please close this tab...")

### Phase 2: Gmail Authentication Flow

- [x] **`script.js` (Envision Neural):**
  - [x] Implement `checkGmailAuthStatus()` function
  - [x] Add event listener to "Fetch Attachment from Email" button:
    - [x] If not authenticated via `checkGmailAuthStatus()`, open `gmail_login.html` in a new tab
    - [x] If authenticated, call function to open email selection modal
  - [x] (Optional but Recommended) Add a "Logout from Gmail" button/mechanism and its handler

### Phase 3: Email/Attachment Selection Modal (Envision Neural Frontend)

- [x] **`script.js`**:
  - [x] Implement `openEmailSelectionModal()`: Shows modal, calls `listGmailEmails()`
  - [x] Implement `listGmailEmails()`:
    - [x] Fetches emails from `{GMAIL_S3_API_BASE_URL}/api/emails`
    - [x] Renders emails in the modal
    - [x] Adds click listeners to emails to call `listGmailAttachments()`
  - [x] Implement `listGmailAttachments(emailId)` (implemented as `selectEmail(email)`):
    - [x] Fetches attachments from `{GMAIL_S3_API_BASE_URL}/api/emails/{emailId}/attachments`
    - [x] Renders attachments in the modal
    - [x] Adds click listeners to attachments to select them and enable the "Fetch Selected Attachment" button
  - [x] Implement logic for "Fetch Selected Attachment" button within the modal (event listener)
- [x] **`styles.css`**:
  - [x] Add styles for email and attachment lists
  - [x] Add styles for selected items
  - [x] Ensure proper scrolling for long lists

### Phase 4: Fetching and Uploading to Neural Backend

- [x] **`script.js` (Handler for "Fetch Selected Attachment" button):**
  - [x] Get selected message ID and attachment details
  - [x] Download attachment data as a `Blob` from the Gmail API's download attachment endpoint
  - [x] Create a JavaScript `File` object from the `Blob` and attachment details
  - [x] Adapt or reuse existing file upload logic (`handleFileUpload`) to send this `File` object to `${NEURAL_API_BASE_URL}/files/upload`
  - [x] Implement UI feedback (close modal, show success/error on main page, optionally trigger preview)
  - [x] Ensure `loadUploadedFiles()` is called to refresh relevant lists

### Phase 5: Testing and Refinements

- [ ] Test the entire flow:
  - [ ] Unauthenticated -> click "Fetch..." -> new tab login -> close tab -> click "Fetch..." again -> modal
  - [ ] Authenticated -> click "Fetch..." -> modal
  - [ ] Email and attachment listing
  - [ ] Fetching attachment and its appearance in the Neural backend (e.g., via preview or lists)
- [ ] Test error handling at each step (API errors, no emails/attachments found, etc.)
- [ ] Refine UI/UX elements for clarity and consistency with the "Envision Neural" frontend
- [ ] Check CORS configurations on both backend APIs if testing across different local ports

### Phase 6: S3 Upload Feature Implementation

- [ ] **`index.html`**:
  - [ ] Add checkbox in email attachment modal for "Also upload to S3"
  - [ ] Add area to display S3 upload results (URL, object key)
- [ ] **`script.js`**:
  - [ ] Modify `handleFetchAttachment()` to check if S3 upload is requested
  - [ ] If S3 upload is requested, call the Gmail to S3 API's upload endpoint
  - [ ] Display S3 upload results to the user (URL, object key)
  - [ ] Handle errors and provide appropriate feedback
- [ ] **`styles.css`**:
  - [ ] Add styles for the S3 upload option and results display

## S3 Upload Implementation Plan

1. **UI Modifications**:
   - Add a checkbox labeled "Also upload to S3" to the email attachment modal
   - Add a collapsible section to display S3 upload results (initially hidden)
   - Style these new UI elements to match the existing design

2. **JavaScript Implementation**:
   - Add a variable to track whether S3 upload is requested
   - Update the `handleFetchAttachment()` function:
     ```javascript
     // After downloading the attachment as a blob
     if (s3UploadRequested) {
       try {
         // Call the S3 upload endpoint
         const s3Response = await fetch(
           `${GMAIL_S3_API_BASE_URL}/api/emails/${currentMessageId}/attachments/${attachmentId}/upload?expected_filename=${encodeURIComponent(filename)}&expected_mime_type=${encodeURIComponent(mimeType)}`,
           { method: 'POST' }
         );
         
         if (!s3Response.ok) {
           throw new Error('Failed to upload to S3');
         }
         
         const s3Data = await s3Response.json();
         
         // Display S3 upload results
         displayS3UploadResults(s3Data);
       } catch (error) {
         // Handle S3 upload errors
         showModalError(`S3 upload error: ${error.message}`);
       }
     }
     ```

3. **Helper Functions**:
   - Implement `displayS3UploadResults(data)` to show S3 location and metadata
   - Add toggle functionality for the S3 results section

4. **Error Handling**:
   - Ensure errors in S3 upload don't prevent Neural backend upload
   - Provide clear error messages specific to S3 upload issues
   - Log detailed error information to console for debugging

5. **Testing**:
   - Test with S3 upload enabled and disabled
   - Verify correct metadata is passed to the S3 upload endpoint
   - Check error handling when S3 upload fails but Neural upload succeeds

## Technical Notes

1. **API Endpoints**:
   - Envision Neural API: `http://localhost:8000/api`
   - Gmail to S3 API: `http://localhost:8002`

2. **Key Gmail to S3 API Endpoints**:
   - Auth Status: `GET /auth/status`
   - Login: `GET /auth/login`
   - Logout: `POST /auth/logout`
   - List Emails: `GET /api/emails`
   - List Attachments: `GET /api/emails/{messageId}/attachments`
   - Download Attachment: `GET /api/emails/{messageId}/attachments/{attachmentId}`
   - Upload to S3: `POST /api/emails/{messageId}/attachments/{attachmentId}/upload`

3. **File Handling**:
   - Only CSV files will be supported for this integration
   - The Gmail attachment will be downloaded as a Blob and converted to a File object
   - The File object will be uploaded to the Envision Neural backend as if it were selected via the file input
   - When S3 upload is requested, the attachment will also be uploaded to S3 via the Gmail to S3 API

## Implementation Details

The integration will keep the two APIs separate. The Envision Neural frontend will communicate with:
1. The Gmail to S3 API (`http://localhost:8002`) for Gmail authentication and email/attachment operations
2. The Envision Neural API (`http://localhost:8000/api`) for uploading the fetched attachment

The Gmail login will occur in a separate page (`gmail_login.html`), while the email/attachment selection will happen in a modal dialog within the main Envision Neural frontend.
