"""
================================================================================
Configuration Management - Application Settings and Environment Variables
================================================================================

DESCRIPTION:
    Centralized configuration management using Pydantic BaseSettings.
    Loads and validates all environment variables required for the application.

FEATURES:
    - Type-safe configuration with Pydantic validation
    - Automatic .env file loading
    - Default values for optional settings
    - Environment variable validation on startup
    - Secure secret management

CONFIGURATION CATEGORIES:
    - Database: PostgreSQL connection settings
    - Redis: Cache and session storage
    - Security: JWT secrets, API keys
    - OpenAI: API keys and model settings
    - Zendesk: API credentials
    - CORS: Allowed origins for web clients
    - Logging: Log levels and formatting

ENVIRONMENT VARIABLES:
    Required:
        DATABASE_URL        - PostgreSQL connection string
        REDIS_URL           - Redis connection string
        SECRET_KEY          - JWT secret key
        OPENAI_API_KEY      - OpenAI API key
        ZENDESK_SUBDOMAIN   - Zendesk subdomain
        ZENDESK_EMAIL       - Zendesk email
        ZENDESK_API_TOKEN   - Zendesk API token

    Optional:
        CORS_ORIGINS        - Comma-separated allowed origins
        LOG_LEVEL           - Logging level (default: INFO)
        MAX_WORKERS         - Thread pool size (default: 5)

USAGE:
    from app.config import settings

    # Access configuration
    print(settings.DATABASE_URL)
    print(settings.OPENAI_API_KEY)

.ENV FILE EXAMPLE:
    DATABASE_URL=postgresql://user:pass@localhost/dbname
    REDIS_URL=redis://localhost:6379
    SECRET_KEY=your-secret-key-here
    OPENAI_API_KEY=sk-...
    ZENDESK_SUBDOMAIN=yourcompany
    ZENDESK_EMAIL=admin@yourcompany.com
    ZENDESK_API_TOKEN=your-token

AUTHOR: AI Ticket Processor Team
LICENSE: Proprietary
LAST UPDATED: 2025-11-11
================================================================================
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are type-validated using Pydantic. Missing required
    settings will raise validation errors on startup.
    """
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # OpenAI
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 200
    DEFAULT_OPENAI_API_KEY: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
