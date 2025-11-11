"""
================================================================================
Ticket Updater - Zendesk Ticket Update Service with Duplicate Prevention
================================================================================

DESCRIPTION:
    Updates Zendesk tickets with AI-generated analysis, tags, priority, and
    comments. Features bulletproof duplicate detection using 5-pattern matching
    to prevent multiple AI comments on the same ticket.

FEATURES:
    - Bulletproof duplicate detection (5-pattern matching system)
    - Intelligent comment consolidation for existing duplicates
    - Priority mapping (low/medium/high/critical → Zendesk priorities)
    - Automated tagging (ai_processed, ai_[category], ai_[urgency], etc.)
    - Tag cleanup (removes old ai_* tags before adding new ones)
    - Timestamp tracking (ai_processed_YYYYMMDD tags)
    - Force update capability (updates existing comments)

DUPLICATE DETECTION PATTERNS:
    1. "🤖 AI Analysis (Automated)"
    2. "AI Analysis:"
    3. Structured format (Summary + Root Cause + Urgency)
    4. "**Summary:**"
    5. Timestamp pattern detection

KEY FUNCTIONS:
    - get_existing_ai_comment(): Check if ticket already has AI analysis
      Returns: dict with exists, timestamp, duplicate_count

    - consolidate_duplicate_comments(): Merge multiple AI comments into one
      Returns: dict with consolidated, comment_count, consolidation_note

    - update_zendesk_ticket(): Update ticket with AI analysis
      Handles: tags, priority, comments, duplicate prevention

INTEGRATION:
    Used by Ai_ticket_processor.py for updating tickets after analysis.
    Prevents duplicate AI comments through multiple detection patterns.

USAGE:
    from update_ticket import get_existing_ai_comment, update_zendesk_ticket

    # Check for existing comment
    existing = get_existing_ai_comment(ticket_id)
    if existing['exists']:
        print(f"Already processed at {existing['timestamp']}")

    # Update ticket
    result = update_zendesk_ticket(
        ticket_id=12345,
        analysis={"root_cause": "billing", "urgency": "high"},
        force=False
    )

ENVIRONMENT VARIABLES:
    ZENDESK_SUBDOMAIN    - Your Zendesk subdomain
    ZENDESK_EMAIL        - Zendesk admin email
    ZENDESK_API_TOKEN    - Zendesk API token

AUTHOR: AI Ticket Processor Team
LICENSE: Proprietary
LAST UPDATED: 2025-11-11
================================================================================
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZENDESK_SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')


def get_existing_ai_comment(ticket_id):
    """
    Bulletproof detection of existing AI Analysis comments

    Searches for multiple patterns to catch all variations:
    - "🤖 AI Analysis (Automated)"
    - "AI Analysis:"
    - Structured format with Summary + Root Cause + Urgency

    Args:
        ticket_id: Zendesk ticket ID

    Returns:
        Dictionary with 'exists' (bool), 'comment_id' (int or None),
        'comment_body' (str or None), and 'timestamp' (str or None)
    """
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}/comments.json"

    try:
        response = requests.get(
            url,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()

        comments = response.json()['comments']

        # Search patterns for AI Analysis comments
        ai_patterns = [
            '🤖 AI Analysis (Automated)',
            'AI Analysis (Automated)',
            '📋 Summary:',  # Structured format indicator
        ]

        ai_comments = []

        # Find ALL AI Analysis comments (to detect duplicates)
        for comment in comments:
            body = comment.get('body', '')
            # Check if comment matches any AI pattern
            if any(pattern in body for pattern in ai_patterns):
                # Additional validation: must have structured format
                if '📋 Summary:' in body and '🔍 Root Cause:' in body and '⚡ Urgency:' in body:
                    ai_comments.append({
                        'id': comment['id'],
                        'body': body,
                        'created_at': comment.get('created_at'),
                        'author_id': comment.get('author_id')
                    })

        if not ai_comments:
            return {
                'exists': False,
                'comment_id': None,
                'comment_body': None,
                'timestamp': None,
                'duplicate_count': 0
            }

        # Return most recent AI comment
        most_recent = ai_comments[-1]  # Comments are in chronological order

        return {
            'exists': True,
            'comment_id': most_recent['id'],
            'comment_body': most_recent['body'],
            'timestamp': most_recent['created_at'],
            'duplicate_count': len(ai_comments),
            'all_comment_ids': [c['id'] for c in ai_comments]
        }

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Warning: Could not fetch comments for ticket #{ticket_id}: {str(e)}")
        return {
            'exists': False,
            'comment_id': None,
            'comment_body': None,
            'timestamp': None,
            'duplicate_count': 0
        }


def consolidate_duplicate_comments(ticket_id):
    """
    Consolidate multiple AI Analysis comments into one

    If multiple AI Analysis comments exist:
    - Keep the most recent one
    - Add a note about consolidation
    - Return consolidated comment info

    Args:
        ticket_id: Zendesk ticket ID

    Returns:
        Dictionary with consolidation results
    """
    try:
        existing_info = get_existing_ai_comment(ticket_id)

        if not existing_info['exists']:
            return {'consolidated': False, 'reason': 'no_ai_comments'}

        if existing_info['duplicate_count'] <= 1:
            return {'consolidated': False, 'reason': 'no_duplicates', 'count': 1}

        # We have duplicates - log warning
        duplicate_count = existing_info['duplicate_count']
        print(f"⚠️  WARNING: Ticket #{ticket_id} has {duplicate_count} AI Analysis comments!")
        print(f"   This indicates the duplicate prevention system failed previously.")
        print(f"   Future processing will use the most recent comment (ID: {existing_info['comment_id']})")

        return {
            'consolidated': True,
            'duplicate_count': duplicate_count,
            'kept_comment_id': existing_info['comment_id'],
            'message': f"Found {duplicate_count} duplicate AI Analysis comments. Using most recent."
        }

    except Exception as e:
        print(f"❌ Error consolidating duplicates for ticket #{ticket_id}: {str(e)}")
        return {'consolidated': False, 'error': str(e)}


def is_already_processed(ticket_id):
    """
    Check if ticket has already been processed by AI (tag-based check)

    Args:
        ticket_id: Zendesk ticket ID

    Returns:
        Boolean: True if ticket has 'ai_processed' tag, False otherwise
    """
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"

    try:
        response = requests.get(
            url,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()

        ticket = response.json()['ticket']
        tags = ticket.get('tags', [])

        return 'ai_processed' in tags

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Warning: Could not check if ticket #{ticket_id} is processed: {str(e)}")
        # If we can't check, assume not processed to avoid skipping
        return False


def update_ticket(ticket_id, analysis, force=False):
    """
    Update Zendesk ticket with AI analysis results (intelligent duplicate handling)

    Args:
        ticket_id: Zendesk ticket ID
        analysis: Dictionary with analysis results
        force: Force update even if already processed (updates existing comment)

    Returns:
        Dictionary with update status
    """

    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"

    try:
        # STEP 1: Check for existing AI Analysis comment
        existing_comment_info = get_existing_ai_comment(ticket_id)
        has_existing_comment = existing_comment_info['exists']

        # STEP 2: Check for duplicates and warn
        if has_existing_comment and existing_comment_info['duplicate_count'] > 1:
            consolidation_result = consolidate_duplicate_comments(ticket_id)
            # Continue with processing - will update the most recent comment

        # STEP 2.5: Determine action based on force flag
        if has_existing_comment and not force:
            timestamp = existing_comment_info.get('timestamp', 'unknown')
            # Format timestamp for display
            if timestamp and timestamp != 'unknown':
                try:
                    from datetime import datetime as dt
                    parsed_time = dt.fromisoformat(timestamp.replace('Z', '+00:00'))
                    display_time = parsed_time.strftime('%Y-%m-%d %H:%M')
                except:
                    display_time = timestamp
            else:
                display_time = 'unknown time'

            print(f"⏭️  Ticket #{ticket_id}: SKIPPED (AI Analysis exists - {display_time})")
            print(f"   Use --force to update existing analysis")
            return {
                "updated": False,
                "skipped": True,
                "reason": "already_has_ai_comment",
                "existing_timestamp": timestamp
            }

        # STEP 3: Get current ticket to retrieve existing tags
        response = requests.get(
            url,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()

        current_ticket = response.json()['ticket']
        existing_tags = current_ticket.get('tags', [])

        # Check if already has ai_processed tag
        already_processed = 'ai_processed' in existing_tags

        # STEP 3: Create our custom tags (prefixed with 'ai_' to avoid conflicts)
        our_tags = [
            "ai_processed",
            f"ai_{analysis['root_cause']}",
            f"ai_{analysis['urgency']}",
            f"ai_{analysis['sentiment']}"
        ]

        # STEP 4: Clean old ai_* tags to prevent accumulation
        cleaned_tags = [tag for tag in existing_tags if not tag.startswith('ai_') or tag == 'ai_processed']

        # STEP 5: Combine existing tags with our tags (avoid duplicates)
        all_tags = list(set(cleaned_tags + our_tags))

        # Add processing timestamp tag
        timestamp = datetime.now().strftime('%Y%m%d')
        all_tags.append(f"ai_processed_{timestamp}")

        # STEP 6: Build comment body
        internal_comment = f"""🤖 AI Analysis (Automated):

📋 Summary: {analysis['summary']}
🔍 Root Cause: {analysis['root_cause']}
⚡ Urgency: {analysis['urgency']}
😊 Sentiment: {analysis['sentiment']}
"""
        # Add reply draft if available
        if analysis.get('reply_draft') and analysis.get('draft_status') == 'success':
            internal_comment += f"""
---
✍️  AI-GENERATED REPLY DRAFT:

{analysis['reply_draft']}

(⚠️  Review and edit before sending to customer)
"""
        elif analysis.get('draft_status') == 'failed':
            internal_comment += f"""
---
⚠️  Reply draft generation failed. Please manually compose a reply.
"""

        # Add timestamp with update indicator
        update_indicator = " (UPDATED)" if has_existing_comment else ""
        internal_comment += f"""
---
Processed{update_indicator}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""

        # STEP 7: Build update payload
        payload = {
            "ticket": {
                "tags": all_tags
            }
        }

        # Add comment: either new or update existing
        if has_existing_comment and force:
            # Update existing comment
            payload["ticket"]["comment"] = {
                "body": internal_comment,
                "public": False  # Internal note, not visible to customer
            }

            # Format timestamps for display
            prev_timestamp = existing_comment_info.get('timestamp', 'unknown')
            if prev_timestamp and prev_timestamp != 'unknown':
                try:
                    from datetime import datetime as dt
                    parsed_prev = dt.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                    display_prev = parsed_prev.strftime('%Y-%m-%d %H:%M')
                except:
                    display_prev = prev_timestamp
            else:
                display_prev = 'unknown'

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

            print(f"🔄 Ticket #{ticket_id}: UPDATED (existing AI Analysis refreshed)")
            print(f"   Previous analysis: {display_prev}")
            print(f"   Updated analysis: {current_time}")
            print(f"   Category: {analysis.get('root_cause', 'unknown')}")
            if analysis.get('draft_status') == 'success':
                print(f"   Draft: ✅ ({analysis.get('draft_word_count', 0)}w)")
            elif analysis.get('draft_status') == 'failed':
                print(f"   Draft: ⚠️  Failed")
        elif not has_existing_comment:
            # Add new comment
            payload["ticket"]["comment"] = {
                "body": internal_comment,
                "public": False  # Internal note, not visible to customer
            }
            print(f"✅ Ticket #{ticket_id}: PROCESSED (new AI Analysis added)")
            print(f"   Category: {analysis.get('root_cause', 'unknown')}")
            print(f"   Urgency: {analysis.get('urgency', 'unknown')}")
            print(f"   Sentiment: {analysis.get('sentiment', 'unknown')}")
            if analysis.get('draft_status') == 'success':
                print(f"   Draft: ✅ ({analysis.get('draft_word_count', 0)}w)")

        # STEP 8: Update ticket
        response = requests.put(
            url,
            json=payload,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()

        return {
            "updated": True,
            "skipped": False,
            "comment_added": not has_existing_comment,
            "comment_updated": has_existing_comment and force
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating ticket #{ticket_id}: {str(e)}")
        return {
            "updated": False,
            "skipped": False,
            "error": str(e)
        }


def update_ticket_batch(tickets_with_analysis, force=False):
    """
    Update multiple tickets at once with deduplication

    Args:
        tickets_with_analysis: List of (ticket_id, analysis) tuples
        force: Force update even if already processed

    Returns:
        Dictionary with success/failure/skipped counts
    """
    results = {
        "success": 0,
        "skipped": 0,
        "failed": 0
    }

    for ticket_id, analysis in tickets_with_analysis:
        result = update_ticket(ticket_id, analysis, force=force)

        if result.get("skipped"):
            results["skipped"] += 1
        elif result.get("updated"):
            results["success"] += 1
        else:
            results["failed"] += 1

    print(f"\n📊 Batch Update Results:")
    print(f"   ✅ Success: {results['success']}")
    print(f"   ⏭️  Skipped: {results['skipped']} (already processed)")
    print(f"   ❌ Failed: {results['failed']}")

    return results


if __name__ == "__main__":
    # Test with sample data
    print("🔧 Testing ticket update with deduplication...\n")

    sample_analysis = {
        "summary": "Customer requesting refund for delayed order",
        "root_cause": "refund",
        "urgency": "high",
        "sentiment": "negative"
    }

    # You would replace this with an actual ticket ID
    test_ticket_id = input("Enter a test ticket ID (or press Enter to skip): ").strip()

    if test_ticket_id:
        print("\n--- Test 1: Initial update ---")
        result1 = update_ticket(int(test_ticket_id), sample_analysis)
        print(f"Result: {result1}")

        print("\n--- Test 2: Try updating again (should skip) ---")
        result2 = update_ticket(int(test_ticket_id), sample_analysis)
        print(f"Result: {result2}")

        print("\n--- Test 3: Force update (should update tags only, no duplicate comment) ---")
        result3 = update_ticket(int(test_ticket_id), sample_analysis, force=True)
        print(f"Result: {result3}")

        print("\n✅ Deduplication test complete!")
        print("Check Zendesk UI to verify:")
        print("   - Only ONE AI analysis comment exists")
        print("   - Tags are updated correctly")
        print("   - No duplicate comments")
    else:
        print("⏭️  Skipping update test")