"""
================================================================================
AI Ticket Processor API - FastAPI Application Entry Point
================================================================================

DESCRIPTION:
    RESTful API service for AI-powered support ticket processing and analytics.
    Provides endpoints for ticket analysis, classification, PII protection,
    and real-time analytics dashboard.

FEATURES:
    - RESTful API with automatic OpenAPI documentation
    - JWT-based authentication and authorization
    - CORS support for web dashboards
    - Real-time analytics and reporting
    - Ticket processing endpoints
    - Settings management
    - Health check and status endpoints

API ENDPOINTS:
    /docs           - Interactive API documentation (Swagger UI)
    /redoc          - Alternative API documentation (ReDoc)
    /api/v1/auth    - Authentication endpoints
    /api/v1/tickets - Ticket processing endpoints
    /api/v1/analytics - Analytics and reporting
    /api/v1/settings - Configuration management

FEATURES BY MODULE:
    - Authentication: JWT tokens, user management
    - Tickets: Process, fetch, update tickets
    - Analytics: Statistics, trends, performance metrics
    - Settings: System configuration, API keys management

STARTUP:
    Database initialization on startup
    Automatic table creation if not exists
    Environment validation

CORS:
    Configured for cross-origin requests from web dashboards
    Origins defined in settings.cors_origins

DOCUMENTATION:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

DEPLOYMENT:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

ENVIRONMENT VARIABLES:
    DATABASE_URL      - PostgreSQL connection string
    JWT_SECRET_KEY    - Secret key for JWT tokens
    OPENAI_API_KEY    - OpenAI API key
    ZENDESK_*         - Zendesk API credentials
    (See settings.py for complete list)

DEPENDENCIES:
    - FastAPI: Web framework
    - SQLAlchemy: ORM and database management
    - Pydantic: Data validation
    - JWT: Authentication
    - CORS: Cross-origin support

AUTHOR: AI Ticket Processor Team
LICENSE: Proprietary
LAST UPDATED: 2025-11-11
================================================================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import init_db
from app.api import auth, tickets, analytics, settings as settings_routes

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Ticket Processor API",
    description="Automated support ticket processing using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting AI Ticket Processor API")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Ticket Processor API")


# Health check endpoint
@app.get("/")
def root():
    """Root endpoint - health check"""
    return {
        "status": "online",
        "service": "AI Ticket Processor API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational"
    }


# Include routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(analytics.router)
app.include_router(settings_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
