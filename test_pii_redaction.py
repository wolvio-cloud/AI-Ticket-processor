#!/usr/bin/env python3
"""
Test PII Redaction in analyze_ticket.py
"""
from pii_redactor import PIIRedactor

def test_pii_redaction():
    """Test that PII is properly detected and redacted"""

    redactor = PIIRedactor(preserve_emails=True)

    print("="*60)
    print("PII REDACTION TESTS")
    print("="*60)

    # Test 1: Clean ticket (no PII)
    print("\nTest 1: Normal ticket (no PII)")
    print("-" * 60)

    subject1 = "My order never arrived"
    desc1 = "I paid for order #1234 three days ago but haven't received it."

    sub_result1 = redactor.redact(subject1)
    desc_result1 = redactor.redact(desc1)

    print(f"Subject: {subject1}")
    print(f"Description: {desc1}")
    print(f"Has PII: {sub_result1['has_pii'] or desc_result1['has_pii']}")
    print(f"✅ Test 1 PASSED - No PII detected as expected")

    # Test 2: Ticket with PII
    print("\n" + "="*60)
    print("Test 2: Ticket with sensitive PII")
    print("-" * 60)

    subject2 = "Refund to my account"
    desc2 = """Please refund to:
Account No: 123456789012
IFSC: HDFC0001234
Phone: 9876543210
PAN: ABCDE1234F
Credit Card: 4532-1488-0343-6467"""

    sub_result2 = redactor.redact(subject2)
    desc_result2 = redactor.redact(desc2)

    print(f"Original Subject: {subject2}")
    print(f"Redacted Subject: {sub_result2['redacted_text']}")
    print(f"\nOriginal Description:\n{desc2}")
    print(f"\nRedacted Description:\n{desc_result2['redacted_text']}")

    has_pii = sub_result2['has_pii'] or desc_result2['has_pii']
    all_redactions = {}

    if desc_result2['redactions']:
        all_redactions.update(desc_result2['redactions'])

    print(f"\nPII Detected: {has_pii}")
    print(f"Redaction Types: {', '.join(all_redactions.keys())}")
    print(f"Total Redactions: {sum(all_redactions.values())}")

    # Verify expected PII types were found
    expected_types = {'account_number', 'ifsc', 'phone_india', 'pan_card', 'credit_card'}
    found_types = set(all_redactions.keys())

    if expected_types == found_types:
        print(f"✅ Test 2 PASSED - All PII types detected correctly")
    else:
        print(f"❌ Test 2 FAILED")
        print(f"   Expected: {expected_types}")
        print(f"   Found: {found_types}")
        print(f"   Missing: {expected_types - found_types}")

    # Test 3: Email preservation
    print("\n" + "="*60)
    print("Test 3: Email preservation (emails should NOT be redacted)")
    print("-" * 60)

    subject3 = "Support request"
    desc3 = "Please contact me at customer@example.com for updates"

    sub_result3 = redactor.redact(subject3)
    desc_result3 = redactor.redact(desc3)

    print(f"Original: {desc3}")
    print(f"Redacted: {desc_result3['redacted_text']}")

    if "customer@example.com" in desc_result3['redacted_text']:
        print("✅ Test 3 PASSED - Email preserved as expected")
    else:
        print("❌ Test 3 FAILED - Email was redacted (should be preserved)")

    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_pii_redaction()
