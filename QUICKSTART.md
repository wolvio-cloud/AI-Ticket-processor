# 🚀 QUICK START - 5 MINUTES TO LAUNCH

## Step 1: Setup (2 minutes)

```bash
# Run setup script
./setup.sh

# OR manually:
pip install -r requirements.txt
cp .env.example .env
mkdir -p logs
```

## Step 2: Configure API Keys (2 minutes)

Edit `.env` file:

```env
ZENDESK_SUBDOMAIN=yourcompany        # Just the subdomain, not full URL
ZENDESK_EMAIL=admin@yourcompany.com  # Your Zendesk admin email
ZENDESK_API_TOKEN=your_token_here    # From Zendesk Settings > API
OPENAI_API_KEY=sk-proj-xxxxx         # From platform.openai.com
LOG_LEVEL=INFO
```

### Getting Your API Keys:

**Zendesk:**
1. Go to Zendesk Admin → API → Token Access
2. Enable it and create new token
3. Copy the token immediately (you can't see it again!)

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy it (starts with `sk-`)

## Step 3: Test Everything (1 minute)

```bash
# Run comprehensive test
python test_system.py
```

If all tests pass ✅, you're ready!

## Step 4: Process Your First Tickets!

```bash
# Process 5 tickets
python ai_ticket_processor.py --limit 5

# Process specific ticket
python ai_ticket_processor.py --ticket-id 12345

# Process 50 tickets
python ai_ticket_processor.py --limit 50
```

---

## 🎯 Common Commands

```bash
# Test Zendesk only
python fetch_tickets.py

# Test OpenAI only
python analyze_ticket.py

# Full system test
python test_system.py

# Process tickets
python ai_ticket_processor.py --limit 10

# Check logs
tail -f logs/processor.log
```

---

## 🐛 Troubleshooting

### "401 Unauthorized" Error

**For Zendesk:**
- Check subdomain doesn't include "https://" or ".zendesk.com"
- Just use: `yourcompany`
- Verify email matches token owner

**For OpenAI:**
- Key should start with `sk-`
- Check you have credit in your account
- Try regenerating the key

### "No tickets fetched"

- Check you have tickets in Zendesk
- Try processing a specific ticket ID: `--ticket-id 12345`

### "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 🔄 Automate It (Cron Job)

Run every 5 minutes:

```bash
crontab -e

# Add this line:
*/5 * * * * cd /path/to/ai-ticket-processor-v2 && python ai_ticket_processor.py --limit 50 >> logs/cron.log 2>&1
```

---

## 📊 What Gets Logged

- All processing in `logs/processor.log`
- Results saved to `logs/results_TIMESTAMP.json`
- You can analyze these later for insights

---

## 💰 Cost Breakdown

**OpenAI (gpt-4o-mini):**
- ~$0.001 per ticket
- 1,000 tickets = ~$1.00
- 10,000 tickets = ~$10.00

**ROI Example:**
- Manual: 5 min/ticket × $50/hr = $4.17/ticket
- AI: $0.001/ticket
- **Savings: 99.98% ($4.169 per ticket)**

---

## 🎉 YOU'RE DONE!

Your AI Ticket Processor is now running!

Questions? Issues? 
📧 madhan1787@gmail.com
📱 +91 9994151325
