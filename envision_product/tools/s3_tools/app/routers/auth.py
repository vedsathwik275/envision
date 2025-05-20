"""
Router for authentication endpoints.

This module provides API endpoints for OAuth2 authentication with Gmail API.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthorizationResponse(BaseModel):
    """Model for authorization response."""
    
    authorization_url: str
    state: str


@router.get("/login", response_model=AuthorizationResponse)
async def login():
    """
    Start OAuth2 flow by getting authorization URL.
    
    Returns:
        Dictionary with authorization URL and state
    """
    auth_service = AuthService()
    
    try:
        auth_data = auth_service.get_authorization_url()
        return auth_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get authorization URL: {str(e)}"
        )


@router.get("/callback")
async def callback(code: str, state: str, request: Request):
    """
    Handle OAuth2 callback.
    
    Args:
        code: Authorization code from OAuth2 flow
        state: State from OAuth2 flow
        request: FastAPI request object
        
    Returns:
        Redirect to home page
    """
    auth_service = AuthService()
    
    try:
        # Exchange code for credentials
        credentials = auth_service.exchange_code(code, state)
        
        # Validate credentials
        if not auth_service.validate_credentials(credentials):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Redirect to home page
        return RedirectResponse(url="/")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to authenticate: {str(e)}"
        )


@router.get("/status")
async def status():
    """
    Check authentication status.
    
    Returns:
        Dictionary with authentication status
    """
    auth_service = AuthService()
    credentials = auth_service.get_credentials()
    
    if credentials:
        is_valid = auth_service.validate_credentials(credentials)
        return {"authenticated": is_valid}
    
    return {"authenticated": False}


@router.post("/logout")
async def logout():
    """
    Logout by removing stored credentials.
    
    Returns:
        Dictionary with logout status
    """
    import os
    
    auth_service = AuthService()
    token_path = os.path.join(auth_service.token_dir, 'token.json')
    
    if os.path.exists(token_path):
        try:
            os.remove(token_path)
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to logout: {str(e)}"
            )
    
    return {"success": True, "message": "Already logged out"} 