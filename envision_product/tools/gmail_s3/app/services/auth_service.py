"""
Authentication service for managing OAuth2 credentials.

This module provides functions for creating, refreshing, and validating
OAuth2 credentials for the Gmail API.
"""
from typing import Dict, Optional
import os
import json
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import settings


class AuthService:
    """Service for managing OAuth2 authentication."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.client_id = settings.gmail_client_id
        self.client_secret = settings.gmail_client_secret
        self.redirect_uri = settings.gmail_redirect_uri
        self.token_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tokens')
        
        # Create tokens directory if it doesn't exist
        os.makedirs(self.token_dir, exist_ok=True)
        
        # Set up OAuth2 scopes
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def get_authorization_url(self) -> Dict[str, str]:
        """
        Get the authorization URL for OAuth2 flow.
        
        Returns:
            Dictionary with authorization URL and state
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return {
            "authorization_url": authorization_url,
            "state": state
        }
    
    def exchange_code(self, code: str, state: str) -> Credentials:
        """
        Exchange authorization code for credentials.
        
        Args:
            code: Authorization code from OAuth2 flow
            state: State from OAuth2 flow
            
        Returns:
            OAuth2 credentials
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            state=state
        )
        
        flow.redirect_uri = self.redirect_uri
        
        # Exchange code for credentials
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Save credentials
        self._save_credentials(credentials)
        
        return credentials
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get stored credentials if they exist and are valid.
        
        Returns:
            OAuth2 credentials or None if not available
        """
        token_path = os.path.join(self.token_dir, 'token.json')
        
        if not os.path.exists(token_path):
            return None
        
        try:
            with open(token_path, 'r') as token_file:
                token_data = json.load(token_file)
            
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=token_data.get('scopes')
            )
            
            # Check if token is expired and refresh if needed
            if credentials.expired:
                credentials.refresh(Request())
                self._save_credentials(credentials)
            
            return credentials
            
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def _save_credentials(self, credentials: Credentials) -> None:
        """
        Save credentials to a file.
        
        Args:
            credentials: OAuth2 credentials to save
        """
        token_path = os.path.join(self.token_dir, 'token.json')
        
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        with open(token_path, 'w') as token_file:
            json.dump(token_data, token_file)
    
    def validate_credentials(self, credentials: Credentials) -> bool:
        """
        Validate credentials by making a test API call.
        
        Args:
            credentials: OAuth2 credentials to validate
            
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            service = build('gmail', 'v1', credentials=credentials)
            
            # Make a test API call
            service.users().getProfile(userId='me').execute()
            
            return True
            
        except HttpError:
            return False 