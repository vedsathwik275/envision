"""
Service for interacting with AWS S3.

This module provides functions for uploading files to an S3 bucket.
"""
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from typing import Optional, Dict
import io

from ..config import settings


class S3Service:
    """Service for uploading files to AWS S3."""

    def __init__(self):
        """
        Initialize the S3 service with credentials and configuration
        from application settings.
        """
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.s3_bucket_name = settings.s3_bucket_name
        self.s3_region = settings.s3_region

        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.s3_bucket_name, self.s3_region]):
            raise ValueError(
                "AWS S3 credentials and bucket information are not fully configured. "
                "Please check your environment variables: "
                "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, S3_REGION."
            )

        session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.s3_region
        )
        self.s3_client = session.client("s3")
        self.s3_resource = session.resource("s3") # For simpler object operations if needed

    def upload_to_s3(self, file_data: bytes, filename: str, content_type: Optional[str] = None) -> Dict[str, str]:
        """
        Upload file data to the configured S3 bucket.

        Args:
            file_data: The byte content of the file.
            filename: The desired filename in the S3 bucket (can include paths).
            content_type: Optional. The MIME type of the file. If None, S3 will attempt to guess.

        Returns:
            A dictionary containing the S3 object URL and the object key.
            Example: {"s3_url": "https://bucket.s3.region.amazonaws.com/key", "object_key": "key"}

        Raises:
            ValueError: If S3 bucket name is not configured.
            NoCredentialsError: If AWS credentials are not found.
            PartialCredentialsError: If AWS credentials are incomplete.
            ClientError: For other Boto3/AWS related errors during upload.
        """
        if not self.s3_bucket_name:
            raise ValueError("S3 bucket name is not configured.")

        try:
            file_obj = io.BytesIO(file_data)
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.s3_bucket_name,
                Key=filename,
                ExtraArgs=extra_args
            )
            
            # Construct the S3 object URL
            # Note: For virtual-hosted style URLs, ensure bucket name complies with DNS naming rules.
            # For path-style URLs (less common for new buckets):
            # s3_url = f"https://s3.{self.s3_region}.amazonaws.com/{self.s3_bucket_name}/{filename}"
            # For virtual-hosted style (more common):
            s3_url = f"https://{self.s3_bucket_name}.s3.{self.s3_region}.amazonaws.com/{filename}"
            
            # Ensure the bucket exists and is accessible (optional check, upload_fileobj implies it)
            # self.s3_client.head_bucket(Bucket=self.s3_bucket_name) # Raises ClientError if not found/accessible

            return {"s3_url": s3_url, "object_key": filename}

        except (NoCredentialsError, PartialCredentialsError) as e:
            # Log the specific credential error
            print(f"S3 Upload Error: AWS credentials not configured or incomplete. {e}")
            raise NoCredentialsError("AWS credentials not configured or incomplete.") from e
        except ClientError as e:
            # Log the specific Boto3 client error
            error_code = e.response.get('Error', {}).get('Code')
            error_message = e.response.get('Error', {}).get('Message')
            print(f"S3 Upload Error: ClientError - Code: {error_code}, Message: {error_message}. {e}")
            raise ClientError(f"S3 upload failed: {error_message}", e.response) from e
        except Exception as e:
            # Catch any other unexpected errors
            print(f"S3 Upload Error: An unexpected error occurred. {e}")
            raise RuntimeError(f"An unexpected error occurred during S3 upload: {str(e)}") from e 