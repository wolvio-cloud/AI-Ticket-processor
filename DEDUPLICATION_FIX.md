# 🔧 TICKET DEDUPLICATION FIX

## Problem Identified

The system is updating tickets multiple times with the same AI analysis, causing:
1. **Duplicate internal comments** on every run
2. **Redundant processing** of already-analyzed tickets
3. **Wasted API calls** to OpenAI (costs money)
4. **Potential webhook loops** if webhooks trigger on ticket.updated

## Root Causes

### 1. No Pre-Processing Check
```python
# Current code in process_ticket() - Line 286
def process_ticket(ticket, industry=None):
    ticket_id = ticket['id']
    description = ticket.get('description', '') or ticket.get('subject', '')

    # ❌ NO CHECK IF ALREADY PROCESSED!

    # Analyze with AI (wasted API call)
    ai_result = analyze_with_openai(description, industry=industry)

    # Update Zendesk (duplicate comment)
    update_result = update_ticket(ticket_id, ai_result["analysis"])
```

### 2. Always Adds Comment
```python
# Current code in update_ticket() - Line 258-269
# Always creates and adds comment, even if ticket was already processed
comment_body = f"""AI Analysis:

Summary: {analysis['summary']}
Root Cause: {analysis['root_cause']}
...
"""

payload = {
    "ticket": {
        "comment": {"body": comment_body, "public": False},  # ❌ ALWAYS ADDED
        "tags": all_tags,
        "priority": map_urgency_to_priority(analysis['urgency'])
    }
}
```

### 3. No Processing Timestamp
- Can't tell when ticket was last analyzed
- Can't implement "reprocess if older than X days" logic
- No version tracking for analysis

### 4. Batch Fetcher Gets All Tickets
```python
# Current code in main() - Line 325-335
# Fetches ALL tickets, not just unprocessed ones
url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/search.json"
params = {
    'query': 'type:ticket',  # ❌ Gets all tickets, including processed ones
    'sort_by': 'updated_at',
    'sort_order': 'desc'
}
```

## Solution: Comprehensive Deduplication

### Fix 1: Check Before Processing
```python
def is_ticket_already_processed(ticket):
    """
    Check if ticket was already processed by AI
    """
    tags = ticket.get('tags', [])

    # Check for ai_processed tag
    if 'ai_processed' in tags:
        return True

    return False

def process_ticket(ticket, industry=None, force=False):
    """
    Process one ticket through pipeline with deduplication

    Args:
        ticket: Ticket data from Zendesk
        industry: Optional industry override
        force: Force reprocessing even if already processed
    """
    ticket_id = ticket['id']
    description = ticket.get('description', '') or ticket.get('subject', '')

    if not description.strip():
        return {"ticket_id": ticket_id, "success": False, "error": "No description"}

    # ✅ CHECK IF ALREADY PROCESSED
    if not force and is_ticket_already_processed(ticket):
        logger.info(f"Ticket {ticket_id} already processed, skipping")
        return {
            "ticket_id": ticket_id,
            "success": True,
            "skipped": True,
            "reason": "already_processed"
        }

    logger.info(f"Processing ticket {ticket_id}")

    # Analyze with AI
    ai_result = analyze_with_openai(description, industry=industry)
    if not ai_result["success"]:
        return {**ai_result, "ticket_id": ticket_id, "updated": False}

    # Update Zendesk
    update_result = update_ticket(ticket_id, ai_result["analysis"], ticket)

    return {
        "ticket_id": ticket_id,
        "success": True,
        "skipped": False,
        "industry": ai_result.get("industry", "unknown"),
        "analysis": ai_result["analysis"],
        "processing_time": ai_result["processing_time"],
        "updated": update_result["updated"],
        "pii_protected": ai_result.get("pii_protected", False),
        "redactions": ai_result.get("redactions", {})
    }
```

### Fix 2: Only Add Comment If Not Already Processed
```python
def update_ticket(ticket_id, analysis, existing_ticket=None):
    """
    Update Zendesk ticket with AI analysis (idempotent)

    Args:
        ticket_id: Zendesk ticket ID
        analysis: AI analysis results
        existing_ticket: Optional pre-fetched ticket data to avoid extra API call
    """
    start = time.time()
    url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"

    try:
        # Fetch existing tags if not provided
        if existing_ticket is None:
            resp_get = session.get(url, auth=zendesk_auth, timeout=10)
            resp_get.raise_for_status()
            current_ticket = resp_get.json()['ticket']
        else:
            current_ticket = existing_ticket

        existing_tags = current_ticket.get('tags', [])

        # ✅ CHECK IF ALREADY HAS AI_PROCESSED TAG
        already_processed = 'ai_processed' in existing_tags

        # Create AI tags
        ai_tags = [
            "ai_processed",
            f"ai_{analysis['root_cause']}",
            f"ai_{analysis['urgency']}",
            f"ai_{analysis['sentiment']}"
        ]

        # Combine tags (remove old AI tags if reprocessing)
        # Remove old ai_* tags except ai_processed
        cleaned_tags = [tag for tag in existing_tags if not tag.startswith('ai_') or tag == 'ai_processed']
        all_tags = list(set(cleaned_tags + ai_tags))

        # Add processing timestamp tag
        timestamp = datetime.now().strftime('%Y%m%d')
        all_tags.append(f"ai_processed_{timestamp}")

        # Build payload
        payload = {
            "ticket": {
                "tags": all_tags,
                "priority": map_urgency_to_priority(analysis['urgency'])
            }
        }

        # ✅ ONLY ADD COMMENT IF NOT ALREADY PROCESSED
        if not already_processed:
            comment_body = f"""🤖 AI Analysis (Automated):

📋 Summary: {analysis['summary']}
🔍 Root Cause: {analysis['root_cause']}
⚡ Urgency: {analysis['urgency']}
😊 Sentiment: {analysis['sentiment']}

---
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            payload["ticket"]["comment"] = {"body": comment_body, "public": False}
            logger.info(f"Adding AI analysis comment to ticket {ticket_id}")
        else:
            logger.info(f"Ticket {ticket_id} already has AI analysis, updating tags only")

        # Update ticket
        resp_put = session.put(url, json=payload, auth=zendesk_auth, timeout=10)
        resp_put.raise_for_status()

        logger.info(f"Ticket {ticket_id} updated with tags: {ai_tags}")
        return {
            "updated": True,
            "time": round(time.time() - start, 2),
            "comment_added": not already_processed
        }

    except Exception as e:
        logger.error(f"Zendesk update failed (ID {ticket_id}): {e}")
        return {"updated": False, "error": str(e), "time": round(time.time() - start, 2)}
```

### Fix 3: Fetch Only Unprocessed Tickets
```python
def main(limit=50, industry=None, force=False, only_unprocessed=True):
    """
    Main processing function with deduplication

    Args:
        limit: Max number of tickets to process
        industry: Force specific industry
        force: Force reprocessing of already-processed tickets
        only_unprocessed: Only fetch tickets without ai_processed tag
    """
    start_total = time.time()

    logger.info(f"Starting batch processing (limit: {limit}, industry: {industry or 'auto-detect'}, force: {force})")
    print(f"AI TICKET PROCESSOR - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Fetch tickets
    url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/search.json"

    # ✅ FETCH ONLY UNPROCESSED TICKETS BY DEFAULT
    if only_unprocessed and not force:
        # Exclude tickets with ai_processed tag
        query = 'type:ticket -tags:ai_processed'
        logger.info("Fetching only unprocessed tickets")
    else:
        query = 'type:ticket'
        logger.info("Fetching all tickets")

    params = {
        'query': query,
        'sort_by': 'created_at',  # Process oldest first
        'sort_order': 'asc'
    }

    try:
        resp = session.get(url, params=params, auth=zendesk_auth, timeout=10)
        resp.raise_for_status()
        tickets = resp.json()['results'][:limit]

        if not tickets:
            print("\n✅ No unprocessed tickets found!")
            logger.info("No tickets to process")
            return

        print(f"Successfully fetched {len(tickets)} tickets\n")
    except Exception as e:
        logger.critical(f"Failed to fetch tickets: {e}")
        print(f"ERROR: Failed to fetch tickets - {e}")
        return

    # Process tickets
    results = []
    skipped = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_ticket, ticket, industry, force): ticket for ticket in tickets}

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)

            # Track skipped tickets
            if result.get("skipped"):
                skipped += 1
                status = "SKIPPED (already processed)"
            else:
                status = "SUCCESS" if result.get("success") else "FAILED"

            detected_industry = result.get("industry", "unknown")
            print(f"[{i}/{len(tickets)}] Ticket #{result['ticket_id']} ({detected_industry}): {status}")

    # Calculate statistics
    total_time = round(time.time() - start_total, 2)
    success = sum(1 for r in results if r.get("success") and not r.get("skipped"))
    failed = sum(1 for r in results if not r.get("success"))

    # ... rest of stats calculation

    # Print summary
    print("\n" + "="*60)
    print("BATCH PROCESSING COMPLETE")
    print("="*60)
    print(f"Total Tickets:    {len(tickets)}")
    print(f"Processed:        {success}")
    print(f"Skipped:          {skipped} (already processed)")
    print(f"Failed:           {failed}")
    print(f"Total Time:       {total_time}s ({total_time/60:.1f} minutes)")

    # ... rest of summary
```

### Fix 4: Add Force Reprocess Flag
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Ticket Processor - Multi-Industry')
    parser.add_argument("--limit", type=int, default=50, help="Number of tickets to process")
    parser.add_argument("--industry", type=str, choices=['ecommerce', 'saas', 'general'],
                       help="Force specific industry (optional, auto-detects if not specified)")
    parser.add_argument("--force", action="store_true",
                       help="Force reprocessing of already-processed tickets")
    parser.add_argument("--all", action="store_true",
                       help="Process all tickets including already processed ones")
    args = parser.parse_args()

    main(args.limit, args.industry, force=args.force, only_unprocessed=not args.all)
```

## Usage Examples

### Process only new tickets (default)
```bash
python Ai_ticket_processor.py --limit 50
# Output: Only processes tickets without ai_processed tag
```

### Force reprocess all tickets
```bash
python Ai_ticket_processor.py --limit 50 --force
# Output: Reprocesses all tickets, updates tags only (no duplicate comments)
```

### Process all tickets including processed ones
```bash
python Ai_ticket_processor.py --limit 100 --all
# Output: Fetches all tickets but skips already processed ones
```

## Webhook Loop Prevention

### Fix 5: Ignore Our Own Updates
```python
@router.post("/webhooks/zendesk")
async def zendesk_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Zendesk webhook endpoint with loop prevention
    """
    body = await request.body()
    signature = request.headers.get("X-Zendesk-Webhook-Signature")

    if not validate_zendesk_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("type")
    ticket_data = payload.get("ticket")

    # ✅ IGNORE IF TICKET ALREADY HAS AI_PROCESSED TAG
    if "ai_processed" in ticket_data.get("tags", []):
        logger.info(f"Ignoring webhook for already-processed ticket {ticket_data.get('id')}")
        return {"status": "ignored", "reason": "already_processed"}

    # ✅ IGNORE ticket.updated EVENTS TRIGGERED BY OUR OWN UPDATES
    # Check if the update was made by our system
    updater_id = payload.get("updater_id")
    our_user_id = os.getenv("ZENDESK_USER_ID")  # Set this in .env

    if event_type == "ticket.updated" and updater_id == our_user_id:
        logger.info(f"Ignoring self-triggered update for ticket {ticket_data.get('id')}")
        return {"status": "ignored", "reason": "self_update"}

    # Filter relevant events
    if event_type not in ["ticket.created", "ticket.updated"]:
        return {"status": "ignored", "reason": "event_type_not_supported"}

    # Queue for async processing
    background_tasks.add_task(
        WebhookProcessor.process_ticket_event,
        ticket_data,
        event_type
    )

    return {"status": "queued", "ticket_id": ticket_data.get("id")}
```

## Database-Based Deduplication (Advanced)

For enterprise use with FastAPI backend:

```python
# models.py
class TicketProcessingRecord(Base):
    __tablename__ = "ticket_processing_records"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, index=True, unique=True)
    first_processed_at = Column(DateTime, server_default=func.now())
    last_processed_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    processing_count = Column(Integer, default=1)
    analysis_hash = Column(String(64))  # SHA256 of analysis to detect changes

    __table_args__ = (
        Index('idx_ticket_id_processed', 'ticket_id', 'last_processed_at'),
    )

# services/ticket_processor.py
def should_process_ticket(db: Session, ticket_id: str, current_analysis_hash: str) -> bool:
    """
    Check if ticket should be processed based on database record
    """
    record = db.query(TicketProcessingRecord).filter(
        TicketProcessingRecord.ticket_id == ticket_id
    ).first()

    if not record:
        # Never processed before
        return True

    # Check if analysis would be different
    if record.analysis_hash != current_analysis_hash:
        # Ticket content changed, reprocess
        return True

    # Check if processed too long ago (e.g., 30 days)
    cutoff = datetime.now() - timedelta(days=30)
    if record.last_processed_at < cutoff:
        return True

    return False

def mark_ticket_processed(db: Session, ticket_id: str, analysis_hash: str):
    """
    Record ticket processing in database
    """
    record = db.query(TicketProcessingRecord).filter(
        TicketProcessingRecord.ticket_id == ticket_id
    ).first()

    if record:
        record.processing_count += 1
        record.last_processed_at = datetime.now()
        record.analysis_hash = analysis_hash
    else:
        record = TicketProcessingRecord(
            ticket_id=ticket_id,
            analysis_hash=analysis_hash
        )
        db.add(record)

    db.commit()
```

## Testing

### Test 1: Verify No Duplicates
```bash
# Run twice in a row
python Ai_ticket_processor.py --limit 10
python Ai_ticket_processor.py --limit 10

# Expected: Second run should say "No unprocessed tickets found!"
```

### Test 2: Verify Force Reprocess
```bash
# Force reprocess
python Ai_ticket_processor.py --limit 10 --force

# Expected: Reprocesses all tickets but doesn't add duplicate comments
```

### Test 3: Check Zendesk Tickets
```bash
# Verify in Zendesk UI:
# - Each ticket should have only ONE AI analysis comment
# - Tags should be updated correctly
# - No duplicate comments
```

## Benefits

✅ **Eliminates duplicate comments**
✅ **Saves OpenAI API costs** (no redundant processing)
✅ **Faster batch processing** (skips already-processed tickets)
✅ **Prevents webhook loops**
✅ **Supports force reprocessing** when needed
✅ **Timestamp tracking** for audit trail
✅ **Database-backed** deduplication for enterprise

## Migration Note

If you already have tickets with duplicate comments, you can:
1. Manually clean them up in Zendesk (delete duplicate comments)
2. Or leave them (they won't get more duplicates going forward)
3. The fix prevents future duplicates

## Estimated Impact

**Before Fix:**
- 100 tickets processed → 100 OpenAI API calls → $0.10
- Run 5 times → 500 API calls → $0.50 (wasted)
- 500 duplicate comments in Zendesk

**After Fix:**
- 100 tickets processed → 100 OpenAI API calls → $0.10
- Run 5 times → 100 API calls → $0.10 (no waste)
- 100 comments total (no duplicates)

**Savings:** 80% cost reduction on repeated runs
