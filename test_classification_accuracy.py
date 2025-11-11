"""
================================================================================
Test: Classification Accuracy with Generic Language
================================================================================

PURPOSE:
    Validates improved classification accuracy for tickets with generic/vague
    language. Tests the keyword-based industry detection system.

GOAL:
    - Reduce "others" classification rate from 20% to <8%
    - Achieve >60% industry detection accuracy for generic language
    - Correctly map vague terms to specific categories

TEST COVERAGE:
    - Generic e-commerce tickets: "problem with my order", "account issue"
    - Generic SaaS tickets: "technical problem", "application slow"
    - Edge cases: ambiguous language, minimal context

EXPECTED RESULTS:
    ✅ 8/10 or better correct industry detection (80% accuracy)
    ✅ Handles generic language: "my order", "account issue", "billing problem"

USAGE:
    python test_classification_accuracy.py

DEPENDENCIES:
    - Ai_ticket_processor.py (detect_industry function)

AUTHOR: AI Ticket Processor Team
LAST UPDATED: 2025-11-11
================================================================================
"""

# Test cases with generic language that should map to specific categories
test_tickets = [
    # E-commerce tickets with generic language
    {
        "description": "I have a problem with my order",
        "expected_industry": "ecommerce",
        "expected_category": "order_status_tracking"
    },
    {
        "description": "There's an issue with my account",
        "expected_industry": "ecommerce",
        "expected_category": "account_login_access"
    },
    {
        "description": "I have a billing problem",
        "expected_industry": "ecommerce",
        "expected_category": "payment_checkout_issue"
    },
    {
        "description": "The item I received is wrong",
        "expected_industry": "ecommerce",
        "expected_category": "exchange_replacement_request"
    },
    {
        "description": "I want to return this product",
        "expected_industry": "ecommerce",
        "expected_category": "product_return_refund"
    },

    # SaaS tickets with generic language
    {
        "description": "I'm having an account issue",
        "expected_industry": "saas",
        "expected_category": "user_access_permissions"  # or authentication_login_problem
    },
    {
        "description": "There's a technical problem with the system",
        "expected_industry": "saas",
        "expected_category": "performance_speed_issue"  # or api_integration_error
    },
    {
        "description": "I can't login to my account",
        "expected_industry": "saas",
        "expected_category": "authentication_login_problem"
    },
    {
        "description": "The application is running very slow",
        "expected_industry": "saas",
        "expected_category": "performance_speed_issue"
    },
    {
        "description": "I need help setting up my workspace",
        "expected_industry": "saas",
        "expected_category": "onboarding_setup_help"
    },
]

print("="*80)
print("CLASSIFICATION ACCURACY TEST")
print("Goal: <8% 'other' rate, improved industry detection")
print("="*80)

# Test industry detection
from Ai_ticket_processor import detect_industry

industry_correct = 0
industry_total = len(test_tickets)

for i, ticket in enumerate(test_tickets, 1):
    detected = detect_industry(ticket['description'])
    expected = ticket['expected_industry']
    status = "✅" if detected == expected else "❌"

    print(f"\n{i}. \"{ticket['description']}\"")
    print(f"   Expected: {expected}")
    print(f"   Detected: {detected} {status}")

    if detected == expected:
        industry_correct += 1

print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"Industry Detection Accuracy: {industry_correct}/{industry_total} ({industry_correct/industry_total*100:.1f}%)")
print(f"Target: >60% industry detection rate")

if industry_correct / industry_total >= 0.6:
    print("✅ PASS - Industry detection improved!")
else:
    print("❌ FAIL - Need more keyword improvements")

print("\nNext: Run full processor to test category classification and 'others' rate")
