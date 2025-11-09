"""
Security Configuration Module
Implements international security standards (OWASP, ISO 27001, SOC 2)
"""

import os
import re
import secrets
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY CONSTANTS (OWASP Recommendations)
# ============================================================================

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 60
MAX_REQUESTS_PER_HOUR = 1000
MAX_FAILED_AUTH_ATTEMPTS = 5
AUTH_LOCKOUT_DURATION_MINUTES = 30

# Input Validation
MAX_INPUT_LENGTH = 50000  # Max characters in ticket description
MAX_FIELD_LENGTH = 1000   # Max characters in individual fields
ALLOWED_CONTENT_TYPES = ['application/json', 'text/plain']

# Timeouts (prevent DoS)
API_TIMEOUT_SECONDS = 30
OPENAI_TIMEOUT_SECONDS = 60
ZENDESK_TIMEOUT_SECONDS = 30

# Security Headers (OWASP recommendations)
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# Allowed origins for CORS (update with your domains)
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://api.yourdomain.com"
]

# ============================================================================
# INPUT VALIDATION (Prevent Injection Attacks)
# ============================================================================

class InputValidator:
    """
    Validates and sanitizes user inputs to prevent injection attacks
    Follows OWASP Input Validation principles
    """
    
    # Dangerous patterns (SQL injection, XSS, command injection)
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",                 # XSS
        r"on\w+\s*=",                  # Event handlers
        r"(\bunion\b.*\bselect\b|\bselect\b.*\bunion\b)",  # SQL injection
        r"(\bexec\b|\bexecute\b|\bdrop\b|\bdelete\b|\binsert\b|\bupdate\b)\s+",  # SQL injection
        r"(&&|\|\||;|\$\(|\`)",        # Command injection
        r"\.\.\/",                      # Path traversal
        r"<iframe",                     # Iframe injection
        r"eval\s*\(",                   # Code injection
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = MAX_FIELD_LENGTH) -> str:
        """
        Sanitize string input (remove dangerous characters)
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Trim to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except newline, tab, carriage return
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        return value.strip()
    
    @classmethod
    def validate_input(cls, value: str, field_name: str = "input") -> str:
        """
        Validate input for dangerous patterns
        Raises ValueError if dangerous pattern detected
        """
        if not value:
            return value
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in {field_name}: {pattern}")
                raise ValueError(f"Invalid input detected in {field_name}")
        
        return cls.sanitize_string(value)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format (only HTTPS allowed for security)"""
        pattern = r'^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_ticket_id(ticket_id: Any) -> int:
        """Validate ticket ID (must be positive integer)"""
        try:
            tid = int(ticket_id)
            if tid <= 0:
                raise ValueError("Ticket ID must be positive")
            return tid
        except (ValueError, TypeError):
            raise ValueError("Invalid ticket ID format")

# ============================================================================
# SECRET MANAGEMENT (Prevent Secret Exposure)
# ============================================================================

class SecretManager:
    """
    Manages sensitive credentials securely
    Follows NIST SP 800-57 key management guidelines
    """
    
    @staticmethod
    def validate_environment_variables() -> Dict[str, bool]:
        """
        Validate that all required environment variables are set
        Returns dict of variable name -> is_set
        """
        required_vars = [
            'ZENDESK_SUBDOMAIN',
            'ZENDESK_EMAIL',
            'ZENDESK_API_TOKEN',
            'OPENAI_API_KEY'
        ]
        
        results = {}
        missing = []
        
        for var in required_vars:
            value = os.getenv(var)
            is_set = bool(value and value.strip())
            results[var] = is_set
            
            if not is_set:
                missing.append(var)
        
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
        
        return results
    
    @staticmethod
    def mask_secret(secret: str, visible_chars: int = 4) -> str:
        """
        Mask secret for logging (show only last N characters)
        """
        if not secret or len(secret) <= visible_chars:
            return "***"
        return f"***{secret[-visible_chars:]}"
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_value(value: str) -> str:
        """Hash a value using SHA-256 (for comparing without storing)"""
        return hashlib.sha256(value.encode()).hexdigest()

# ============================================================================
# RATE LIMITING (Prevent Abuse and DoS)
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis or similar distributed cache
    """
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = {}
        self._failed_auth: Dict[str, int] = {}
        self._lockouts: Dict[str, datetime] = {}
    
    def check_rate_limit(self, identifier: str, max_requests: int, window_minutes: int) -> bool:
        """
        Check if identifier has exceeded rate limit
        Returns True if allowed, False if rate limited
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Initialize if new identifier
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Clean old requests outside window
        self._requests[identifier] = [
            req_time for req_time in self._requests[identifier]
            if req_time > window_start
        ]
        
        # Check if within limit
        if len(self._requests[identifier]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self._requests[identifier].append(now)
        return True
    
    def record_failed_auth(self, identifier: str) -> bool:
        """
        Record failed authentication attempt
        Returns True if account should be locked
        """
        if identifier not in self._failed_auth:
            self._failed_auth[identifier] = 0
        
        self._failed_auth[identifier] += 1
        
        if self._failed_auth[identifier] >= MAX_FAILED_AUTH_ATTEMPTS:
            self._lockouts[identifier] = datetime.now()
            logger.warning(f"Account locked due to failed auth attempts: {identifier}")
            return True
        
        return False
    
    def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is locked out"""
        if identifier not in self._lockouts:
            return False
        
        lockout_time = self._lockouts[identifier]
        lockout_end = lockout_time + timedelta(minutes=AUTH_LOCKOUT_DURATION_MINUTES)
        
        if datetime.now() < lockout_end:
            return True
        
        # Lockout expired, clear it
        del self._lockouts[identifier]
        self._failed_auth[identifier] = 0
        return False

# ============================================================================
# LOGGING SECURITY (Prevent Log Injection & Info Disclosure)
# ============================================================================

class SecureLogger:
    """
    Secure logging wrapper that prevents log injection and sensitive data exposure
    """
    
    SENSITIVE_PATTERNS = [
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]'),  # Credit card
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),  # SSN
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),  # Email
        (r'bearer\s+[A-Za-z0-9\-._~+/]+', 'bearer [TOKEN_REDACTED]'),  # Bearer token
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', 'api_key=[REDACTED]'),  # API key
    ]
    
    @classmethod
    def sanitize_log_message(cls, message: str) -> str:
        """Remove sensitive data from log messages"""
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        # Remove newlines to prevent log injection
        message = message.replace('\n', ' ').replace('\r', ' ')
        
        return message
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any]):
        """Log security-related events for auditing"""
        timestamp = datetime.now().isoformat()
        logger.warning(f"SECURITY_EVENT | {timestamp} | {event_type} | {details}")

# ============================================================================
# CORS AND SECURITY HEADERS
# ============================================================================

def get_cors_headers(origin: str) -> Dict[str, str]:
    """
    Get CORS headers if origin is allowed
    """
    if origin in ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
    return {}

# ============================================================================
# INITIALIZATION
# ============================================================================

# Global instances
validator = InputValidator()
secret_manager = SecretManager()
rate_limiter = RateLimiter()
secure_logger = SecureLogger()

# Validate environment on module load (fail fast)
try:
    secret_manager.validate_environment_variables()
    logger.info("✅ Security configuration initialized successfully")
except EnvironmentError as e:
    logger.error(f"❌ Security initialization failed: {e}")
    raise

if __name__ == "__main__":
    print("Security Configuration Module")
    print("=" * 50)
    print("\n✅ All security checks passed")
    print(f"- Max requests per minute: {MAX_REQUESTS_PER_MINUTE}")
    print(f"- Max input length: {MAX_INPUT_LENGTH}")
    print(f"- API timeout: {API_TIMEOUT_SECONDS}s")
    print(f"- Security headers configured: {len(SECURITY_HEADERS)}")
