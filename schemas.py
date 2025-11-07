from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    zendesk_subdomain: Optional[str] = None
    zendesk_email: Optional[EmailStr] = None
    zendesk_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    zendesk_subdomain: Optional[str] = None
    zendesk_email: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ticket Schemas
class TicketBase(BaseModel):
    zendesk_ticket_id: int
    subject: str
    description: str
    status: Optional[str] = None
    priority: Optional[str] = None
    requester_email: Optional[str] = None


class TicketCreate(TicketBase):
    pass


class TicketAnalysisResponse(BaseModel):
    summary: str
    category: str
    urgency: str
    sentiment: str
    processing_time: float
    cost: float
    
    class Config:
        from_attributes = True


class TicketResponse(TicketBase):
    id: int
    user_id: int
    processed_at: Optional[datetime] = None
    created_at: datetime
    analysis: Optional[TicketAnalysisResponse] = None
    
    class Config:
        from_attributes = True


# Analysis Schemas
class AIAnalysisRequest(BaseModel):
    subject: str
    description: str


class AIAnalysisResponse(BaseModel):
    summary: str
    category: str  # bug|feature|billing|support|other
    urgency: str   # low|medium|high
    sentiment: str # positive|neutral|negative


# Processing Schemas
class ProcessTicketRequest(BaseModel):
    ticket_id: int


class ProcessTicketResponse(BaseModel):
    ticket_id: int
    status: str
    analysis: Optional[AIAnalysisResponse] = None
    processing_time: float
    message: str


# Analytics Schemas
class DashboardStats(BaseModel):
    tickets_today: int
    tickets_this_week: int
    tickets_this_month: int
    avg_processing_time: float
    total_cost_today: float
    total_cost_month: float
    accuracy_rate: float


class CategoryDistribution(BaseModel):
    bug: int
    feature: int
    billing: int
    support: int
    other: int


class SentimentDistribution(BaseModel):
    positive: int
    neutral: int
    negative: int


class AnalyticsResponse(BaseModel):
    stats: DashboardStats
    category_distribution: CategoryDistribution
    sentiment_distribution: SentimentDistribution


# Settings Schemas
class ZendeskSettings(BaseModel):
    subdomain: str
    email: EmailStr
    api_token: str


class OpenAISettings(BaseModel):
    api_key: str


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
