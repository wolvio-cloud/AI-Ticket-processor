#!/usr/bin/env python3
"""
upload_import_and_poll.py
Uploads /mnt/data/zendesk_bulk_import_500_pii.json to Zendesk import API,
polls the import job until it completes, and prints results.

Usage (Linux/macOS):
export ZENDESK_API_TOKEN="your_token_here"
python upload_import_and_poll.py
"""
import os, time, json, requests
from requests.auth import HTTPBasicAuth

# CONFIG - filled with values you provided
SUBDOMAIN = "cognizant-72363"
EMAIL = "madhan1787@gmail.com"
JSON_FILE = "zendesk_bulk_import_500_pii.json"
API_TOKEN = os.getenv("ZENDESK_API_TOKEN")
BASE = f"https://{SUBDOMAIN}.zendesk.com/api/v2/"

if not API_TOKEN:
    raise SystemExit("Set ZENDESK_API_TOKEN environment variable before running.")

auth = HTTPBasicAuth(f"{EMAIL}/token", API_TOKEN)
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def upload_import(json_path):
    url = BASE + "imports/tickets.json"
    print("Uploading JSON to", url)
    with open(json_path, "rb") as f:
        resp = requests.post(url, headers=HEADERS, auth=auth, data=f)
    if resp.status_code not in (200, 201):
        print("Upload failed:", resp.status_code, resp.text)
        raise SystemExit(1)
    data = resp.json()
    # The response should contain 'import' object with 'id'; handle variations
    import_id = None
    if isinstance(data, dict):
        import_id = data.get("import", {}).get("id") or data.get("id")
    if not import_id:
        print("Could not find import id in response:", json.dumps(data, indent=2))
        raise SystemExit(1)
    print("Import job created. id =", import_id)
    return import_id

def poll_import(import_id, timeout_minutes=20, poll_interval=5):
    url = BASE + f"imports/{import_id}.json"
    deadline = time.time() + timeout_minutes * 60
    while time.time() < deadline:
        resp = requests.get(url, headers=HEADERS, auth=auth)
        if resp.status_code != 200:
            print("Error polling:", resp.status_code, resp.text)
            time.sleep(poll_interval)
            continue
        data = resp.json().get("import") or resp.json()
        status = data.get("status")
        print("Import status:", status)
        # statuses: "queued", "processing", "completed", "failed" (may vary)
        if status in ("completed", "done", "finished"):
            print("Import completed.")
            return data
        if status in ("failed","error"):
            print("Import failed:", json.dumps(data, indent=2))
            raise SystemExit(1)
        time.sleep(poll_interval)
    print("Polling timed out after", timeout_minutes, "minutes.")
    raise SystemExit(1)

def main():
    import_id = upload_import(JSON_FILE)
    result = poll_import(import_id)
    print("Import result summary:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
