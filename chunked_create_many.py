# chunked_create_many.py
import os, json, requests, math, time
from requests.auth import HTTPBasicAuth

SUBDOMAIN = "cognizant-72363"
EMAIL = "madhan1787@gmail.com"
API_TOKEN = os.getenv("ZENDESK_API_TOKEN")
JSON_FILE = "zendesk_bulk_import_500_pii_clean.json"  # cleaned JSON path
BASE = f"https://{SUBDOMAIN}.zendesk.com/api/v2/"

if not API_TOKEN:
    raise SystemExit("Set ZENDESK_API_TOKEN environment variable locally before running.")

auth = HTTPBasicAuth(f"{EMAIL}/token", API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

CHUNK_SIZE = 80  # keep this <= 80; reduce if you hit size limits
RATE_LIMIT_SLEEP = 1.0  # seconds between batch calls, adjust if you hit 429

def load_tickets(path):
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    tickets = payload.get("tickets") or []
    print(f"Loaded {len(tickets)} tickets")
    return tickets

def create_batch(batch, idx):
    url = BASE + "tickets/create_many.json"
    body = {"tickets": batch}
    try:
        resp = requests.post(url, headers=HEADERS, auth=auth, json=body, timeout=120)
    except Exception as e:
        print("Request exception:", e)
        return False, str(e)
    print(f"Batch {idx} -> HTTP {resp.status_code}")
    if resp.status_code not in (200,201):
        print("Response body:", resp.text)
        return False, resp.text
    return True, resp.json()

def main():
    tickets = load_tickets(JSON_FILE)
    if not tickets:
        print("No tickets found.")
        return
    chunks = [tickets[i:i+CHUNK_SIZE] for i in range(0, len(tickets), CHUNK_SIZE)]
    created = 0
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Creating chunk {idx}/{len(chunks)} (size={len(chunk)})")
        ok, resp = create_batch(chunk, idx)
        if not ok:
            print("Stopping upload due to error on chunk", idx)
            break
        created += len(chunk)
        time.sleep(RATE_LIMIT_SLEEP)
    print("Done. Attempted:", len(tickets), "Created approx:", created)

if __name__ == "__main__":
    main()
