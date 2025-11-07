from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserUpdate, UserResponse, ZendeskSettings, OpenAISettings
from app.auth import get_current_active_user
from app.services.zendesk_service import ZendeskService
from app.services.openai_service import OpenAIService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", response_model=UserResponse)
def get_settings(current_user: User = Depends(get_current_active_user)):
    """
    Get current user settings
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User settings (without sensitive data)
    """
    return current_user


@router.put("/", response_model=UserResponse)
def update_settings(
    settings: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user settings
    
    Args:
        settings: Settings to update
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user settings
    """
    # Update fields if provided
    if settings.zendesk_subdomain is not None:
        current_user.zendesk_subdomain = settings.zendesk_subdomain
    
    if settings.zendesk_email is not None:
        current_user.zendesk_email = settings.zendesk_email
    
    if settings.zendesk_api_token is not None:
        current_user.zendesk_api_token = settings.zendesk_api_token
    
    if settings.openai_api_key is not None:
        current_user.openai_api_key = settings.openai_api_key
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/zendesk/test")
def test_zendesk_connection(
    settings: ZendeskSettings,
    current_user: User = Depends(get_current_active_user)
):
    """
    Test Zendesk API connection
    
    Args:
        settings: Zendesk credentials to test
        current_user: Current authenticated user
        
    Returns:
        Connection test result
    """
    zendesk = ZendeskService(
        subdomain=settings.subdomain,
        email=settings.email,
        api_token=settings.api_token
    )
    
    is_connected = zendesk.test_connection()
    
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect to Zendesk. Please check your credentials."
        )
    
    return {
        "success": True,
        "message": "Successfully connected to Zendesk"
    }


@router.post("/openai/test")
def test_openai_connection(
    settings: OpenAISettings,
    current_user: User = Depends(get_current_active_user)
):
    """
    Test OpenAI API connection
    
    Args:
        settings: OpenAI credentials to test
        current_user: Current authenticated user
        
    Returns:
        Connection test result
    """
    openai = OpenAIService(api_key=settings.api_key)
    
    is_connected = openai.test_connection()
    
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect to OpenAI. Please check your API key."
        )
    
    return {
        "success": True,
        "message": "Successfully connected to OpenAI"
    }


@router.get("/integration-status")
def get_integration_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get status of integrations
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Integration status
    """
    return {
        "zendesk_configured": bool(
            current_user.zendesk_subdomain and 
            current_user.zendesk_email and 
            current_user.zendesk_api_token
        ),
        "openai_configured": bool(current_user.openai_api_key)
    }
