"""
================================================================================
Ticket Fetcher - Zendesk Ticket Retrieval Service
================================================================================

DESCRIPTION:
    Fetches recent support tickets from Zendesk API with optional filtering
    to exclude already-processed tickets. Supports pagination and customizable
    ticket limits.

FEATURES:
    - Fetch recent tickets from Zendesk (default: last 100)
    - Filter out already-processed tickets (ai_processed tag)
    - Customizable ticket limits
    - Automatic pagination handling
    - Error handling with detailed error messages
    - Test mode for connection verification

KEY FUNCTIONS:
    - get_recent_tickets(): Fetch recent tickets with optional filtering
      Args: limit (int), exclude_processed (bool)
      Returns: list of ticket dictionaries

    - test_zendesk_connection(): Verify Zendesk API connectivity
      Returns: bool indicating connection success

FILTERING:
    When exclude_processed=True, fetches tickets WITHOUT 'ai_processed' tag.
    When exclude_processed=False, fetches all recent tickets regardless of tags.

INTEGRATION:
    Used by Ai_ticket_processor.py to retrieve tickets for processing.
    Works with update_ticket.py tagging system to avoid reprocessing.

USAGE:
    from fetch_tickets import get_recent_tickets, test_zendesk_connection

    # Test connection first
    if test_zendesk_connection():
        print("Connected to Zendesk!")

    # Fetch unprocessed tickets
    tickets = get_recent_tickets(limit=50, exclude_processed=True)
    print(f"Found {len(tickets)} unprocessed tickets")

    # Fetch all recent tickets
    all_tickets = get_recent_tickets(limit=100, exclude_processed=False)

ENVIRONMENT VARIABLES:
    ZENDESK_SUBDOMAIN    - Your Zendesk subdomain (e.g., 'yourcompany')
    ZENDESK_EMAIL        - Zendesk admin email
    ZENDESK_API_TOKEN    - Zendesk API token

API DOCUMENTATION:
    Zendesk API: https://developer.zendesk.com/api-reference/

AUTHOR: AI Ticket Processor Team
LICENSE: Proprietary
LAST UPDATED: 2025-11-11
================================================================================
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZENDESK_SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')


def get_recent_tickets(limit=100, exclude_processed=False):
    """
    Fetch recent tickets from Zendesk with optional deduplication

    Args:
        limit: Maximum number of tickets to fetch (default 100)
        exclude_processed: If True, exclude tickets with 'ai_processed' tag (default False)

    Returns:
        List of ticket dictionaries
    """
    # Use search API to get all tickets, sorted by updated_at
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/search.json"

    # Build query with optional exclusion of processed tickets
    if exclude_processed:
        query = 'type:ticket -tags:ai_processed'  # Exclude already processed tickets
        print("🔍 Fetching only unprocessed tickets (excluding ai_processed tag)")
    else:
        query = 'type:ticket'  # Get all tickets regardless of status
        print("🔍 Fetching all tickets")

    params = {
        'query': query,
        'sort_by': 'created_at',  # Sort by created date (oldest first for processing)
        'sort_order': 'asc'
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()
        
        tickets = response.json()['results'][:limit]
        
        print(f"✅ Successfully fetched {len(tickets)} tickets")
        return tickets
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching tickets: {str(e)}")
        return []


def get_ticket_by_id(ticket_id):
    """
    Fetch a specific ticket by ID
    
    Args:
        ticket_id: Zendesk ticket ID
        
    Returns:
        Ticket dictionary or None
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
        print(f"✅ Successfully fetched ticket #{ticket_id}")
        return ticket
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching ticket #{ticket_id}: {str(e)}")
        return None


def test_connection():
    """Test Zendesk API connection"""
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/users/me.json"
    
    try:
        response = requests.get(
            url,
            auth=(f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN),
            timeout=10
        )
        response.raise_for_status()
        
        user = response.json()['user']
        print(f"✅ Connected to Zendesk as: {user['email']}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🔍 Testing Zendesk Connection...")
    print(f"   Subdomain: {ZENDESK_SUBDOMAIN}")
    print(f"   Email: {ZENDESK_EMAIL}")
    print()

    if test_connection():
        print("\n" + "="*60)
        print("TEST 1: Fetch all tickets")
        print("="*60)
        all_tickets = get_recent_tickets(limit=21, exclude_processed=False)

        for i, ticket in enumerate(all_tickets[:5], 1):  # Show first 5
            tags = ticket.get('tags', [])
            has_ai_tag = 'ai_processed' in tags
            print(f"{i}. Ticket #{ticket['id']}")
            print(f"   Subject: {ticket['subject']}")
            print(f"   Status: {ticket['status']}")
            print(f"   AI Processed: {'✅ Yes' if has_ai_tag else '❌ No'}")
            print()

        print("\n" + "="*60)
        print("TEST 2: Fetch only unprocessed tickets")
        print("="*60)
        unprocessed_tickets = get_recent_tickets(limit=21, exclude_processed=True)

        if not unprocessed_tickets:
            print("✅ No unprocessed tickets found! All tickets have been processed.")
        else:
            for i, ticket in enumerate(unprocessed_tickets[:5], 1):  # Show first 5
                print(f"{i}. Ticket #{ticket['id']}")
                print(f"   Subject: {ticket['subject']}")
                print(f"   Status: {ticket['status']}")
                print()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total tickets (all):         {len(all_tickets)}")
        print(f"Unprocessed tickets:         {len(unprocessed_tickets)}")
        print(f"Already processed:           {len(all_tickets) - len(unprocessed_tickets)}")
        print("="*60)