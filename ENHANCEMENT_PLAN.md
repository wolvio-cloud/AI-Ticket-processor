# 🚀 AI TICKET PROCESSOR - ENHANCEMENT IMPLEMENTATION PLAN

**Version:** 2.2 Enterprise-Ready MVP
**Date:** November 7, 2025
**Status:** Implementation Phase

---

## 📊 GAP ANALYSIS

### ✅ What You Have (Complete)
- ✅ Zendesk API integration (fetch, update, search)
- ✅ OpenAI GPT-4o-mini analysis
- ✅ Multi-industry detection (E-commerce, SaaS, General)
- ✅ PII redaction (9 types)
- ✅ Parallel batch processing (10 workers)
- ✅ Basic dashboard (Streamlit)
- ✅ FastAPI backend with PostgreSQL
- ✅ JWT authentication
- ✅ Basic analytics
- ✅ Docker deployment
- ✅ Tag merge pattern (preserves Zendesk native tags)
- ✅ JSON comment format
- ✅ Cost tracking

### ❌ What Needs Building (Enhancements)

#### **HIGH PRIORITY (Build First)**
1. ❌ **Real-time webhook triggers** (v2.1) - 1 week
2. ❌ **Enhanced monitoring & alerting** (PagerDuty, Slack) - 3 days
3. ❌ **Circuit breaker & rate limiting** - 3 days
4. ❌ **DLP enhancements** (NER-based PII detection) - 1 week
5. ❌ **Audit trail system** (12-month retention) - 3 days

#### **MEDIUM PRIORITY (Build Next)**
6. ❌ **Multi-platform support** (Freshdesk, Intercom) - v2.2 - 2 weeks
7. ❌ **Private LLM integration** (Llama 3.1 8B) - v3.0 - 3 weeks
8. ❌ **Human-in-loop QA system** - 1 week
9. ❌ **Auto-reply draft generation** - v2.3 - 3 weeks
10. ❌ **Advanced metrics** (Precision/Recall/F1) - 1 week

#### **LOW PRIORITY (Future)**
11. ❌ **Multi-language support** - v3.1 - 4 weeks
12. ❌ **SLA prediction/escalation** - v4.0 - 6 weeks
13. ❌ **Multi-client SaaS dashboard** - v5.0 - 8 weeks

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: Core Enhancements (Weeks 1-2)**
**Goal:** Make system production-ready with enterprise features

#### Week 1: Real-time Processing & Monitoring

**Day 1-2: Webhook System**
- [ ] Create webhook endpoint `/webhooks/zendesk`
- [ ] Implement signature verification
- [ ] Add event filtering (ticket.created, ticket.updated)
- [ ] Queue system for async processing
- [ ] Implement retry logic
- [ ] Add webhook registration management

**Day 3-4: Monitoring & Alerting**
- [ ] Integrate PagerDuty SDK
- [ ] Add Slack webhook notifications
- [ ] Create alert templates (high urgency, failure rate, etc.)
- [ ] Implement SLI tracking (success rate, latency, error rate)
- [ ] Add health check endpoints
- [ ] Create monitoring dashboard

**Day 5-7: Rate Limiting & Circuit Breaker**
- [ ] Implement token bucket rate limiter
- [ ] Add circuit breaker pattern (pybreaker)
- [ ] Create rate limit monitoring
- [ ] Add graceful degradation
- [ ] Implement queue overflow handling
- [ ] Add backpressure mechanisms

#### Week 2: Security & Compliance

**Day 8-10: Enhanced DLP & Security**
- [ ] Integrate spaCy for NER-based PII detection
- [ ] Add regex patterns for additional PII types
- [ ] Implement AES-256 encryption for API keys
- [ ] Add TLS 1.3 enforcement
- [ ] Create data retention policies
- [ ] Implement field-level encryption

**Day 11-12: Audit Trail System**
- [ ] Create AuditLog model (PostgreSQL)
- [ ] Log all API calls, processing events, changes
- [ ] Add user activity tracking
- [ ] Implement 12-month retention with archival
- [ ] Create audit log query API
- [ ] Build audit log viewer UI

**Day 13-14: Testing & Documentation**
- [ ] Write unit tests for new features
- [ ] Integration tests for webhooks
- [ ] Load testing (simulate 1,000 tickets/hour)
- [ ] Update API documentation
- [ ] Create admin guides

---

### **Phase 2: Multi-Platform Support (Weeks 3-4)**
**Goal:** Support Freshdesk and Intercom

#### Week 3: Freshdesk Integration

**Day 15-17: Freshdesk API Client**
- [ ] Create `freshdesk_service.py`
- [ ] Implement ticket fetching
- [ ] Add ticket update with notes
- [ ] Implement search/filter
- [ ] Add connection testing
- [ ] Map Freshdesk fields to internal model

**Day 18-19: Freshdesk Webhook Handler**
- [ ] Create Freshdesk webhook endpoint
- [ ] Implement signature verification
- [ ] Add event parsing
- [ ] Integrate with processing queue

**Day 20-21: Testing & Polish**
- [ ] Test all Freshdesk operations
- [ ] Create Freshdesk setup guide
- [ ] Add UI for Freshdesk configuration

#### Week 4: Intercom Integration

**Day 22-24: Intercom API Client**
- [ ] Create `intercom_service.py`
- [ ] Implement conversation fetching
- [ ] Add reply/note functionality
- [ ] Implement filtering
- [ ] Add connection testing
- [ ] Map Intercom conversations to tickets

**Day 25-26: Intercom Webhook Handler**
- [ ] Create Intercom webhook endpoint
- [ ] Implement signature verification
- [ ] Add event parsing
- [ ] Handle conversation events

**Day 27-28: UI & Documentation**
- [ ] Add platform selector in UI
- [ ] Create unified ticket view
- [ ] Update documentation
- [ ] Test multi-platform switching

---

### **Phase 3: Private LLM & Advanced Features (Weeks 5-7)**
**Goal:** Add private LLM support and auto-reply

#### Week 5: Private LLM Integration (v3.0)

**Day 29-31: Llama 3.1 Setup**
- [ ] Set up Ollama/vLLM for Llama 3.1 8B
- [ ] Create Docker container for local LLM
- [ ] Configure model parameters (temp, max_tokens)
- [ ] Benchmark performance (latency, accuracy)
- [ ] Optimize inference speed

**Day 32-33: LLM Service Abstraction**
- [ ] Create `BaseLLMService` abstract class
- [ ] Implement `OpenAIService` (existing)
- [ ] Implement `LlamaService` (new)
- [ ] Add model selection in settings
- [ ] Implement fallback logic
- [ ] Add cost tracking for both

**Day 34-35: Testing & Optimization**
- [ ] Compare accuracy: OpenAI vs Llama
- [ ] Optimize prompts for Llama
- [ ] Load testing
- [ ] Document setup process
- [ ] Create deployment guide

#### Week 6: Auto-Reply Drafts (v2.3)

**Day 36-38: Reply Generation**
- [ ] Create auto-reply prompt templates
- [ ] Implement reply generation service
- [ ] Add tone customization (friendly, professional, etc.)
- [ ] Implement template system
- [ ] Add variable substitution
- [ ] Create reply preview

**Day 39-40: Integration & UI**
- [ ] Add reply draft to ticket updates
- [ ] Create UI for reply review
- [ ] Add approve/reject workflow
- [ ] Implement reply editing
- [ ] Add send functionality

**Day 41-42: Quality Control**
- [ ] Test reply quality
- [ ] Create reply templates library
- [ ] Add human-in-loop review
- [ ] Document best practices

#### Week 7: Human-in-Loop QA System

**Day 43-45: QA Interface**
- [ ] Create QA review queue
- [ ] Build ticket review UI
- [ ] Add feedback form (correct/incorrect)
- [ ] Implement sampling (5% random)
- [ ] Create metrics dashboard
- [ ] Add QA analytics

**Day 46-47: Fine-tuning Pipeline**
- [ ] Collect feedback data
- [ ] Create training data export
- [ ] Implement model fine-tuning workflow
- [ ] Add A/B testing framework
- [ ] Document fine-tuning process

**Day 48-49: Testing & Rollout**
- [ ] Test QA workflow
- [ ] Train team on QA process
- [ ] Create QA guidelines
- [ ] Launch QA program

---

### **Phase 4: Advanced Features (Weeks 8-10)**

#### Week 8: Multi-Language Support (v3.1)
- [ ] Language detection (langdetect)
- [ ] Multi-language prompts
- [ ] Translation service integration
- [ ] Language-specific analysis
- [ ] Testing with 5+ languages

#### Week 9: SLA Prediction (v4.0)
- [ ] Collect historical SLA data
- [ ] Train prediction model
- [ ] Implement SLA scoring
- [ ] Add escalation rules
- [ ] Create SLA dashboard

#### Week 10: Multi-Client Dashboard (v5.0)
- [ ] Multi-tenancy enhancement
- [ ] Client isolation
- [ ] Per-client dashboards
- [ ] Usage tracking
- [ ] Billing integration

---

## 🏗️ TECHNICAL SPECIFICATIONS

### 1. Webhook System Architecture

```python
# webhooks/zendesk.py

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.services.webhook_processor import WebhookProcessor
from app.utils.signature_validator import validate_zendesk_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/zendesk")
async def zendesk_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Zendesk webhook endpoint for real-time ticket processing
    """
    # 1. Verify webhook signature
    body = await request.body()
    signature = request.headers.get("X-Zendesk-Webhook-Signature")

    if not validate_zendesk_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Parse webhook payload
    payload = await request.json()
    event_type = payload.get("type")
    ticket_data = payload.get("ticket")

    # 3. Filter events
    if event_type not in ["ticket.created", "ticket.updated"]:
        return {"status": "ignored", "reason": "event_type_not_supported"}

    # 4. Queue for async processing
    background_tasks.add_task(
        WebhookProcessor.process_ticket_event,
        ticket_data,
        event_type
    )

    return {"status": "queued", "ticket_id": ticket_data.get("id")}
```

### 2. Circuit Breaker Implementation

```python
# utils/circuit_breaker.py

from pybreaker import CircuitBreaker, CircuitBreakerError
import logging

logger = logging.getLogger(__name__)

# OpenAI circuit breaker
openai_breaker = CircuitBreaker(
    fail_max=5,           # Open after 5 failures
    timeout_duration=60,  # Try again after 60 seconds
    name="OpenAI API"
)

# Zendesk circuit breaker
zendesk_breaker = CircuitBreaker(
    fail_max=3,
    timeout_duration=30,
    name="Zendesk API"
)

@openai_breaker
def call_openai_api(prompt, model="gpt-4o-mini"):
    """
    Protected OpenAI API call with circuit breaker
    """
    try:
        # Make API call
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        return response
    except Exception as e:
        logger.error(f"OpenAI API failed: {e}")
        raise
```

### 3. Rate Limiter (Token Bucket)

```python
# utils/rate_limiter.py

import time
from threading import Lock
from typing import Dict

class TokenBucket:
    """
    Token bucket rate limiter
    """
    def __init__(self, rate: float, capacity: int):
        self.rate = rate           # Tokens per second
        self.capacity = capacity   # Max tokens
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens. Returns True if successful.
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            # Try to consume
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_for_token(self, timeout: float = None) -> bool:
        """
        Wait until a token is available
        """
        start = time.time()
        while True:
            if self.consume():
                return True

            if timeout and (time.time() - start) > timeout:
                return False

            time.sleep(0.1)  # Check every 100ms

# Global rate limiters
rate_limiters: Dict[str, TokenBucket] = {
    "openai": TokenBucket(rate=10, capacity=20),      # 10 req/sec, burst 20
    "zendesk": TokenBucket(rate=100, capacity=200),   # 100 req/sec, burst 200
}
```

### 4. Enhanced PII Detection (NER-based)

```python
# pii_redactor_enhanced.py

import re
import spacy
from typing import Dict, List, Tuple

class EnhancedPIIRedactor:
    """
    Enhanced PII redaction using regex + NER
    """

    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Download if not available
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Regex patterns (existing)
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        }

    def redact(self, text: str, preserve_emails: bool = False) -> Dict:
        """
        Redact PII using both regex and NER
        """
        redacted_text = text
        redactions = {}

        # 1. Regex-based redaction (fast, specific patterns)
        for pii_type, pattern in self.patterns.items():
            if pii_type == 'email' and preserve_emails:
                continue

            matches = re.findall(pattern, text)
            if matches:
                redactions[pii_type] = len(matches)
                for match in matches:
                    redacted_text = redacted_text.replace(match, f"[{pii_type.upper()}_REDACTED]")

        # 2. NER-based redaction (names, organizations, locations)
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC']:
                pii_type = f"ner_{ent.label_.lower()}"
                redactions[pii_type] = redactions.get(pii_type, 0) + 1
                redacted_text = redacted_text.replace(ent.text, f"[{ent.label_}_REDACTED]")

        return {
            'original_text': text,
            'redacted_text': redacted_text,
            'has_pii': len(redactions) > 0,
            'redactions': redactions
        }
```

### 5. Audit Trail System

```python
# models/audit_log.py

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), index=True)  # "ticket_processed", "settings_updated"
    resource_type = Column(String(50), index=True)  # "ticket", "user", "settings"
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    status = Column(String(20))  # "success", "failure"
    error_message = Column(Text, nullable=True)

    # Retention: 12 months
    # Add index on timestamp for efficient queries
    # Add archival job to move old logs to cold storage

# Usage
def log_audit_event(
    action: str,
    resource_type: str,
    resource_id: str = None,
    user_id: int = None,
    details: dict = None,
    status: str = "success",
    ip_address: str = None,
    user_agent: str = None
):
    """
    Log an audit event
    """
    audit_log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details,
        status=status,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
```

### 6. Private LLM Service (Llama 3.1)

```python
# services/llama_service.py

import requests
from typing import Dict
from app.services.base_llm_service import BaseLLMService

class LlamaService(BaseLLMService):
    """
    Private LLM service using Llama 3.1 8B via Ollama/vLLM
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.1:8b"

    def analyze_ticket(self, subject: str, description: str) -> Dict:
        """
        Analyze ticket using local Llama model
        """
        prompt = self._build_prompt(subject, description)

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 200
                    }
                },
                timeout=10
            )
            response.raise_for_status()

            result = response.json()
            analysis = self._parse_response(result["response"])

            return {
                "success": True,
                "analysis": analysis,
                "model": self.model,
                "tokens_used": result.get("eval_count", 0),
                "cost": 0.0  # Private LLM has no per-token cost
            }

        except Exception as e:
            return self._fallback_response(str(e))
```

---

## 📊 MONITORING & ALERTING SYSTEM

### Metrics to Track

#### 1. **Service Level Indicators (SLIs)**
```python
# SLI Definitions
SLIs = {
    "success_rate": {
        "target": 99.0,  # 99% success rate
        "measurement": "successful_requests / total_requests * 100"
    },
    "latency_p95": {
        "target": 5.0,  # 5 seconds at 95th percentile
        "measurement": "processing_time_95th_percentile"
    },
    "error_rate": {
        "target": 1.0,  # <1% error rate
        "measurement": "failed_requests / total_requests * 100"
    },
    "availability": {
        "target": 99.9,  # 99.9% uptime
        "measurement": "uptime / total_time * 100"
    }
}
```

#### 2. **Alert Rules**
```python
# alerts/rules.py

ALERT_RULES = [
    {
        "name": "High Error Rate",
        "condition": "error_rate > 5%",
        "severity": "critical",
        "channels": ["pagerduty", "slack"],
        "message": "Error rate is {error_rate}% (threshold: 5%)"
    },
    {
        "name": "High Urgency Tickets",
        "condition": "high_urgency_count > 10",
        "severity": "warning",
        "channels": ["slack"],
        "message": "{high_urgency_count} high-urgency tickets detected"
    },
    {
        "name": "Negative Sentiment Spike",
        "condition": "negative_sentiment_rate > 30%",
        "severity": "warning",
        "channels": ["slack"],
        "message": "Negative sentiment at {negative_sentiment_rate}%"
    },
    {
        "name": "Processing Queue Backup",
        "condition": "queue_size > 100",
        "severity": "warning",
        "channels": ["slack"],
        "message": "Processing queue has {queue_size} tickets"
    },
    {
        "name": "API Rate Limit Approaching",
        "condition": "api_usage > 80%",
        "severity": "warning",
        "channels": ["slack"],
        "message": "API usage at {api_usage}% of rate limit"
    }
]
```

#### 3. **PagerDuty Integration**
```python
# services/pagerduty_service.py

from pdpyras import EventsAPISession

class PagerDutyService:
    def __init__(self, integration_key: str):
        self.session = EventsAPISession(integration_key)

    def trigger_incident(
        self,
        summary: str,
        severity: str = "error",
        details: dict = None
    ):
        """
        Trigger a PagerDuty incident
        """
        self.session.trigger(
            summary=summary,
            severity=severity,
            source="AI Ticket Processor",
            custom_details=details
        )

    def resolve_incident(self, dedup_key: str):
        """
        Resolve a PagerDuty incident
        """
        self.session.resolve(dedup_key=dedup_key)
```

#### 4. **Slack Notifications**
```python
# services/slack_service.py

import requests

class SlackService:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "warning",
        fields: dict = None
    ):
        """
        Send alert to Slack
        """
        color_map = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#0000FF"
        }

        payload = {
            "attachments": [{
                "color": color_map.get(severity, "#808080"),
                "title": title,
                "text": message,
                "fields": [
                    {"title": k, "value": v, "short": True}
                    for k, v in (fields or {}).items()
                ],
                "footer": "AI Ticket Processor",
                "ts": int(time.time())
            }]
        }

        requests.post(self.webhook_url, json=payload)
```

---

## 🔐 SECURITY ENHANCEMENTS

### 1. API Key Encryption

```python
# utils/encryption.py

from cryptography.fernet import Fernet
import os

class EncryptionService:
    """
    AES-256 encryption for sensitive data
    """

    def __init__(self):
        # Load encryption key from environment
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            # Generate new key if not exists
            key = Fernet.generate_key()
            print(f"Generated encryption key: {key.decode()}")
            print("Add this to your .env file as ENCRYPTION_KEY")

        self.cipher = Fernet(key if isinstance(key, bytes) else key.encode())

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        """
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string
        """
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Usage in User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

    # Encrypted fields
    _zendesk_api_token = Column("zendesk_api_token", String)
    _openai_api_key = Column("openai_api_key", String)

    encryption_service = EncryptionService()

    @property
    def zendesk_api_token(self) -> str:
        if self._zendesk_api_token:
            return self.encryption_service.decrypt(self._zendesk_api_token)
        return None

    @zendesk_api_token.setter
    def zendesk_api_token(self, value: str):
        if value:
            self._zendesk_api_token = self.encryption_service.encrypt(value)
```

### 2. Data Retention Policy

```python
# tasks/data_retention.py

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import AuditLog, ProcessingLog

def cleanup_old_logs():
    """
    Archive/delete logs older than retention period
    """
    db = SessionLocal()

    # Audit logs: 12 months retention
    audit_cutoff = datetime.now() - timedelta(days=365)
    old_audit_logs = db.query(AuditLog).filter(
        AuditLog.timestamp < audit_cutoff
    )

    # Archive to S3/cold storage before delete
    archive_logs_to_s3(old_audit_logs.all())
    old_audit_logs.delete()

    # Processing logs: 90 days retention
    processing_cutoff = datetime.now() - timedelta(days=90)
    db.query(ProcessingLog).filter(
        ProcessingLog.created_at < processing_cutoff
    ).delete()

    db.commit()
    db.close()

# Schedule with Celery
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('tasks')

@celery_app.task
def scheduled_cleanup():
    cleanup_old_logs()

# Run daily at 2 AM
celery_app.conf.beat_schedule = {
    'cleanup-logs': {
        'task': 'tasks.data_retention.scheduled_cleanup',
        'schedule': crontab(hour=2, minute=0)
    }
}
```

---

## 📦 DEPLOYMENT ENHANCEMENTS

### Docker Compose - Enhanced

```yaml
# docker-compose.production.yml

version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ticketai
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ticketai
      REDIS_URL: redis://redis:6379/0
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      PAGERDUTY_KEY: ${PAGERDUTY_KEY}
      SLACK_WEBHOOK: ${SLACK_WEBHOOK}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - backend
      - frontend
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Celery Worker
  celery_worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ticketai
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - backend
    restart: unless-stopped

  # Celery Beat (Scheduler)
  celery_beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ticketai
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - backend
    restart: unless-stopped

  # Private LLM (Llama 3.1)
  llama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - backend
    environment:
      OLLAMA_MODELS: llama3.1:8b
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    networks:
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  ollama_data:

networks:
  backend:
  frontend:
```

---

## 🧪 TESTING STRATEGY

### 1. Unit Tests
```python
# tests/test_webhook_system.py

import pytest
from app.webhooks.zendesk import zendesk_webhook
from app.utils.signature_validator import validate_zendesk_signature

def test_webhook_signature_validation():
    """Test webhook signature verification"""
    body = b'{"ticket": {"id": 123}}'
    signature = generate_test_signature(body)

    assert validate_zendesk_signature(body, signature) == True
    assert validate_zendesk_signature(body, "invalid") == False

def test_webhook_event_filtering():
    """Test that only relevant events are processed"""
    payload = {"type": "ticket.created", "ticket": {"id": 123}}
    result = process_webhook_payload(payload)
    assert result["status"] == "queued"

    payload = {"type": "ticket.deleted", "ticket": {"id": 123}}
    result = process_webhook_payload(payload)
    assert result["status"] == "ignored"
```

### 2. Integration Tests
```python
# tests/test_integration.py

def test_end_to_end_processing():
    """Test complete ticket processing flow"""
    # 1. Create test ticket in Zendesk
    ticket = create_test_ticket()

    # 2. Trigger webhook
    trigger_webhook(ticket.id)

    # 3. Wait for processing
    time.sleep(5)

    # 4. Verify ticket was updated
    updated_ticket = get_ticket(ticket.id)
    assert "ai_processed" in updated_ticket.tags
    assert updated_ticket.priority is not None
```

### 3. Load Tests
```python
# tests/load_test.py

import concurrent.futures

def test_concurrent_processing():
    """Test system under load"""
    num_tickets = 1000

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(process_ticket, i)
            for i in range(num_tickets)
        ]

        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
    assert success_rate >= 99.0  # 99% success rate target
```

---

## 📈 SUCCESS METRICS

### Key Performance Indicators (KPIs)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Processing Time** | 3.5s | <5s | ✅ |
| **Success Rate** | 100% | >99% | ✅ |
| **Cost per Ticket** | $0.001 | <$0.002 | ✅ |
| **Accuracy (Root Cause)** | 91.7% | >93% | ⚠️ |
| **Accuracy (Urgency)** | - | >95% | ⏳ |
| **Accuracy (Sentiment)** | - | >92% | ⏳ |
| **Webhook Latency** | - | <2s | ⏳ |
| **Uptime** | - | >99.9% | ⏳ |

### Business Metrics

| Metric | Month 1 | Month 3 | Month 6 |
|--------|---------|---------|---------|
| **Active Customers** | 5 | 20 | 50 |
| **Tickets Processed** | 10K | 50K | 200K |
| **Revenue** | $10K | $40K | $100K |
| **Customer Satisfaction** | - | >4.5/5 | >4.7/5 |

---

## 🚀 IMMEDIATE NEXT STEPS

### This Week: Foundation Setup

1. **Set up enhanced project structure**
   ```bash
   mkdir -p backend/app/{webhooks,services,utils,alerts,tasks}
   ```

2. **Install new dependencies**
   ```bash
   cd backend
   pip install pybreaker pdpyras spacy cryptography celery
   python -m spacy download en_core_web_sm
   ```

3. **Create webhook endpoint** (Day 1-2)
   - Implement `/webhooks/zendesk`
   - Add signature verification
   - Test with Zendesk test tickets

4. **Implement monitoring** (Day 3-4)
   - Set up PagerDuty integration
   - Add Slack notifications
   - Create alert rules

5. **Add rate limiting** (Day 5)
   - Implement token bucket
   - Add circuit breaker
   - Test under load

**Ready to start? I can help you implement any of these features. Which would you like to build first?**

1. **Webhook system** (real-time processing)
2. **Monitoring & alerting** (PagerDuty + Slack)
3. **Rate limiting & circuit breaker**
4. **Enhanced PII detection** (NER-based)
5. **Audit trail system**

Or shall we start with all of Phase 1 (Week 1-2)?
