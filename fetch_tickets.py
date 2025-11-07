"""
fetch_tickets.py - Fetch recent tickets from Zendesk
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZENDESK_SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')
ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN')


def get_recent_tickets(limit=100):
    """
    Fetch recent tickets from Zendesk
    
    Args:
        limit: Maximum number of tickets to fetch (default 100)
        
    Returns:
        List of ticket dictionaries
    """
    # Use search API to get all tickets, sorted by updated_at
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/search.json"
    params = {
        'query': 'type:ticket',  # Get all tickets regardless of status
        'sort_by': 'updated_at',
        'sort_order': 'desc'
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
        print("\n📋 Fetching recent tickets...\n")
        tickets = get_recent_tickets(21)
        
        for i, ticket in enumerate(tickets, 1):
            print(f"{i}. Ticket #{ticket['id']}")
            print(f"   Subject: {ticket['subject']}")
            print(f"   Status: {ticket['status']}")
            print(f"   Created: {ticket['created_at']}")
            print()