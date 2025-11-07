"""
Multi-Industry Test Data Generator
Creates realistic support tickets across industries to validate:
1. E-commerce classification (45%)
2. SaaS classification (45%)
3. Other industries fallback to "general" (5%)
4. Edge case handling (5%)
"""
import json
import random
from datetime import datetime, timedelta

# ============================================================================
# E-COMMERCE TICKET TEMPLATES (112 tickets - 45%)
# ============================================================================

ECOMMERCE_TEMPLATES = {
    'delivery_issue': [
        "My order #{order_id} was supposed to arrive {days} days ago but still hasn't come. Tracking shows it's stuck in transit.",
        "Package #{order_id} delivered to wrong address. I never received it. Need immediate redelivery.",
        "Order delayed by a week! This is unacceptable. Order #{order_id}. I need it urgently for a gift.",
        "Tracking says delivered but I didn't receive anything. Order #{order_id}. Please investigate.",
        "My package arrived damaged - box was crushed. Order #{order_id}. Who do I contact about this?"
    ],
    'product_defect': [
        "Product arrived broken! The screen is cracked. Order #{order_id}. Want full refund.",
        "Item not as described - color is completely different from photos. Order #{order_id}. Very disappointed.",
        "Shoes arrived with defect - sole is coming off already. Only wore once! Order #{order_id}.",
        "Electronic item doesn't work at all - won't turn on. Dead on arrival. Order #{order_id}.",
        "Quality is terrible - fabric is cheap and tears easily. This is not what I paid for. Order #{order_id}."
    ],
    'payment_failed': [
        "Payment declined but I have sufficient balance. Card ending {card_last4}. Order #{order_id}.",
        "Charged twice for the same order! See duplicate charges on my statement. Order #{order_id}.",
        "Payment went through but order shows as failed. Money was taken from account. Order #{order_id}.",
        "Getting error at checkout - payment keeps failing. Tried {attempts} times. Card is valid.",
        "Refund not received yet. It's been {days} days since I returned item. Order #{order_id}."
    ],
    'refund_request': [
        "Want full refund - product is not what I expected. Order #{order_id}. How long does refund take?",
        "Requesting refund for order #{order_id}. Changed my mind about purchase. Item unopened.",
        "Product didn't fit. Need refund to original payment method. Order #{order_id}.",
        "Received wrong item so want refund instead of replacement. Order #{order_id}.",
        "Cancel order and refund immediately - don't want it anymore. Order #{order_id}."
    ],
    'order_cancellation': [
        "Need to cancel order #{order_id} urgently! Just placed it 10 minutes ago.",
        "Can I still cancel? Order #{order_id}. Found better price elsewhere.",
        "Order #{order_id} - please cancel before it ships. No longer need the item.",
        "Accidentally ordered wrong size. Want to cancel order #{order_id} and reorder correct one.",
        "Cancel my subscription order #{order_id}. Moving to different product."
    ],
    'wrong_item': [
        "Received completely different product! Ordered shoes got a t-shirt. Order #{order_id}.",
        "Wrong size sent - ordered Large received Small. Order #{order_id}. Need exchange.",
        "Got the wrong color. Ordered black received white. Order #{order_id}.",
        "Received {quantity} items instead of {correct_quantity}. Order #{order_id}. What do I do?",
        "Wrong variant sent. Ordered iPhone 13 Pro received regular iPhone 13. Order #{order_id}."
    ],
    'account_help': [
        "Can't login to my account. Password reset link not working. Email: {email}",
        "Forgot my password and security question. How do I recover account?",
        "Account locked after too many login attempts. Please unlock. Username: {username}",
        "Can't update my shipping address. Getting error message. Need to change it urgently.",
        "How do I delete my account? Want to close it permanently."
    ],
    'return_exchange': [
        "How do I return this item? Order #{order_id}. Want to exchange for different size.",
        "Return label not working. Can't print it. Order #{order_id}. Need help ASAP.",
        "Want to exchange item for different color. Order #{order_id}. What's the process?",
        "Do you cover return shipping? Item doesn't fit. Order #{order_id}.",
        "How long do returns take? Sent item back {days} days ago. Order #{order_id}."
    ],
    'promo_code': [
        "Promo code {promo_code} not working at checkout. Says invalid but I just received it.",
        "Discount not applied even though I entered code {promo_code}. Getting full price.",
        "Code {promo_code} expired already? Email said valid until {date}.",
        "First time customer discount not working. Code {promo_code}.",
        "Applied code but discount is less than advertised. Code {promo_code} should give {discount}% off."
    ],
    'tracking_inquiry': [
        "Where is my order? #{order_id}. Tracking hasn't updated in {days} days.",
        "Tracking number {tracking} shows no information. Is it shipped yet?",
        "Order #{order_id} status stuck on 'Processing' for a week. What's going on?",
        "When will my order ship? Placed it {days} days ago. Order #{order_id}.",
        "Tracking says delivered but never arrived. Order #{order_id}. Please help."
    ]
}

# ============================================================================
# SAAS TICKET TEMPLATES (113 tickets - 45%)
# ============================================================================

SAAS_TEMPLATES = {
    'login_issue': [
        "Can't login - getting 'Invalid credentials' but password is correct. Username: {username}",
        "Account locked after failed login attempts. Please unlock immediately.",
        "SSO login not working - redirects to error page. Using {provider} authentication.",
        "2FA code not arriving. Can't login without it. Checked spam folder.",
        "Password reset email never came. Tried {attempts} times. Email: {email}"
    ],
    'bug_report': [
        "Found a bug - clicking Save button does nothing. Tried on Chrome and Firefox.",
        "App crashes when I try to export data. Happens every time. Version {version}.",
        "Dashboard showing wrong numbers. Revenue is off by ${amount}. Please fix urgently.",
        "Can't upload files - getting error 'File too large' even for small files.",
        "Search function broken - returns no results even for exact matches."
    ],
    'feature_request': [
        "Please add dark mode! Would really help with night-time usage.",
        "Need bulk import feature. Currently have to add {count} items manually.",
        "Would love to see calendar view option instead of just list view.",
        "Can you add export to PDF? Currently only have CSV option.",
        "Request: Add keyboard shortcuts for common actions. Would speed up workflow significantly."
    ],
    'integration_error': [
        "Slack integration stopped working - not receiving notifications anymore.",
        "Zapier connection keeps failing. Error: 'Authentication failed'.",
        "Google Calendar sync not working. Events aren't showing up.",
        "Salesforce integration broke after your recent update. Nothing syncing.",
        "Webhook stopped firing. Checked endpoint - it's working. Issue on your end?"
    ],
    'billing_question': [
        "How do I upgrade from Starter to Pro plan? Need more seats.",
        "Charged ${amount} but invoice says ${different_amount}. Which is correct?",
        "Want to downgrade plan. How does prorated refund work?",
        "Card declined - please update payment method manually. Card ending {card_last4}.",
        "Need invoice for last month. Accounting department needs it urgently."
    ],
    'performance_slow': [
        "App extremely slow today. Taking {seconds} seconds to load dashboard.",
        "Page load times increased dramatically after last update. Any issues?",
        "Reports timing out - can't generate anything. Been trying for {minutes} minutes.",
        "Everything lagging - typing has noticeable delay. Is this a known issue?",
        "Dashboard freezes when loading large datasets. Unusable right now."
    ],
    'api_error': [
        "Getting 429 Too Many Requests error. Need rate limit increased ASAP.",
        "API returning 500 Internal Server Error for /api/users endpoint.",
        "Authentication failing - API key is valid but getting 401 Unauthorized.",
        "Webhook payload format changed without notice. Breaking our integration.",
        "API response time increased from {old_ms}ms to {new_ms}ms. Performance issue?"
    ],
    'data_sync': [
        "Data not syncing between web and mobile app. Last sync: {hours} hours ago.",
        "Changes made on desktop not appearing on mobile. Tried logging out/in.",
        "Sync stuck at {percent}%. Been {minutes} minutes. What's wrong?",
        "Lost data after sync failed. Can you recover from backup?",
        "Duplicate entries appearing after sync. Database getting messy."
    ],
    'account_setup': [
        "New user onboarding - how do I set up my workspace? Need guide.",
        "Can't complete setup - stuck on step {step}. What am I doing wrong?",
        "How do I import existing data from {competitor}? Need migration help.",
        "Team setup questions - how many seats do I need for {count} users?",
        "Initial configuration help needed. What are best practice settings?"
    ],
    'user_management': [
        "How do I add users to my workspace? Can't find the option.",
        "Need to remove user access - they left the company. Urgent.",
        "Can I change user roles? Want to make {name} an admin.",
        "User permissions not working correctly. Everyone can see everything.",
        "Bulk user import - have {count} users to add. CSV upload available?"
    ]
}

# ============================================================================
# OTHER INDUSTRIES (13 tickets - 5%) - Should become "general"
# ============================================================================

OTHER_INDUSTRY_TEMPLATES = [
    # Healthcare
    "Need to reschedule my doctor appointment for next week. Patient ID: {id}",
    "Prescription refill request for {medication}. Last refill was {months} months ago.",
    "Haven't received my lab test results yet. It's been {days} days.",
    
    # Fintech
    "Seeing unauthorized transaction of ${amount} on my account. Possible fraud.",
    "My card was declined at merchant but I have sufficient balance.",
    "Need statement for tax purposes. Account number: {account}",
    
    # Telecom
    "Internet down for {hours} hours. No connection. Service ID: {id}",
    "Mobile plan - want to upgrade to unlimited data. Current plan: {plan}",
    
    # Education
    "Can't access course materials. Getting 404 error. Course: {course}",
    "Grade shows as F but I submitted assignment on time. Need review.",
    
    # Real Estate
    "Maintenance request - AC not working in unit {unit}.",
    "Rent payment didn't go through. Transaction failed. Lease #: {lease}",
    
    # General Services
    "Appointment confirmation didn't arrive. Booking reference: {ref}"
]

# ============================================================================
# EDGE CASES (12 tickets - 5%) - Ambiguous/Mixed
# ============================================================================

EDGE_CASE_TEMPLATES = [
    "Hi, just wanted to say I love your product! Keep up the great work!",
    "Quick question - are you hiring? Saw the role on LinkedIn.",
    "This is a test ticket. Please ignore.",
    "Can you recommend a good competitor? Your product doesn't fit our needs.",
    "Urgent: CEO wants demo ASAP. Who should I contact?",
    "Is this the right email for partnerships?",
    "How much does your enterprise plan cost?",
    "Do you have an office in {city}? Want to visit.",
    "Press inquiry - writing article about your industry.",
    "Random feedback - UI could be better.",
    "Just browsing, no specific question.",
    "Does your product work with {random_tool}?"
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_placeholders():
    """Generate random placeholder values"""
    return {
        'order_id': random.randint(10000, 99999),
        'tracking': f"{random.choice(['USPS', 'FEDEX', 'UPS'])}{random.randint(100000000, 999999999)}",
        'email': f"customer{random.randint(100, 999)}@{random.choice(['gmail.com', 'yahoo.com', 'company.com'])}",
        'username': f"user{random.randint(1000, 9999)}",
        'promo_code': f"{random.choice(['SAVE', 'DEAL', 'FIRST', 'VIP'])}{random.randint(10, 99)}",
        'days': random.randint(1, 14),
        'card_last4': random.randint(1000, 9999),
        'attempts': random.randint(2, 5),
        'amount': random.randint(50, 500),
        'different_amount': random.randint(50, 500),
        'quantity': random.randint(1, 5),
        'correct_quantity': random.randint(1, 5),
        'discount': random.choice([10, 15, 20, 25, 30]),
        'date': (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        'version': f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
        'count': random.randint(10, 500),
        'seconds': random.randint(10, 60),
        'minutes': random.randint(5, 30),
        'hours': random.randint(2, 48),
        'old_ms': random.randint(100, 300),
        'new_ms': random.randint(1000, 3000),
        'percent': random.randint(10, 90),
        'step': random.randint(2, 5),
        'competitor': random.choice(['Competitor A', 'Other Tool', 'Previous System']),
        'name': random.choice(['John', 'Sarah', 'Mike', 'Emily']),
        'provider': random.choice(['Google', 'Microsoft', 'Okta']),
        'medication': random.choice(['Medication A', 'Prescription B']),
        'months': random.randint(1, 6),
        'account': random.randint(100000, 999999),
        'plan': random.choice(['Basic', 'Standard', 'Premium']),
        'course': f"CS{random.randint(100, 499)}",
        'unit': f"{random.randint(1, 20)}{random.choice(['A', 'B', 'C'])}",
        'lease': random.randint(1000, 9999),
        'ref': f"REF{random.randint(10000, 99999)}",
        'id': random.randint(1000, 9999),
        'city': random.choice(['San Francisco', 'New York', 'London', 'Berlin']),
        'random_tool': random.choice(['Jira', 'Asana', 'Monday.com', 'ClickUp', 'Trello'])
    }

def create_ticket(description, expected_category, expected_industry, priority="new"):
    """Create a ticket object"""
    return {
        'id': random.randint(1000, 999999),
        'subject': description[:50] + "...",
        'description': description,
        'status': 'new',
        'priority': priority,
        'created_at': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        'expected_category': expected_category,
        'expected_industry': expected_industry
    }

def generate_tickets(count=250):
    """Generate complete test dataset"""
    tickets = []
    
    print(f"Generating {count} test tickets...")
    print("="*80)
    
    # 1. E-COMMERCE TICKETS (45% = 112 tickets)
    ecommerce_count = int(count * 0.45)
    print(f"Creating {ecommerce_count} e-commerce tickets...")
    
    categories = list(ECOMMERCE_TEMPLATES.keys())
    tickets_per_category = ecommerce_count // len(categories)
    
    for category in categories:
        templates = ECOMMERCE_TEMPLATES[category]
        for _ in range(tickets_per_category):
            template = random.choice(templates)
            description = template.format(**generate_placeholders())
            tickets.append(create_ticket(description, category, 'ecommerce'))
    
    # 2. SAAS TICKETS (45% = 113 tickets)
    saas_count = int(count * 0.45)
    print(f"Creating {saas_count} SaaS tickets...")
    
    categories = list(SAAS_TEMPLATES.keys())
    tickets_per_category = saas_count // len(categories)
    
    for category in categories:
        templates = SAAS_TEMPLATES[category]
        for _ in range(tickets_per_category):
            template = random.choice(templates)
            description = template.format(**generate_placeholders())
            tickets.append(create_ticket(description, category, 'saas'))
    
    # 3. OTHER INDUSTRIES (5% = 13 tickets) - Should become "general"
    other_count = int(count * 0.05)
    print(f"Creating {other_count} other industry tickets (should→general)...")
    
    for _ in range(other_count):
        template = random.choice(OTHER_INDUSTRY_TEMPLATES)
        description = template.format(**generate_placeholders())
        tickets.append(create_ticket(description, 'general', 'general'))
    
    # 4. EDGE CASES (5% = 12 tickets) - Ambiguous
    edge_count = count - len(tickets)  # Fill remaining
    print(f"Creating {edge_count} edge case tickets...")
    
    for _ in range(edge_count):
        template = random.choice(EDGE_CASE_TEMPLATES)
        description = template.format(**generate_placeholders())
        tickets.append(create_ticket(description, 'general', 'general'))
    
    # Shuffle tickets
    random.shuffle(tickets)
    
    # Assign sequential IDs
    for i, ticket in enumerate(tickets, 1):
        ticket['id'] = i
    
    return tickets

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("MULTI-INDUSTRY TEST DATA GENERATOR")
    print("="*80)
    print()
    
    # Generate tickets
    tickets = generate_tickets(250)
    
    # Save to JSON
    filename = f"test_tickets_multi_industry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_tickets': len(tickets),
        'distribution': {
            'ecommerce': len([t for t in tickets if t['expected_industry'] == 'ecommerce']),
            'saas': len([t for t in tickets if t['expected_industry'] == 'saas']),
            'general': len([t for t in tickets if t['expected_industry'] == 'general'])
        },
        'tickets': tickets
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print()
    print("="*80)
    print("GENERATION COMPLETE")
    print("="*80)
    print(f"Total Tickets: {len(tickets)}")
    print()
    print("Distribution:")
    print(f"  E-commerce: {output['distribution']['ecommerce']} ({output['distribution']['ecommerce']/len(tickets)*100:.1f}%)")
    print(f"  SaaS:       {output['distribution']['saas']} ({output['distribution']['saas']/len(tickets)*100:.1f}%)")
    print(f"  General:    {output['distribution']['general']} ({output['distribution']['general']/len(tickets)*100:.1f}%)")
    print()
    print(f"✅ Saved to: {filename}")
    print()
    print("="*80)
    print("EXPECTED RESULTS WHEN TESTED:")
    print("="*80)
    print("Industry Detection:")
    print("  - Ecommerce tickets → 'ecommerce' industry ✅")
    print("  - SaaS tickets → 'saas' industry ✅")
    print("  - Other/Edge cases → 'general' industry ✅")
    print()
    print("Category Accuracy:")
    print("  - E-commerce: 10 specific categories")
    print("  - SaaS: 11 specific categories")
    print("  - Others: 'general' category")
    print()
    print("🎯 TARGET: 'General' rate should be ~10% (25 tickets)")
    print("   90% should get specific e-commerce/SaaS categories")
    print()
    print("="*80)
    print()
    print("SAMPLE TICKETS (First 5):")
    print("="*80)
    for i, ticket in enumerate(tickets[:5], 1):
        print(f"\n#{i} | Expected: {ticket['expected_industry']} → {ticket['expected_category']}")
        print(f"    {ticket['description'][:100]}...")
    print()
    print("="*80)
    print("✅ Ready to test! Run:")
    print(f"   python test_multi_industry_processor.py {filename}")
    print("="*80)
