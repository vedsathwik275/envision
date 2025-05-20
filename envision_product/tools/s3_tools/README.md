# Email Attachment Processing Tool

A FastAPI-based tool that extracts specific CSV and JSON attachments from Gmail and uploads them to Amazon S3.

## Features

- Access emails using Gmail API
- Identify and extract specific CSV/JSON attachments by filename
- Upload attachments to Amazon S3 with metadata
- API-first design for integration with existing systems

## Project Structure

```
envision_product/tools/s3_tools/
├── app/
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Application configuration
│   ├── routers/            # API route definitions
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── tests/                  # Test modules
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp envision_product/tools/s3_tools/.env.example envision_product/tools/s3_tools/.env
   ```
4. Configure Gmail API:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API
   - Create OAuth 2.0 credentials
   - Add the redirect URI: `http://localhost:8000/auth/callback`
   - Copy the client ID and client secret to your `.env` file

5. Configure AWS S3:
   - Create an S3 bucket
   - Create an IAM user with permissions to access the bucket
   - Copy the access key ID and secret access key to your `.env` file

## Running the Application

Run the application with:

```
cd envision_product/tools/s3_tools
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` and the documentation at `http://localhost:8000/docs`.

## API Endpoints

- `GET /api/emails` - List emails with attachments
- `GET /api/emails/{message_id}/attachments` - List attachments for a specific email
- `GET /api/emails/{message_id}/attachments/{attachment_id}` - Download a specific attachment
- `POST /api/emails/{message_id}/attachments/{attachment_id}/upload` - Upload a specific attachment to S3
- `POST /api/process-attachments` - Process all matching emails and attachments (future implementation)

## Testing

Run tests with:

```
pytest
```

## License

[MIT](LICENSE) 