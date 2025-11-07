import requests
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class ZendeskService:
    """Service for interacting with Zendesk API"""
    
    def __init__(self, subdomain: str, email: str, api_token: str):
        self.subdomain = subdomain
        self.email = email
        self.api_token = api_token
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self.auth = (f"{email}/token", api_token)
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """
        Fetch a single ticket from Zendesk
        
        Args:
            ticket_id: The Zendesk ticket ID
            
        Returns:
            Ticket data as dictionary or None if failed
        """
        try:
            url = f"{self.base_url}/tickets/{ticket_id}.json"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get("ticket")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch ticket {ticket_id}: {str(e)}")
            return None
    
    def search_tickets(self, query: str, limit: int = 100) -> List[Dict]:
        """
        Search for tickets using Zendesk search API
        
        Args:
            query: Search query (e.g., "status:new type:ticket")
            limit: Maximum number of results
            
        Returns:
            List of ticket dictionaries
        """
        try:
            url = f"{self.base_url}/search.json"
            params = {
                "query": query,
                "per_page": limit
            }
            response = requests.get(url, auth=self.auth, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get("results", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search tickets: {str(e)}")
            return []
    
    def get_unprocessed_tickets(self, limit: int = 100) -> List[Dict]:
        """
        Get tickets that haven't been processed by AI yet
        
        Args:
            limit: Maximum number of tickets to fetch
            
        Returns:
            List of unprocessed tickets
        """
        # Search for tickets without the 'ai-processed' tag
        query = "type:ticket -tags:ai-processed"
        return self.search_tickets(query, limit)
    
    def update_ticket(
        self, 
        ticket_id: int, 
        tags: Optional[List[str]] = None,
        comment: Optional[str] = None,
        internal_note: Optional[str] = None
    ) -> bool:
        """
        Update a Zendesk ticket with tags and/or comments
        
        Args:
            ticket_id: The ticket ID to update
            tags: List of tags to add
            comment: Public comment to add
            internal_note: Internal note for agents
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/tickets/{ticket_id}.json"
            
            # Build update payload
            ticket_update = {}
            
            if tags:
                ticket_update["tags"] = tags
            
            # Add comment or note
            if comment or internal_note:
                ticket_update["comment"] = {
                    "body": comment or internal_note,
                    "public": bool(comment)  # Public if comment, private if internal_note
                }
            
            payload = {"ticket": ticket_update}
            
            response = requests.put(
                url, 
                auth=self.auth, 
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Successfully updated ticket {ticket_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update ticket {ticket_id}: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the Zendesk API connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = f"{self.base_url}/users/me.json"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
