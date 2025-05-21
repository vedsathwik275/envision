# Email Attachment Processing Tool

A FastAPI-based tool that extracts specific CSV and JSON attachments from Gmail and uploads them to Amazon S3.

## Features

- Access emails using Gmail API via OAuth2.
- Identify and extract specific CSV/JSON attachments by filename patterns and subject lines.
- Download attachments with correct filenames and MIME types.
- Upload attachments directly to Amazon S3 with associated metadata.
- API-first design for integration with existing systems.

## Project Structure

```
envision_product/tools/gmail_s3/
├── app/
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Application configuration
│   ├── routers/            # API route definitions (auth.py, emails.py)
│   ├── models/             # Pydantic models (schemas.py)
│   ├── services/           # Business logic (auth_service.py, gmail_service.py, s3_service.py)
│   └── utils/              # Utility functions (attachment_utils.py)
├── tests/                  # Test modules (to be implemented)
├── tokens/                 # Stores OAuth tokens (auto-created, add to .gitignore)
├── .env.example            # Example environment variables
├── .env                    # Local environment variables (created from .env.example)
├── API_DOCS.md             # Detailed API documentation
└── README.md               # This file
```

## Setup Instructions

1.  **Clone the repository** (if you haven't already).
2.  **Navigate to the tool directory**:
    ```bash
    cd path/to/envision_product/tools/gmail_s3
    ```
3.  **Install dependencies** (ensure you have Python 3.8+ and pip):
    ```bash
    pip install -r requirements.txt 
    ```
    *(Note: `requirements.txt` should include `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `google-api-python-client`, `google-auth-oauthlib`, `boto3`)*

4.  **Set up environment variables**:
    Copy `.env.example` to `.env` and fill in your credentials:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your specific details.

5.  **Configure Gmail API**:
    - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
    - Enable the Gmail API for your project.
    - Create OAuth 2.0 credentials (for a "Web application").
    - Add the redirect URI to your OAuth 2.0 client ID settings. If running locally on port 8002, this will be: `http://localhost:8002/auth/callback` (Update this if your port changes).
    - Copy the "Client ID" and "Client Secret" to your `.env` file (`GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET`).

6.  **Configure AWS S3**:
    - Create an S3 bucket in your desired AWS region.
    - Create an IAM user with programmatic access and permissions to read/write to this bucket (e.g., `AmazonS3FullAccess` for simplicity, or a more restrictive policy).
    - Copy the "Access key ID" and "Secret access key" to your `.env` file (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).
    - Set `S3_BUCKET_NAME` and `S3_REGION` in your `.env` file.

## Running the Application

Run the application using Uvicorn (ensure you are in the `envision_product/tools/gmail_s3` directory):

```bash
uvicorn app.main:app --reload --port 8002
```

- The API will be available at `http://localhost:8002`.
- Interactive API documentation (Swagger UI) will be at `http://localhost:8002/docs`.
- Alternative API documentation (ReDoc) will be at `http://localhost:8002/redoc`.

## API Endpoints Summary

Full details can be found in [API_DOCS.md](./API_DOCS.md).

- **Authentication (`/auth`)**
    - `GET /auth/login`: Initiate Gmail OAuth2 login.
    - `GET /auth/callback`: Handle OAuth2 callback.
    - `GET /auth/status`: Check authentication status.
    - `POST /auth/logout`: Logout and clear session.

- **Emails & Attachments (`/api/emails`)**
    - `GET /api/emails`: List emails with filterable attachments.
    - `GET /api/emails/{message_id}/attachments`: List attachments for a specific email.
    - `GET /api/emails/{message_id}/attachments/{attachment_id}`: Download a specific attachment.
    - `POST /api/emails/{message_id}/attachments/{attachment_id}/upload`: Upload a specific attachment to S3.

## Testing

(Test setup and commands to be added here once tests are implemented.)

Run tests with:
```bash
pytest
```

## License

[MIT](LICENSE) *(Assuming MIT, add a LICENSE file if one doesn't exist)* 