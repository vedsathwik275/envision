# API Documentation: Email Attachment Processing Tool

This document provides detailed information about the API endpoints for the Email Attachment Processing Tool. This tool allows users to authenticate with Gmail, list emails and attachments, download attachments, and upload attachments directly to an AWS S3 bucket.

## Base URL

All API endpoints are relative to the base URL where the application is running (e.g., `http://localhost:8002` if running locally on port 8002).

## Authentication

Authentication is handled via OAuth2 with Google. Users must first authenticate to access most email and attachment-related endpoints. The authentication flow involves redirecting the user to a Google consent screen and then handling a callback.

--- 

## Authentication Endpoints

These endpoints manage the OAuth2 authentication flow with Gmail.

### 1. `GET /auth/login`

-   **Description**: Initiates the OAuth2 authentication flow by providing a Google authorization URL.
-   **Request Body**: None.
-   **Responses**:
    -   `200 OK`: Returns the authorization URL and a state parameter.
        ```json
        {
          "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
          "state": "UNIQUE_STATE_STRING"
        }
        ```
    -   `500 Internal Server Error`: If there's an issue generating the URL.

### 2. `GET /auth/callback`

-   **Description**: Handles the callback from Google after the user has authorized the application. It exchanges the received authorization code for an access token and stores the credentials.
-   **Query Parameters**:
    -   `code: str` (required): The authorization code provided by Google.
    -   `state: str` (required): The state parameter returned from the `/auth/login` step (for CSRF protection).
-   **Responses**:
    -   `307 Temporary Redirect`: On successful authentication, redirects the user to the application's root (`/`).
    -   `401 Unauthorized`: If credentials are invalid.
    -   `500 Internal Server Error`: If there's an issue during token exchange or credential validation.

### 3. `GET /auth/status`

-   **Description**: Checks the current authentication status by verifying if valid credentials exist and are working.
-   **Request Body**: None.
-   **Responses**:
    -   `200 OK`:
        ```json
        // If authenticated and token is valid
        { "authenticated": true }
        
        // If not authenticated or token is invalid
        { "authenticated": false }
        ```

### 4. `POST /auth/logout`

-   **Description**: Logs the user out by removing the stored OAuth credentials from the `tokens/token.json` file.
-   **Request Body**: None.
-   **Responses**:
    -   `200 OK`:
        ```json
        {
          "success": true,
          "message": "Logged out successfully" 
        }
        // Or if already logged out:
        // { "success": true, "message": "Already logged out" }
        ```
    -   `500 Internal Server Error`: If an error occurs during file deletion.

--- 

## Email and Attachment Endpoints

These endpoints require prior authentication and allow interaction with Gmail messages and attachments, including uploading to S3.

### 1. `GET /api/emails`

-   **Description**: Lists emails from the authenticated user's Gmail account that contain supported attachments (CSV or JSON) and optionally match subject patterns.
-   **Query Parameters**:
    -   `max_results: Optional[int]` (default: `20`): The maximum number of emails to return.
    -   `filter_by_subject: Optional[bool]` (default: `True`): If `True`, filters emails based on subject patterns defined in the application configuration (e.g., `TARGET_SUBJECTS` in `.env`).
-   **Response `200 OK`**: A list of `EmailInfo` objects.
    ```json
    [
      {
        "id": "EMAIL_MESSAGE_ID_1",
        "subject": "Order Volume Report Q2",
        "from_email": "reports@example.com", // Alias for 'from'
        "date": "Tue, 21 May 2024 10:00:00 +0000",
        "has_target_attachments": true,
        "is_target_subject": true
      },
      // ... more emails
    ]
    ```
    *(Note: `from_email` is an alias for the `from` field in the Pydantic model to avoid conflict with Python's `from` keyword.)*
-   **Responses `401 Unauthorized`, `500 Internal Server Error`**.

### 2. `GET /api/emails/{message_id}/attachments`

-   **Description**: Lists all supported attachments (CSV or JSON) for a specific email message.
-   **Path Parameters**:
    -   `message_id: str` (required): The ID of the email message.
-   **Response `200 OK`**: A list of `AttachmentInfo` objects.
    ```json
    [
      {
        "id": "ATTACHMENT_ID_1",
        "filename": "orders_q2.csv",
        "mime_type": "text/csv",
        "size": 12345,
        "is_target_file": true
      },
      // ... more attachments
    ]
    ```
-   **Responses `401 Unauthorized`, `500 Internal Server Error`**.

### 3. `GET /api/emails/{message_id}/attachments/{attachment_id}`

-   **Description**: Downloads a specific attachment from an email.
-   **Path Parameters**:
    -   `message_id: str` (required): The ID of the email message.
    -   `attachment_id: str` (required): The ID of the attachment.
-   **Query Parameters (optional but recommended for accuracy)**:
    -   `expected_filename: Optional[str]`: The filename the client expects (useful if the filename from Gmail is ambiguous or needs correction). The service will use this to ensure the downloaded file has the correct name and extension based on the `expected_mime_type`.
    -   `expected_mime_type: Optional[str]`: The MIME type the client expects (e.g., `text/csv`, `application/json`, or shorthands like `csv`, `json`). This helps ensure the correct `Content-Type` header and file extension.
-   **Response `200 OK`**: The raw attachment data as a file stream. The `Content-Disposition` header will suggest the filename, and `Content-Type` will be set according to the (potentially client-hinted and normalized) MIME type.
-   **Responses `401 Unauthorized`, `404 Not Found` (if attachment/message not found), `500 Internal Server Error`**.

### 4. `POST /api/emails/{message_id}/attachments/{attachment_id}/upload`

-   **Description**: Downloads a specific attachment from Gmail and uploads it directly to the configured AWS S3 bucket.
-   **Path Parameters**:
    -   `message_id: str` (required): The ID of the email message.
    -   `attachment_id: str` (required): The ID of the attachment.
-   **Query Parameters (optional but recommended for accuracy)**:
    -   `expected_filename: Optional[str]`: Similar to the download endpoint, helps ensure the correct filename is used for the S3 object key and metadata.
    -   `expected_mime_type: Optional[str]`: Similar to the download endpoint, helps ensure the correct `ContentType` is set for the S3 object.
-   **Response `200 OK`**: An `UploadResponse` object detailing the result of the S3 upload.
    ```json
    {
      "success": true,
      "filename": "orders_q2.csv", // Original filename of the attachment
      "s3_location": "https://your-s3-bucket.s3.your-region.amazonaws.com/attachments/EMAIL_MESSAGE_ID_1/orders_q2.csv",
      "metadata": {
        "object_key": "attachments/EMAIL_MESSAGE_ID_1/orders_q2.csv",
        "content_type": "text/csv",
        "size_bytes": "12345",
        "original_attachment_id": "ATTACHMENT_ID_1",
        "email_message_id": "EMAIL_MESSAGE_ID_1"
      }
    }
    ```
-   **Responses `401 Unauthorized`, `404 Not Found` (if attachment/message not found), `500 Internal Server Error` (for Gmail issues, S3 credential/upload issues, or other internal errors)**.

--- 

## Pydantic Models Used in Responses

*(Brief mention or link to where schemas are defined could go here if needed, but they are implicitly shown in the example responses above.)*

-   **EmailInfo**: Contains metadata about an email message.
-   **AttachmentInfo**: Contains metadata about an email attachment.
-   **UploadResponse**: Contains information about the result of an S3 upload, including success status, original filename, S3 location, and other metadata.

--- 