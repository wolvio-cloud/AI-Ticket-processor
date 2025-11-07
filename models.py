from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User/Organization model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Integration credentials (encrypted in production)
    zendesk_subdomain = Column(String(100))
    zendesk_email = Column(String(255))
    zendesk_api_token = Column(Text)
    openai_api_key = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="user")


class Ticket(Base):
    """Support ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Zendesk data
    zendesk_ticket_id = Column(Integer, index=True, nullable=False)
    subject = Column(Text)
    description = Column(Text)
    status = Column(String(50))
    priority = Column(String(20))
    requester_email = Column(String(255))
    
    # Timestamps
    ticket_created_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    analysis = relationship("TicketAnalysis", back_populates="ticket", uselist=False)
    logs = relationship("ProcessingLog", back_populates="ticket")


class TicketAnalysis(Base):
    """AI analysis results for tickets"""
    __tablename__ = "ticket_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), unique=True, nullable=False)
    
    # AI analysis results
    summary = Column(Text)
    category = Column(String(50), index=True)  # bug, feature, billing, support, other
    urgency = Column(String(20), index=True)   # low, medium, high
    sentiment = Column(String(20), index=True) # positive, neutral, negative
    
    # Metrics
    processing_time = Column(Float)  # seconds
    cost = Column(Float)             # dollars
    
    # AI response metadata
    model_used = Column(String(50))
    tokens_used = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="analysis")


class ProcessingLog(Base):
    """Processing logs for debugging and monitoring"""
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    
    status = Column(String(50))  # queued, processing, success, failed
    stage = Column(String(100))  # fetch, analyze, update
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="logs")


class SystemMetrics(Base):
    """Daily system metrics for analytics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    date = Column(DateTime(timezone=True), index=True)
    tickets_processed = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    avg_processing_time = Column(Float)
    
    # Category counts
    bugs = Column(Integer, default=0)
    features = Column(Integer, default=0)
    billing = Column(Integer, default=0)
    support = Column(Integer, default=0)
    
    # Sentiment counts
    positive = Column(Integer, default=0)
    neutral = Column(Integer, default=0)
    negative = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
