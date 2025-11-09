# GCP Deployment Guide - AI Ticket Processor

Production deployment guide for AI Ticket Processor with PII protection on Google Cloud Platform.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Cloud Run Deployment (Recommended)](#cloud-run-deployment-recommended)
- [App Engine Deployment (Alternative)](#app-engine-deployment-alternative)
- [Environment Variables](#environment-variables)
- [Scheduled Execution](#scheduled-execution)
- [Monitoring & Logging](#monitoring--logging)
- [Cost Optimization](#cost-optimization)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed and configured
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   
   # Initialize and authenticate
   gcloud init
   gcloud auth login
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

4. **Set up environment variables**
   ```bash
   export PROJECT_ID="your-gcp-project-id"
   export REGION="us-central1"
   gcloud config set project $PROJECT_ID
   ```

---

## Cloud Run Deployment (Recommended)

Cloud Run is recommended for batch processing with automatic scaling and pay-per-use pricing.

### Step 1: Create Secrets (Secure Credential Storage)

```bash
# Store Zendesk API token
echo -n "your-zendesk-api-token" | \
  gcloud secrets create zendesk-api-token \
  --data-file=- \
  --replication-policy="automatic"

# Store OpenAI API key
echo -n "your-openai-api-key" | \
  gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy="automatic"
```

### Step 2: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create ai-ticket-processor \
  --display-name="AI Ticket Processor Service Account"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ai-ticket-processor@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Grant Cloud Run invoker role (for Cloud Scheduler)
gcloud run services add-iam-policy-binding ai-ticket-processor \
  --member="serviceAccount:ai-ticket-processor@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=$REGION
```

### Step 3: Build and Push Docker Image

```bash
# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/ai-ticket-processor:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/ai-ticket-processor:latest

# Or use Cloud Build (recommended - builds in GCP)
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-ticket-processor:latest
```

### Step 4: Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy ai-ticket-processor \
  --image gcr.io/$PROJECT_ID/ai-ticket-processor:latest \
  --region $REGION \
  --platform managed \
  --service-account ai-ticket-processor@$PROJECT_ID.iam.gserviceaccount.com \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 5 \
  --min-instances 0 \
  --set-env-vars ZENDESK_SUBDOMAIN=your-subdomain \
  --set-env-vars ZENDESK_EMAIL=your-email@example.com \
  --set-secrets ZENDESK_API_TOKEN=zendesk-api-token:latest \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest \
  --no-allow-unauthenticated
```

### Step 5: Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe ai-ticket-processor \
  --region $REGION \
  --format 'value(status.url)')

echo "Service deployed at: $SERVICE_URL"

# Test the service (requires authentication)
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  $SERVICE_URL
```

---

## Scheduled Execution (Every 5 Minutes)

Use Cloud Scheduler to trigger the service automatically.

### Step 1: Create Cloud Scheduler Job

```bash
# Create scheduler job (runs every 5 minutes)
gcloud scheduler jobs create http ai-ticket-processor-job \
  --location $REGION \
  --schedule "*/5 * * * *" \
  --uri "$SERVICE_URL" \
  --http-method POST \
  --oidc-service-account-email ai-ticket-processor@$PROJECT_ID.iam.gserviceaccount.com \
  --headers "Content-Type=application/json" \
  --message-body '{"limit": 50, "force": false}' \
  --time-zone "UTC"
```

### Step 2: Test the Scheduler Job

```bash
# Manually trigger the job to test
gcloud scheduler jobs run ai-ticket-processor-job --location $REGION

# View logs
gcloud scheduler jobs describe ai-ticket-processor-job --location $REGION
```

### Alternative Schedules

```bash
# Every 10 minutes
--schedule "*/10 * * * *"

# Every 30 minutes
--schedule "*/30 * * * *"

# Every hour
--schedule "0 * * * *"

# Business hours only (9 AM - 5 PM, Mon-Fri)
--schedule "0 9-17 * * 1-5"

# Daily at 9 AM
--schedule "0 9 * * *"
```

---

## App Engine Deployment (Alternative)

If you prefer App Engine over Cloud Run:

### Step 1: Update app.yaml with Secrets

Edit `app.yaml` and add environment variables or use Secret Manager.

### Step 2: Deploy to App Engine

```bash
# Deploy
gcloud app deploy app.yaml

# View logs
gcloud app logs tail -s default

# Open in browser
gcloud app browse
```

---

## Environment Variables

Required environment variables for the application:

| Variable | Description | Example |
|----------|-------------|---------|
| `ZENDESK_SUBDOMAIN` | Your Zendesk subdomain | `mycompany` |
| `ZENDESK_EMAIL` | Zendesk admin email | `admin@company.com` |
| `ZENDESK_API_TOKEN` | Zendesk API token | `secret-token-here` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `LOG_DIR` | Log directory path | `/app/logs` |
| `PYTHONUNBUFFERED` | Python output buffering | `1` |

---

## Monitoring & Logging

### View Cloud Run Logs

```bash
# Stream logs in real-time
gcloud run logs tail ai-ticket-processor --region $REGION

# View recent logs
gcloud run logs read ai-ticket-processor --region $REGION --limit 50

# Filter by severity
gcloud run logs read ai-ticket-processor \
  --region $REGION \
  --filter "severity>=ERROR" \
  --limit 20
```

### View Metrics in Cloud Console

1. Go to [Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Run** > **ai-ticket-processor**
3. Click **Logs** or **Metrics** tab

### Set up Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="AI Ticket Processor - High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

---

## Cost Optimization

### Estimated Monthly Costs

**Cloud Run (Pay-per-use)**
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests
- **Estimated**: $5-20/month for 5-minute intervals

**Secrets Manager**
- Active secret versions: $0.06 per secret version per month
- Access operations: $0.03 per 10,000 accesses
- **Estimated**: $0.50/month

**Cloud Scheduler**
- Jobs: $0.10 per job per month
- **Estimated**: $0.10/month

**Total Estimated Cost**: $5-25/month

### Cost Reduction Tips

1. **Adjust schedule**: Run less frequently (e.g., every 15 minutes instead of 5)
   ```bash
   --schedule "*/15 * * * *"
   ```

2. **Reduce resources**: Use 1 CPU / 512Mi memory if processing < 100 tickets
   ```bash
   --cpu 1 --memory 512Mi
   ```

3. **Scale to zero**: Keep `min-instances 0` to avoid idle costs

4. **Use business hours only**: Process tickets only during work hours
   ```bash
   --schedule "0 9-17 * * 1-5"
   ```

---

## Troubleshooting

### Common Issues

**1. Build fails with "permission denied"**
```bash
# Grant Cloud Build service account permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder
```

**2. Service returns 403 Forbidden**
```bash
# Verify service account has Secret Manager access
gcloud secrets get-iam-policy zendesk-api-token
gcloud secrets get-iam-policy openai-api-key
```

**3. Scheduler job fails**
```bash
# Check scheduler job logs
gcloud scheduler jobs describe ai-ticket-processor-job --location $REGION

# Verify service account has Cloud Run invoker role
gcloud run services get-iam-policy ai-ticket-processor --region $REGION
```

**4. Out of memory errors**
```bash
# Increase memory allocation
gcloud run services update ai-ticket-processor \
  --memory 4Gi \
  --region $REGION
```

**5. Timeout errors**
```bash
# Increase timeout (max 900s for Cloud Run)
gcloud run services update ai-ticket-processor \
  --timeout 900 \
  --region $REGION
```

### Debugging

```bash
# View service configuration
gcloud run services describe ai-ticket-processor --region $REGION

# Check environment variables
gcloud run services describe ai-ticket-processor \
  --region $REGION \
  --format "value(spec.template.spec.containers[0].env)"

# Test locally with Docker
docker run -it --rm \
  -e ZENDESK_SUBDOMAIN=your-subdomain \
  -e ZENDESK_EMAIL=your-email \
  -e ZENDESK_API_TOKEN=your-token \
  -e OPENAI_API_KEY=your-key \
  gcr.io/$PROJECT_ID/ai-ticket-processor:latest
```

---

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use Secret Manager** for all sensitive data
3. **Enable VPC** for private network communication
4. **Set up alerts** for unauthorized access attempts
5. **Rotate secrets** regularly (every 90 days)
6. **Use least privilege** IAM roles
7. **Enable audit logging** for compliance

---

## Quick Start Commands

```bash
# Set variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/ai-ticket-processor:latest
gcloud run deploy ai-ticket-processor \
  --image gcr.io/$PROJECT_ID/ai-ticket-processor:latest \
  --region $REGION

# Set up scheduler
gcloud scheduler jobs create http ai-ticket-processor-job \
  --location $REGION \
  --schedule "*/5 * * * *" \
  --uri "$(gcloud run services describe ai-ticket-processor --region $REGION --format 'value(status.url)')" \
  --http-method POST

# View logs
gcloud run logs tail ai-ticket-processor --region $REGION
```

---

## Support

For issues or questions:
- Check [Cloud Run documentation](https://cloud.google.com/run/docs)
- Review [pricing calculator](https://cloud.google.com/products/calculator)
- Open an issue in the repository

---

**Last Updated**: 2025-11-09
**Version**: 1.0
