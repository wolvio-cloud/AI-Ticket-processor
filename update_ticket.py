"""
update_ticket.py - Update Zendesk tickets with AI analysis
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZENDESK_SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')


def update_ticket(ticket_id, analysis):
    """
    Update Zendesk ticket with AI analysis results
    
    Args:
        ticket_id: Zendesk ticket ID
        analysis: Dictionary with analysis results
        
    Returns:
        Boolean indicating success
    """
    
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"
    
    try:
        # Step 1: Get current ticket to retrieve existing tags
        response = requests.get(
            url,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()
        
        current_ticket = response.json()['ticket']
        existing_tags = current_ticket.get('tags', [])
        
        # Step 2: Create internal comment with analysis
        internal_comment = f"""🤖 AI Analysis:

Summary: {analysis['summary']}
Root Cause: {analysis['root_cause']}
Urgency: {analysis['urgency']}
Sentiment: {analysis['sentiment']}
"""
        
        # Step 3: Create our custom tags (prefixed with 'ai_' to avoid conflicts)
        our_tags = [
            "ai_processed",
            f"ai_{analysis['root_cause']}",
            f"ai_{analysis['urgency']}",
            f"ai_{analysis['sentiment']}"
        ]
        
        # Step 4: Combine existing tags with our tags (avoid duplicates)
        all_tags = list(set(existing_tags + our_tags))
        
        # Step 5: Update ticket with comment and all tags
        payload = {
            "ticket": {
                "comment": {
                    "body": internal_comment,
                    "public": False  # Internal note, not visible to customer
                },
                "tags": all_tags  # Use 'tags' instead of 'additional_tags'
            }
        }
        
        response = requests.put(
            url,
            json=payload,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()
        
        print(f"✅ Ticket #{ticket_id} updated successfully")
        print(f"   AI tags added: {', '.join(our_tags)}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating ticket #{ticket_id}: {str(e)}")
        return False


def update_ticket_batch(tickets_with_analysis):
    """
    Update multiple tickets at once
    
    Args:
        tickets_with_analysis: List of (ticket_id, analysis) tuples
        
    Returns:
        Dictionary with success/failure counts
    """
    results = {
        "success": 0,
        "failed": 0
    }
    
    for ticket_id, analysis in tickets_with_analysis:
        if update_ticket(ticket_id, analysis):
            results["success"] += 1
        else:
            results["failed"] += 1
    
    print(f"\n📊 Batch Update Results:")
    print(f"   ✅ Success: {results['success']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    return results


if __name__ == "__main__":
    # Test with sample data
    print("🔧 Testing ticket update...\n")
    
    sample_analysis = {
        "summary": "Customer requesting refund for delayed order",
        "root_cause": "refund",
        "urgency": "high",
        "sentiment": "negative"
    }
    
    # You would replace this with an actual ticket ID
    test_ticket_id = input("Enter a test ticket ID (or press Enter to skip): ").strip()
    
    if test_ticket_id:
        update_ticket(int(test_ticket_id), sample_analysis)
    else:
        print("⏭️  Skipping update test")