"""
create_test_tickets.py - Bulk create test tickets in Zendesk
"""
import os
import time
from dotenv import load_dotenv
from fetch_tickets import ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN
import requests

load_dotenv()

# Sample tickets data
SAMPLE_TICKETS = [
    {
        "subject": "App crashes when clicking submit button",
        "description": "Our mobile app crashes every time I click the submit button on the payment form. I've tried reinstalling but the issue persists. This is blocking me from completing my purchase. Error code: 500",
        "priority": "urgent",
        "type": "problem"
    },
    {
        "subject": "Want a refund for my subscription",
        "description": "I signed up yesterday but this product doesn't meet my needs. I want a full refund immediately. Please cancel my subscription and process the refund ASAP.",
        "priority": "high",
        "type": "problem"
    },
    {
        "subject": "How do I reset my password?",
        "description": "I forgot my password and can't log into my account. I tried the reset link but didn't receive any email. Can you help me reset it?",
        "priority": "normal",
        "type": "question"
    },
    {
        "subject": "Feature request: Dark mode",
        "description": "I love your app but my eyes hurt at night. Can you please add a dark mode option? This would make the app much more comfortable to use in the evening.",
        "priority": "low",
        "type": "question"
    },
    {
        "subject": "Payment failed but money was deducted",
        "description": "I tried to make a payment yesterday and it said 'payment failed' but the money was deducted from my bank account. Transaction ID: TXN12345. Please help!",
        "priority": "urgent",
        "type": "problem"
    },
    {
        "subject": "Cannot upload files larger than 5MB",
        "description": "When I try to upload files larger than 5MB, I get an error message. Is there a way to increase this limit? I need to upload my project files.",
        "priority": "normal",
        "type": "question"
    },
    {
        "subject": "Account locked after 3 failed login attempts",
        "description": "My account got locked after I mistyped my password 3 times. How can I unlock it? I need to access my data urgently.",
        "priority": "high",
        "type": "problem"
    },
    {
        "subject": "Integration with Slack not working",
        "description": "I connected your app to our Slack workspace but notifications aren't coming through. I've checked all settings and permissions. Can you investigate?",
        "priority": "normal",
        "type": "problem"
    },
    {
        "subject": "Thank you for the excellent support!",
        "description": "I just want to say thank you to Sarah from your support team. She helped me resolve my issue within 10 minutes. Great service!",
        "priority": "low",
        "type": "question"
    },
    {
        "subject": "Dashboard loading very slowly",
        "description": "The dashboard takes 30+ seconds to load every time I open it. This is much slower than before. Is there a server issue?",
        "priority": "normal",
        "type": "problem"
    },
    {
        "subject": "How to export data to CSV?",
        "description": "I need to export all my data to CSV format for my records. I can't find the export option in the settings. Where is it located?",
        "priority": "low",
        "type": "question"
    },
    {
        "subject": "Billing charged twice this month",
        "description": "I was charged twice for my subscription this month. My bank statement shows two charges of $49.99 on Nov 1st. Please refund the duplicate charge.",
        "priority": "high",
        "type": "problem"
    },
    {
        "subject": "Mobile app not syncing with web version",
        "description": "Changes I make on the mobile app don't appear on the web version. I've tried logging out and back in but the sync issue continues.",
        "priority": "normal",
        "type": "problem"
    },
    {
        "subject": "Request: API documentation for developers",
        "description": "I'm a developer trying to integrate your API. The documentation is incomplete. Can you provide detailed API docs with code examples?",
        "priority": "normal",
        "type": "question"
    },
    {
        "subject": "Cannot delete my account",
        "description": "I want to delete my account permanently but can't find the option. The settings page doesn't have a delete account button. How do I do this?",
        "priority": "normal",
        "type": "question"
    },
    {
        "subject": "Notification emails going to spam",
        "description": "All notification emails from your service are landing in my spam folder. I've marked them as not spam but it keeps happening. Can you fix this?",
        "priority": "low",
        "type": "problem"
    },
    {
        "subject": "Premium features not working after upgrade",
        "description": "I upgraded to Premium yesterday but I still don't have access to premium features. The app says I'm on the free plan. Payment went through successfully.",
        "priority": "urgent",
        "type": "problem"
    },
    {
        "subject": "Suggestion: Add bulk edit functionality",
        "description": "It would be really helpful if we could edit multiple items at once instead of one by one. This would save so much time for power users like me.",
        "priority": "low",
        "type": "question"
    },
    {
        "subject": "Getting 404 error on reports page",
        "description": "Every time I click on Reports in the menu, I get a 404 error. This started happening after yesterday's update. Other pages work fine.",
        "priority": "high",
        "type": "problem"
    },
    {
        "subject": "Love the new update! Minor bug found",
        "description": "The new interface looks amazing! However, I found a small bug: the search icon overlaps with text on mobile. Otherwise, everything is perfect!",
        "priority": "low",
        "type": "question"
    }
]


def create_ticket(ticket_data):
    """Create a single ticket in Zendesk"""
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets.json"
    
    payload = {
        "ticket": {
            "subject": ticket_data["subject"],
            "comment": {
                "body": ticket_data["description"]
            },
            "priority": ticket_data["priority"],
            "type": ticket_data["type"],
            "status": "open"
        }
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()
        
        ticket = response.json()["ticket"]
        print(f"✅ Created ticket #{ticket['id']}: {ticket_data['subject'][:50]}...")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create ticket: {str(e)}")
        return False


def main():
    print("🎯 BULK TICKET CREATOR")
    print("="*60)
    print(f"Creating {len(SAMPLE_TICKETS)} test tickets...\n")
    
    created = 0
    failed = 0
    
    for i, ticket_data in enumerate(SAMPLE_TICKETS, 1):
        print(f"[{i}/{len(SAMPLE_TICKETS)}] ", end="")
        
        if create_ticket(ticket_data):
            created += 1
        else:
            failed += 1
        
        # Rate limiting - wait 1 second between requests
        if i < len(SAMPLE_TICKETS):
            time.sleep(1)
    
    print("\n" + "="*60)
    print(f"📊 RESULTS:")
    print(f"   ✅ Created: {created}")
    print(f"   ❌ Failed: {failed}")
    print("="*60)
    print("\n✨ Done! Check your Zendesk for the new tickets!")


if __name__ == "__main__":
    main()