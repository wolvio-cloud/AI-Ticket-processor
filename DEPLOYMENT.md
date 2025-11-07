# 🚀 DEPLOYMENT GUIDE

## Option 1: Local Machine (Recommended for Testing)

**Pros:** Free, easy, full control  
**Cons:** Requires computer to be on  
**Setup Time:** 5 minutes

```bash
# Setup
./setup.sh

# Edit .env with your keys
nano .env

# Test
python test_system.py

# Run manually
python ai_ticket_processor.py --limit 10

# OR setup cron (runs every 5 minutes)
crontab -e
*/5 * * * * cd /path/to/ai-ticket-processor-v2 && python ai_ticket_processor.py --limit 50
```

---

## Option 2: Docker Container

**Pros:** Portable, consistent environment  
**Cons:** Requires Docker installed  
**Setup Time:** 10 minutes

```bash
# Build image
docker build -t ai-ticket-processor .

# Run once
docker run --env-file .env ai-ticket-processor

# Run continuously (every 5 min)
# Create docker-compose.yml:
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  processor:
    build: .
    env_file: .env
    volumes:
      - ./logs:/app/logs
    restart: always
```

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Option 3: Google Cloud Run (Production)

**Pros:** Auto-scaling, serverless, cheap  
**Cons:** Requires GCP account  
**Setup Time:** 15 minutes  
**Cost:** ~$5/month for 1000 tickets

### Setup:

```bash
# 1. Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# 2. Initialize
gcloud init
gcloud auth login

# 3. Create project
gcloud projects create ai-ticket-processor
gcloud config set project ai-ticket-processor

# 4. Build and deploy
gcloud builds submit --tag gcr.io/ai-ticket-processor/processor
gcloud run deploy processor \
  --image gcr.io/ai-ticket-processor/processor \
  --platform managed \
  --region us-central1 \
  --set-env-vars ZENDESK_SUBDOMAIN=yourcompany,ZENDESK_EMAIL=admin@company.com,ZENDESK_API_TOKEN=token,OPENAI_API_KEY=sk-key

# 5. Setup Cloud Scheduler (cron)
gcloud scheduler jobs create http ticket-processor \
  --schedule="*/5 * * * *" \
  --uri="https://YOUR_SERVICE_URL" \
  --http-method=POST
```

---

## Option 4: AWS Lambda (Serverless)

**Pros:** Pay per execution, highly scalable  
**Cons:** Complex setup  
**Setup Time:** 30 minutes  
**Cost:** ~$2/month for 1000 tickets

### Requirements:
- AWS Account
- AWS CLI installed
- Serverless Framework

```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless.yml
```

**serverless.yml:**
```yaml
service: ai-ticket-processor

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    ZENDESK_SUBDOMAIN: ${env:ZENDESK_SUBDOMAIN}
    ZENDESK_EMAIL: ${env:ZENDESK_EMAIL}
    ZENDESK_API_TOKEN: ${env:ZENDESK_API_TOKEN}
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}

functions:
  processor:
    handler: handler.lambda_handler
    timeout: 300
    events:
      - schedule: rate(5 minutes)
```

**handler.py:**
```python
import json
from ai_ticket_processor import process_batch

def lambda_handler(event, context):
    results = process_batch(limit=50)
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
```

```bash
# Deploy
serverless deploy
```

---

## Option 5: Heroku (Quick Deploy)

**Pros:** Very simple, free tier available  
**Cons:** Free tier has limits  
**Setup Time:** 10 minutes  
**Cost:** Free (with limits) or $7/month

```bash
# 1. Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Create app
heroku create ai-ticket-processor-YOUR-NAME

# 4. Add environment variables
heroku config:set ZENDESK_SUBDOMAIN=yourcompany
heroku config:set ZENDESK_EMAIL=admin@company.com
heroku config:set ZENDESK_API_TOKEN=your_token
heroku config:set OPENAI_API_KEY=sk-your-key

# 5. Create Procfile
echo "worker: python ai_ticket_processor.py --limit 50" > Procfile

# 6. Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main

# 7. Scale worker
heroku ps:scale worker=1

# 8. Setup scheduler (Heroku Scheduler add-on)
heroku addons:create scheduler:standard
heroku addons:open scheduler
# In UI: Add job "python ai_ticket_processor.py --limit 50" every 10 minutes
```

---

## Comparison Table

| Platform | Cost/Month | Setup | Scalability | Best For |
|----------|-----------|-------|-------------|----------|
| **Local** | $0 | Easy | Low | Testing |
| **Docker** | $0 | Medium | Medium | Dev/Prod |
| **GCP Run** | $5 | Medium | High | Production |
| **AWS Lambda** | $2 | Hard | Very High | Enterprise |
| **Heroku** | $0-7 | Easy | Medium | Quick Deploy |

---

## Monitoring & Alerts

### Option 1: Email Alerts (Simple)

Add to `ai_ticket_processor.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'alerts@yourcompany.com'
    msg['To'] = 'admin@yourcompany.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email', 'your-password')
        server.send_message(msg)

# Use in error handling
if results['failed'] > 0:
    send_alert('Ticket Processing Errors', f"{results['failed']} tickets failed")
```

### Option 2: Slack Alerts (Better)

```bash
pip install slack-sdk
```

```python
from slack_sdk import WebClient

slack = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

def send_slack_alert(message):
    slack.chat_postMessage(channel='#alerts', text=message)

# Use it
send_slack_alert(f"✅ Processed {results['processed']} tickets")
```

### Option 3: Monitoring Dashboard (Best)

Use tools like:
- **Grafana** - Free, open source
- **Datadog** - Paid, enterprise-grade
- **New Relic** - Free tier available

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   - Already in .gitignore
   - Use environment variables in production

2. **Rotate API keys regularly**
   - Every 90 days minimum
   - Immediately if compromised

3. **Use secrets management**
   - AWS Secrets Manager
   - GCP Secret Manager
   - HashiCorp Vault

4. **Enable HTTPS only**
   - Already enforced by APIs
   - Use secure webhooks

5. **Monitor API usage**
   - Set up billing alerts
   - Track unusual patterns

---

## 📊 Performance Tuning

### Increase Throughput

```python
# In ai_ticket_processor.py, reduce delay:
time.sleep(0.5)  # Instead of 1 second

# Or use parallel processing:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(process_single_ticket, ticket_ids)
```

### Reduce Costs

```python
# Use cheaper model for simple tickets
# In analyze_ticket.py:
"model": "gpt-3.5-turbo"  # $0.0005 per ticket

# Or use classification first:
# Only use AI for complex tickets
```

---

## 🎯 Next Steps After Deployment

1. **Monitor first 100 tickets** - Check accuracy
2. **Adjust prompts** if needed - Improve categorization
3. **Set up alerts** - Know when things break
4. **Scale gradually** - Start with 10/hour, then increase
5. **Measure ROI** - Track time/cost savings

---

**Questions about deployment?**
📧 madhan1787@gmail.com
📱 +91 9994151325
