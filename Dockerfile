# Production Dockerfile for AI Ticket Processor
# Optimized for GCP Cloud Run deployment with PII protection

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (GCP best practice)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy requirements first (leverages Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R appuser:appuser logs

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    LOG_DIR=/app/logs \
    PORT=8080

# Health check (optional, useful for monitoring)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command: Process 50 tickets with PII protection
# Can be overridden in Cloud Run deployment
CMD ["python", "Ai_ticket_processor.py", "--limit", "50"]
