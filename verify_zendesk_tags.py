"""
Verify Zendesk Tags - Check if AI tags were properly added
"""
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN')
EMAIL = os.getenv('ZENDESK_EMAIL')
TOKEN = os.getenv('ZENDESK_API_TOKEN')

zendesk_auth = (f"{EMAIL}/token", TOKEN)

def check_ticket_tags(ticket_id):
    """Check if a specific ticket has AI tags"""
    url = f"https://{SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}.json"
    
    try:
        resp = requests.get(url, auth=zendesk_auth, timeout=10)
        resp.raise_for_status()
        ticket = resp.json()['ticket']
        
        tags = ticket.get('tags', [])
        ai_tags = [tag for tag in tags if tag.startswith('ai_')]
        
        return {
            'ticket_id': ticket_id,
            'has_ai_tags': len(ai_tags) > 0,
            'ai_tags': ai_tags,
            'all_tags': tags,
            'priority': ticket.get('priority'),
            'status': ticket.get('status')
        }
    except Exception as e:
        return {
            'ticket_id': ticket_id,
            'error': str(e)
        }

def verify_from_results(results_file):
    """Verify tags for tickets in results file"""
    print("="*80)
    print("ZENDESK TAG VERIFICATION")
    print("="*80)
    
    # Load results
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['results'][:10]  # Check first 10 tickets
    
    print(f"\nChecking first 10 tickets from results file...")
    print(f"Total tickets processed: {data['total']}\n")
    
    verified = 0
    failed = 0
    
    for i, result in enumerate(results, 1):
        ticket_id = result['ticket_id']
        print(f"[{i}/10] Checking Ticket #{ticket_id}...", end=" ")
        
        check = check_ticket_tags(ticket_id)
        
        if 'error' in check:
            print(f"❌ ERROR: {check['error']}")
            failed += 1
        elif check['has_ai_tags']:
            print(f"✅ Tags: {check['ai_tags']}")
            verified += 1
        else:
            print(f"⚠️ NO AI TAGS FOUND")
            failed += 1
    
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Verified: {verified}/10")
    print(f"Failed: {failed}/10")
    
    if verified == 10:
        print("\n🎉 SUCCESS! All checked tickets have AI tags!")
    elif verified >= 8:
        print("\n✅ GOOD! Most tickets have AI tags.")
    else:
        print("\n⚠️ WARNING! Many tickets missing AI tags.")
    
    print("="*80)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        # Find latest results file
        import glob
        results_files = sorted(glob.glob('logs/results_*.json'))
        if not results_files:
            print("❌ No results files found!")
            sys.exit(1)
        results_file = results_files[-1]
        print(f"Using latest results file: {results_file}\n")
    
    verify_from_results(results_file)