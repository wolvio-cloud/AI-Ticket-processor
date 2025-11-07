# single_ticket_test.py
import os, json, requests
from requests.auth import HTTPBasicAuth

SUBDOMAIN = "cognizant-72363"
EMAIL = "madhan1787@gmail.com"
API_TOKEN = os.getenv("ZENDESK_API_TOKEN")  # set locally, don't paste it anywhere
BASE = f"https://{SUBDOMAIN}.zendesk.com/api/v2/"

auth = HTTPBasicAuth(f"{EMAIL}/token", API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

sample = {
  "ticket": {
    "subject": "Test PII upload - single ticket",
    "comment": {"body": "Test description with email test.user@example.com and card 4111 1111 1111 1111", "public": False},
    "requester": {"name": "Test User", "email": "test.user@example.com"},
    "tags": ["pii_test","sanity_check"],
    "priority": "normal"
  }
}

resp = requests.post(BASE + "tickets.json", headers=HEADERS, auth=auth, json=sample, timeout=60)
print("HTTP", resp.status_code)
print(resp.text)
