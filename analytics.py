from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import AnalyticsResponse
from app.auth import get_current_active_user
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsResponse)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard analytics
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Complete analytics data for dashboard
    """
    analytics = AnalyticsService(current_user, db)
    return analytics.get_full_analytics()


@router.get("/trends")
def get_trend_data(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get trend data for charts
    
    Args:
        days: Number of days to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Daily trend data
    """
    analytics = AnalyticsService(current_user, db)
    return analytics.get_trend_data(days=days)


@router.get("/categories")
def get_category_breakdown(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get category distribution
    
    Args:
        days: Number of days to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Category distribution
    """
    analytics = AnalyticsService(current_user, db)
    return analytics.get_category_distribution(days=days)


@router.get("/sentiments")
def get_sentiment_breakdown(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get sentiment distribution
    
    Args:
        days: Number of days to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Sentiment distribution
    """
    analytics = AnalyticsService(current_user, db)
    return analytics.get_sentiment_distribution(days=days)
