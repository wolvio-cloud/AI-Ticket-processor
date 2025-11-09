"""
update_ticket.py - Update Zendesk tickets with AI analysis (with deduplication)
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
    Check if ticket has an existing AI Analysis comment and return its ID

    Args:
        ticket_id: Zendesk ticket ID

    Returns:
        Dictionary with 'exists' (bool) and 'comment_id' (int or None)
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

        # Look for AI Analysis comment (search in reverse for latest)
        for comment in reversed(comments):
            if comment.get('body', '').startswith('🤖 AI Analysis (Automated)'):
                return {
                    'exists': True,
                    'comment_id': comment['id'],
                    'comment_body': comment['body']
                }

        return {'exists': False, 'comment_id': None}

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Warning: Could not fetch comments for ticket #{ticket_id}: {str(e)}")
        return {'exists': False, 'comment_id': None}


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

        # STEP 2: Determine action based on force flag
        if has_existing_comment and not force:
            print(f"⏭️  Ticket #{ticket_id} already has AI Analysis, skipping (use --force to update)")
            return {
                "updated": False,
                "skipped": True,
                "reason": "already_has_ai_comment"
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
            print(f"✅ Ticket #{ticket_id} updated successfully (reprocessing - comment updated)")
            print(f"   AI tags updated: {', '.join(our_tags)}")
            print(f"   Comment action: UPDATED existing AI Analysis")
        elif not has_existing_comment:
            # Add new comment
            payload["ticket"]["comment"] = {
                "body": internal_comment,
                "public": False  # Internal note, not visible to customer
            }
            print(f"✅ Ticket #{ticket_id} updated successfully (new processing)")
            print(f"   AI tags added: {', '.join(our_tags)}")
            print(f"   Comment action: ADDED new AI Analysis")

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