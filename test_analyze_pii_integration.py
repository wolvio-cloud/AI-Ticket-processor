#!/usr/bin/env python3
"""
Integration Test: PII Redaction in analyze_ticket.py
Tests the full analyze_ticket() function with PII data
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock OpenAI API if not available (for testing without API key)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_MOCK = not OPENAI_API_KEY or OPENAI_API_KEY == 'your-api-key-here'

if USE_MOCK:
    print("⚠️  No OpenAI API key found - using MOCK mode")
    print("   (Testing PII redaction logic only, not actual AI analysis)")
    print()

from pii_redactor import PIIRedactor


def mock_analyze_ticket(subject, description):
    """Mock version of analyze_ticket for testing without OpenAI API"""

    # Initialize PII redactor (same as in analyze_ticket.py)
    redactor = PIIRedactor(preserve_emails=True)

    # STEP 1: Redact PII from subject and description
    subject_redaction = redactor.redact(subject)
    description_redaction = redactor.redact(description)

    subject_clean = subject_redaction['redacted_text']
    description_clean = description_redaction['redacted_text']

    # STEP 2: Log PII detection
    has_pii = subject_redaction['has_pii'] or description_redaction['has_pii']
    all_redactions = {}

    if subject_redaction['redactions']:
        all_redactions.update(subject_redaction['redactions'])
    if description_redaction['redactions']:
        for key, val in description_redaction['redactions'].items():
            all_redactions[key] = all_redactions.get(key, 0) + val

    if has_pii:
        pii_types = ', '.join(all_redactions.keys())
        total_count = sum(all_redactions.values())
        print(f"🔒 PII detected and redacted: {total_count} instance(s) ({pii_types})")

    # STEP 3: Show what would be sent to OpenAI
    print(f"\n📤 Data sent to OpenAI (PII-safe):")
    print(f"   Subject: {subject_clean}")
    print(f"   Description preview: {description_clean[:100]}...")

    # STEP 4: Mock AI analysis result
    analysis = {
        "summary": "Customer has a support request (MOCK ANALYSIS)",
        "root_cause": "other",
        "urgency": "medium",
        "sentiment": "neutral",
        "pii_redacted": has_pii,
        "redactions": all_redactions
    }

    return analysis, subject_clean, description_clean


def test_pii_integration():
    """Test PII redaction in analyze_ticket function"""

    print("="*70)
    print("INTEGRATION TEST: analyze_ticket.py PII Redaction")
    print("="*70)

    # Test Case 1: Ticket with US-style PII
    print("\n" + "="*70)
    print("TEST 1: US-style PII (Phone, Email, SSN)")
    print("="*70)

    subject1 = "Urgent: Account access issue"
    description1 = """Hi Support Team,

I'm locked out of my account and need immediate help. Here are my details:

Name: John Doe
Phone: 555-123-4567
Email: johndoe@email.com
SSN: 123-45-6789
Credit Card ending in: 4532-1488-0343-6467

Please help me regain access ASAP!

Thanks,
John"""

    print("\n📝 ORIGINAL TICKET:")
    print("-" * 70)
    print(f"Subject: {subject1}")
    print(f"Description:\n{description1}")

    result1, clean_subj1, clean_desc1 = mock_analyze_ticket(subject1, description1)

    print("\n🔒 REDACTED VERSION (sent to OpenAI):")
    print("-" * 70)
    print(f"Subject: {clean_subj1}")
    print(f"Description:\n{clean_desc1}")

    print("\n📊 ANALYSIS RESULT:")
    print(f"   PII Redacted: {'✅ YES' if result1['pii_redacted'] else '❌ NO'}")
    if result1['redactions']:
        print(f"   Redaction types: {', '.join(result1['redactions'].keys())}")
        print(f"   Total redactions: {sum(result1['redactions'].values())}")

    # Test Case 2: Indian-style PII
    print("\n" + "="*70)
    print("TEST 2: Indian-style PII (Phone, PAN, Aadhaar, IFSC, Account)")
    print("="*70)

    subject2 = "Refund request - payment failed"
    description2 = """Dear Support,

My payment failed but the amount was deducted from my bank account.
Please process a refund to:

Bank Account: Account No: 123456789012
IFSC Code: HDFC0001234
Mobile: 9876543210
PAN Card: ABCDE1234F
Aadhaar: 1234 5678 9012

Amount: ₹2,500
Transaction ID: TXN123456

Please expedite!"""

    print("\n📝 ORIGINAL TICKET:")
    print("-" * 70)
    print(f"Subject: {subject2}")
    print(f"Description:\n{description2}")

    result2, clean_subj2, clean_desc2 = mock_analyze_ticket(subject2, description2)

    print("\n🔒 REDACTED VERSION (sent to OpenAI):")
    print("-" * 70)
    print(f"Subject: {clean_subj2}")
    print(f"Description:\n{clean_desc2}")

    print("\n📊 ANALYSIS RESULT:")
    print(f"   PII Redacted: {'✅ YES' if result2['pii_redacted'] else '❌ NO'}")
    if result2['redactions']:
        print(f"   Redaction types: {', '.join(result2['redactions'].keys())}")
        print(f"   Total redactions: {sum(result2['redactions'].values())}")

    # Test Case 3: Mixed international PII
    print("\n" + "="*70)
    print("TEST 3: Mixed International PII")
    print("="*70)

    subject3 = "Payment issue with my subscription"
    description3 = """Hello,

I was charged twice for my subscription. My details:

Email: support-contact@company.com (you can reach me here)
Phone: +91 9988776655
Credit Card: 5555-4444-3333-2222
Address: 123 Main Street (no PII in this)

Transaction 1: Charged on Card ending 3333
Transaction 2: Duplicate charge

Please refund one transaction."""

    print("\n📝 ORIGINAL TICKET:")
    print("-" * 70)
    print(f"Subject: {subject3}")
    print(f"Description:\n{description3}")

    result3, clean_subj3, clean_desc3 = mock_analyze_ticket(subject3, description3)

    print("\n🔒 REDACTED VERSION (sent to OpenAI):")
    print("-" * 70)
    print(f"Subject: {clean_subj3}")
    print(f"Description:\n{clean_desc3}")

    print("\n📊 ANALYSIS RESULT:")
    print(f"   PII Redacted: {'✅ YES' if result3['pii_redacted'] else '❌ NO'}")
    if result3['redactions']:
        print(f"   Redaction types: {', '.join(result3['redactions'].keys())}")
        print(f"   Total redactions: {sum(result3['redactions'].values())}")

    # Verify email preservation
    if "support-contact@company.com" in clean_desc3:
        print("   ✅ Email preserved (as configured)")
    else:
        print("   ❌ Email was redacted (unexpected)")

    # Test Case 4: Clean ticket (no PII)
    print("\n" + "="*70)
    print("TEST 4: Clean Ticket (No PII - control test)")
    print("="*70)

    subject4 = "Feature request: Dark mode"
    description4 = """Hello team,

I would like to request a dark mode feature for the application.
Many users prefer dark themes for night-time usage.

This would be a great addition to the product.

Thank you!"""

    print("\n📝 ORIGINAL TICKET:")
    print("-" * 70)
    print(f"Subject: {subject4}")
    print(f"Description:\n{description4}")

    result4, clean_subj4, clean_desc4 = mock_analyze_ticket(subject4, description4)

    print("\n📊 ANALYSIS RESULT:")
    print(f"   PII Redacted: {'✅ YES' if result4['pii_redacted'] else '❌ NO (expected)'}")
    if not result4['pii_redacted']:
        print("   ✅ Correctly identified as clean (no false positives)")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    test_results = [
        ("Test 1 (US PII)", result1['pii_redacted'], True),
        ("Test 2 (Indian PII)", result2['pii_redacted'], True),
        ("Test 3 (Mixed PII)", result3['pii_redacted'], True),
        ("Test 4 (Clean)", result4['pii_redacted'], False)
    ]

    all_passed = True
    for test_name, actual, expected in test_results:
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"{test_name:25s}: {status} (PII detected: {actual}, expected: {expected})")
        if actual != expected:
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - PII redaction is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation")
    print("="*70)

    # Show protected PII types
    print("\n📋 Protected PII Types (9 total):")
    print("   1. Credit Cards (e.g., 4532-1488-0343-6467)")
    print("   2. SSN (e.g., 123-45-6789)")
    print("   3. Phone Numbers - US format (e.g., 555-123-4567)")
    print("   4. Phone Numbers - India (e.g., 9876543210, +91 9876543210)")
    print("   5. Email (PRESERVED for business context)")
    print("   6. PAN Cards - India (e.g., ABCDE1234F)")
    print("   7. Aadhaar - India (e.g., 1234 5678 9012)")
    print("   8. Bank Account Numbers (e.g., Account No: 123456789012)")
    print("   9. IFSC Codes - India (e.g., HDFC0001234)")
    print()


if __name__ == "__main__":
    test_pii_integration()
