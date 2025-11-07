from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict

from app.models import Ticket, TicketAnalysis, User
from app.schemas import (
    DashboardStats, 
    CategoryDistribution, 
    SentimentDistribution,
    AnalyticsResponse
)


class AnalyticsService:
    """Service for calculating analytics and dashboard statistics"""
    
    def __init__(self, user: User, db: Session):
        self.user = user
        self.db = db
    
    def _get_date_range(self, days: int) -> datetime:
        """Get datetime for X days ago"""
        return datetime.utcnow() - timedelta(days=days)
    
    def get_dashboard_stats(self) -> DashboardStats:
        """
        Calculate overall dashboard statistics
        
        Returns:
            DashboardStats object with key metrics
        """
        # Date ranges
        today = self._get_date_range(0).replace(hour=0, minute=0, second=0)
        week_ago = self._get_date_range(7)
        month_ago = self._get_date_range(30)
        
        # Tickets count by period
        tickets_today = self.db.query(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= today
        ).count()
        
        tickets_this_week = self.db.query(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= week_ago
        ).count()
        
        tickets_this_month = self.db.query(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= month_ago
        ).count()
        
        # Average processing time
        avg_time = self.db.query(
            func.avg(TicketAnalysis.processing_time)
        ).join(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= month_ago
        ).scalar() or 0.0
        
        # Total costs
        cost_today = self.db.query(
            func.sum(TicketAnalysis.cost)
        ).join(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= today
        ).scalar() or 0.0
        
        cost_month = self.db.query(
            func.sum(TicketAnalysis.cost)
        ).join(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= month_ago
        ).scalar() or 0.0
        
        # Accuracy rate (placeholder - would need manual validation data)
        accuracy_rate = 91.7  # From documentation
        
        return DashboardStats(
            tickets_today=tickets_today,
            tickets_this_week=tickets_this_week,
            tickets_this_month=tickets_this_month,
            avg_processing_time=round(avg_time, 2),
            total_cost_today=round(cost_today, 4),
            total_cost_month=round(cost_month, 2),
            accuracy_rate=accuracy_rate
        )
    
    def get_category_distribution(self, days: int = 30) -> CategoryDistribution:
        """
        Get distribution of tickets by category
        
        Args:
            days: Number of days to look back
            
        Returns:
            CategoryDistribution object
        """
        date_threshold = self._get_date_range(days)
        
        # Query category counts
        categories = self.db.query(
            TicketAnalysis.category,
            func.count(TicketAnalysis.id).label("count")
        ).join(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= date_threshold
        ).group_by(TicketAnalysis.category).all()
        
        # Convert to dict
        category_counts = {cat: count for cat, count in categories}
        
        return CategoryDistribution(
            bug=category_counts.get("bug", 0),
            feature=category_counts.get("feature", 0),
            billing=category_counts.get("billing", 0),
            support=category_counts.get("support", 0),
            other=category_counts.get("other", 0)
        )
    
    def get_sentiment_distribution(self, days: int = 30) -> SentimentDistribution:
        """
        Get distribution of tickets by sentiment
        
        Args:
            days: Number of days to look back
            
        Returns:
            SentimentDistribution object
        """
        date_threshold = self._get_date_range(days)
        
        # Query sentiment counts
        sentiments = self.db.query(
            TicketAnalysis.sentiment,
            func.count(TicketAnalysis.id).label("count")
        ).join(Ticket).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= date_threshold
        ).group_by(TicketAnalysis.sentiment).all()
        
        # Convert to dict
        sentiment_counts = {sent: count for sent, count in sentiments}
        
        return SentimentDistribution(
            positive=sentiment_counts.get("positive", 0),
            neutral=sentiment_counts.get("neutral", 0),
            negative=sentiment_counts.get("negative", 0)
        )
    
    def get_full_analytics(self) -> AnalyticsResponse:
        """
        Get complete analytics for dashboard
        
        Returns:
            AnalyticsResponse with all metrics
        """
        return AnalyticsResponse(
            stats=self.get_dashboard_stats(),
            category_distribution=self.get_category_distribution(),
            sentiment_distribution=self.get_sentiment_distribution()
        )
    
    def get_trend_data(self, days: int = 30) -> Dict:
        """
        Get daily trend data for charts
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with daily metrics
        """
        date_threshold = self._get_date_range(days)
        
        # Get daily ticket counts
        daily_counts = self.db.query(
            func.date(Ticket.processed_at).label("date"),
            func.count(Ticket.id).label("count"),
            func.avg(TicketAnalysis.processing_time).label("avg_time"),
            func.sum(TicketAnalysis.cost).label("cost")
        ).join(TicketAnalysis).filter(
            Ticket.user_id == self.user.id,
            Ticket.processed_at >= date_threshold
        ).group_by(func.date(Ticket.processed_at)).all()
        
        return {
            "daily_data": [
                {
                    "date": str(row.date),
                    "tickets": row.count,
                    "avg_processing_time": round(row.avg_time, 2) if row.avg_time else 0,
                    "cost": round(row.cost, 4) if row.cost else 0
                }
                for row in daily_counts
            ]
        }
