"""
ai_ticket_processor.py - Multi-Industry Version
FIXED: 82% "Other" problem with industry-specific prompts
"""
import requests
import os
import json
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import argparse
from dotenv import load_dotenv
from pii_redactor import PIIRedactor

# Load environment variables
load_dotenv()

# Initialize PII Redactor
redactor = PIIRedactor(preserve_emails=True)

# === CONFIG ===
SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
EMAIL = os.getenv('ZENDESK_EMAIL')
TOKEN = os.getenv('ZENDESK_API_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Retry Session
def requests_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = requests_session()

# === AUTH ===
zendesk_auth = (f"{EMAIL}/token", TOKEN)
openai_headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

# === INDUSTRY DETECTION ===
def detect_industry(description):
    """Auto-detect industry based on keywords in ticket"""
    desc_lower = description.lower()
    
    # E-commerce keywords
    ecommerce_keywords = ['order', 'delivery', 'shipping', 'refund', 'product', 'return', 
                          'exchange', 'tracking', 'package', 'checkout', 'cart', 'payment declined']
    
    # SaaS keywords
    saas_keywords = ['login', 'api', 'integration', 'bug', 'error', 'feature', 'subscription', 
                     'account', 'dashboard', 'sync', 'webhook', 'endpoint', 'authentication']
    
    # Count matches
    ecommerce_score = sum(1 for kw in ecommerce_keywords if kw in desc_lower)
    saas_score = sum(1 for kw in saas_keywords if kw in desc_lower)
    
    # Return industry with highest score
    if ecommerce_score > saas_score and ecommerce_score > 0:
        return 'ecommerce'
    elif saas_score > ecommerce_score and saas_score > 0:
        return 'saas'
    else:
        return 'general'

# === INDUSTRY-SPECIFIC PROMPTS ===
PROMPTS = {
    'ecommerce': """
You are a senior e-commerce support analyst. Analyze this ticket and return ONLY valid JSON.

Ticket: {description}

{{
  "summary": "1-sentence summary of the issue",
  "root_cause": "delivery_issue|product_defect|payment_failed|refund_request|order_cancellation|wrong_item|account_help|return_exchange|promo_code|tracking_inquiry|general",
  "urgency": "low|medium|high",
  "sentiment": "positive|neutral|negative"
}}

Category Definitions:
- delivery_issue: Late delivery, damaged in transit, not delivered, lost package
- product_defect: Broken, damaged, not as described, quality issue
- payment_failed: Payment declined, charge error, refund not received
- refund_request: Customer wants money back
- order_cancellation: Cancel before or after shipping
- wrong_item: Received different product than ordered
- account_help: Login, password, profile, account issues
- return_exchange: Want to return or exchange item
- promo_code: Discount code not working
- tracking_inquiry: Where is my order, tracking number questions
- general: Doesn't fit any other category

Choose the MOST SPECIFIC category. Only use "general" if truly doesn't fit others.
""",
    
    'saas': """
You are a senior SaaS support analyst. Analyze this ticket and return ONLY valid JSON.

Ticket: {description}

{{
  "summary": "1-sentence summary of the issue",
  "root_cause": "login_issue|bug_report|feature_request|integration_error|billing_question|performance_slow|api_error|data_sync|account_setup|user_management|general",
  "urgency": "low|medium|high|critical",
  "sentiment": "positive|neutral|negative"
}}

Category Definitions:
- login_issue: Can't login, forgot password, SSO problems, 2FA issues
- bug_report: Something broken, error messages, unexpected behavior
- feature_request: Want new functionality, enhancement ideas
- integration_error: Third-party integration not working (Slack, Zapier, etc)
- billing_question: Subscription, invoices, payment, plan changes
- performance_slow: App is slow, loading issues, timeout errors
- api_error: API calls failing, rate limits, authentication errors
- data_sync: Data not syncing, missing data, sync delays
- account_setup: Onboarding help, initial setup, configuration
- user_management: Adding/removing users, permissions, roles
- general: Doesn't fit any other category

Choose the MOST SPECIFIC category. Only use "general" if truly doesn't fit others.
""",
    
    'general': """
You are a senior support analyst. Analyze this ticket and return ONLY valid JSON.

Ticket: {description}

{{
  "summary": "1-sentence summary",
  "root_cause": "technical|billing|account|inquiry|other",
  "urgency": "low|medium|high",
  "sentiment": "positive|neutral|negative"
}}

Categories:
- technical: Any technical issue, bug, or error
- billing: Payment, subscription, refund issues
- account: Login, profile, account management
- inquiry: Questions, how-to, general information
- other: Truly doesn't fit above
"""
}

# === PRIORITY MAPPING ===
def map_urgency_to_priority(urgency):
    """Map AI urgency to Zendesk priority"""
    mapping = {
        'low': 'low',
        'medium': 'normal',
        'high': 'high',
        'critical': 'urgent'
    }
    return mapping.get(urgency, 'normal')

# === OPENAI ANALYSIS ===
def analyze_with_openai(description, industry=None):
    """Analyze ticket with industry-specific prompt"""
    start = time.time()
    
    # Auto-detect industry if not provided
    if industry is None:
        industry = detect_industry(description)
    
    logger.info(f"Detected industry: {industry}")
    
    # STEP 1: Redact PII
    redaction_result = redactor.redact(description)
    clean_description = redaction_result['redacted_text']
    
    if redaction_result['has_pii']:
        logger.warning(f"[PII] Detected and redacted: {redaction_result['redactions']}")
    
    # STEP 2: Select industry-specific prompt
    prompt_template = PROMPTS.get(industry, PROMPTS['general'])
    
    # STEP 3: Send to OpenAI
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt_template.format(description=clean_description)}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        resp = session.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=openai_headers,
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()
        analysis = json.loads(result['choices'][0]['message']['content'])
        
        return {
            "success": True,
            "analysis": analysis,
            "industry": industry,
            "processing_time": round(time.time() - start, 2),
            "pii_protected": redaction_result['has_pii'],
            "redactions": redaction_result['redactions']
        }
    except Exception as e:
        logger.error(f"OpenAI failed: {e}")
        return {
            "success": False, 
            "error": str(e), 
            "processing_time": round(time.time() - start, 2)
        }

# === ZENDESK UPDATE ===
def update_ticket(ticket_id, analysis):
    """Update Zendesk ticket with AI analysis"""
    start = time.time()
    url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"
    
    try:
        # Fetch existing tags
        resp_get = session.get(url, auth=zendesk_auth, timeout=10)
        resp_get.raise_for_status()
        current_ticket = resp_get.json()['ticket']
        existing_tags = current_ticket.get('tags', [])
        
        # Create AI tags
        ai_tags = [
            "ai_processed",
            f"ai_{analysis['root_cause']}",
            f"ai_{analysis['urgency']}",
            f"ai_{analysis['sentiment']}"
        ]
        
        # Combine tags
        all_tags = list(set(existing_tags + ai_tags))
        
        # Create comment
        comment_body = f"""AI Analysis:

Summary: {analysis['summary']}
Root Cause: {analysis['root_cause']}
Urgency: {analysis['urgency']}
Sentiment: {analysis['sentiment']}
"""
        
        # Update ticket
        payload = {
            "ticket": {
                "comment": {"body": comment_body, "public": False},
                "tags": all_tags,
                "priority": map_urgency_to_priority(analysis['urgency'])
            }
        }
        
        resp_put = session.put(url, json=payload, auth=zendesk_auth, timeout=10)
        resp_put.raise_for_status()
        
        logger.info(f"Ticket {ticket_id} updated with tags: {ai_tags}")
        return {"updated": True, "time": round(time.time() - start, 2)}
        
    except Exception as e:
        logger.error(f"Zendesk update failed (ID {ticket_id}): {e}")
        return {"updated": False, "error": str(e), "time": round(time.time() - start, 2)}

# === PROCESS TICKET ===
def process_ticket(ticket, industry=None):
    """Process one ticket through pipeline"""
    ticket_id = ticket['id']
    description = ticket.get('description', '') or ticket.get('subject', '')
    
    if not description.strip():
        return {"ticket_id": ticket_id, "success": False, "error": "No description"}
    
    logger.info(f"Processing ticket {ticket_id}")
    
    # Analyze with AI
    ai_result = analyze_with_openai(description, industry=industry)
    if not ai_result["success"]:
        return {**ai_result, "ticket_id": ticket_id, "updated": False}
    
    # Update Zendesk
    update_result = update_ticket(ticket_id, ai_result["analysis"])
    
    return {
        "ticket_id": ticket_id,
        "success": True,
        "industry": ai_result.get("industry", "unknown"),
        "analysis": ai_result["analysis"],
        "processing_time": ai_result["processing_time"],
        "updated": update_result["updated"],
        "pii_protected": ai_result.get("pii_protected", False),
        "redactions": ai_result.get("redactions", {})
    }

# === MAIN ===
def main(limit=50, industry=None):
    """Main processing function"""
    start_total = time.time()
    
    logger.info(f"Starting batch processing (limit: {limit}, industry: {industry or 'auto-detect'})")
    print(f"AI TICKET PROCESSOR - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Fetch tickets
    url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/search.json"
    params = {
        'query': 'type:ticket',
        'sort_by': 'updated_at',
        'sort_order': 'desc'
    }
    
    try:
        resp = session.get(url, params=params, auth=zendesk_auth, timeout=10)
        resp.raise_for_status()
        tickets = resp.json()['results'][:limit]
        print(f"Successfully fetched {len(tickets)} tickets\n")
    except Exception as e:
        logger.critical(f"Failed to fetch tickets: {e}")
        print(f"ERROR: Failed to fetch tickets - {e}")
        return
    
    # Process tickets
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_ticket, ticket, industry): ticket for ticket in tickets}
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            
            status = "SUCCESS" if result.get("success") else "FAILED"
            detected_industry = result.get("industry", "unknown")
            print(f"[{i}/{len(tickets)}] Ticket #{result['ticket_id']} ({detected_industry}): {status}")
    
    # Calculate statistics
    total_time = round(time.time() - start_total, 2)
    success = sum(1 for r in results if r.get("success"))
    failed = len(tickets) - success
    avg_time = round(sum(r.get("processing_time", 0) for r in results) / len(results), 2) if results else 0
    
    # PII stats
    tickets_with_pii = sum(1 for r in results if r.get("pii_protected", False))
    total_redactions = {}
    for r in results:
        for pii_type, count in r.get("redactions", {}).items():
            total_redactions[pii_type] = total_redactions.get(pii_type, 0) + count
    
    # Industry breakdown
    industry_counts = {}
    for r in results:
        if r.get('success'):
            ind = r.get('industry', 'unknown')
            industry_counts[ind] = industry_counts.get(ind, 0) + 1
    
    # Category breakdown (check for "general"/"other")
    category_counts = {}
    other_count = 0
    for r in results:
        if r.get('success'):
            cat = r['analysis']['root_cause']
            category_counts[cat] = category_counts.get(cat, 0) + 1
            if cat in ['other', 'general']:
                other_count += 1
    
    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total": len(tickets),
        "processed": success,
        "failed": failed,
        "avg_time_per_ticket": avg_time,
        "total_time": total_time,
        "cost_estimate": round(len(tickets) * 0.001, 3),
        "pii_protection": {
            "tickets_with_pii": tickets_with_pii,
            "total_redactions": sum(total_redactions.values()),
            "by_type": total_redactions
        },
        "industry_breakdown": industry_counts,
        "category_breakdown": category_counts,
        "other_percentage": round(other_count/len(results)*100, 1) if results else 0,
        "results": results
    }
    
    # Print summary
    print("\n" + "="*60)
    print("BATCH PROCESSING COMPLETE")
    print("="*60)
    print(f"Total Tickets:    {len(tickets)}")
    print(f"Processed:        {success}")
    print(f"Failed:           {failed}")
    print(f"Avg Time:         {avg_time}s per ticket")
    print(f"Total Time:       {total_time}s ({total_time/60:.1f} minutes)")
    print(f"Cost Estimate:    ${summary['cost_estimate']}")
    
    print("\n" + "="*60)
    print("INDUSTRY BREAKDOWN")
    print("="*60)
    for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{industry}: {count} ({count/len(results)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("CATEGORY BREAKDOWN")
    print("="*60)
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        emoji = "⚠️" if category in ['other', 'general'] else "✅"
        print(f"{emoji} {category}: {count} ({count/len(results)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("🎯 'OTHER' CATEGORY RATE")
    print("="*60)
    other_pct = summary['other_percentage']
    if other_pct < 15:
        status = "✅ EXCELLENT"
    elif other_pct < 25:
        status = "✓ GOOD"
    elif other_pct < 40:
        status = "⚠️ NEEDS IMPROVEMENT"
    else:
        status = "❌ POOR"
    print(f"Other/General: {other_count}/{len(results)} tickets ({other_pct}%)")
    print(f"Status: {status}")
    print(f"Target: <15% (Excellent), <25% (Good)")
    
    print("\n" + "="*60)
    print("PII PROTECTION SUMMARY")
    print("="*60)
    print(f"Tickets with PII: {tickets_with_pii}")
    print(f"Total Redactions: {sum(total_redactions.values())}")
    if total_redactions:
        for pii_type, count in total_redactions.items():
            print(f"  - {pii_type}: {count}")
    else:
        print("  No PII detected")
    print("="*60)
    
    # Save results
    json_file = f"{LOG_DIR}/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nResults saved to: {json_file}")
    logger.info(f"Batch complete: {success}/{len(tickets)} | Avg: {avg_time}s | Other%: {other_pct}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Ticket Processor - Multi-Industry')
    parser.add_argument("--limit", type=int, default=50, help="Number of tickets to process")
    parser.add_argument("--industry", type=str, choices=['ecommerce', 'saas', 'general'], 
                       help="Force specific industry (optional, auto-detects if not specified)")
    args = parser.parse_args()
    
    main(args.limit, args.industry)