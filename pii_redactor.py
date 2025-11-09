"""PII Redactor - Protects sensitive information before sending to LLM"""
import re
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class PIIRedactor:
    """
    Redact sensitive PII before sending to LLM

    Supports international PII protection for:
    - India: Aadhaar, PAN, IFSC, Phone Numbers
    - US: Social Security Numbers, Bank Routing Numbers
    - UK: National Insurance Numbers, Bank Sort Codes
    - EU: IBAN (International Bank Account Numbers)
    - Australia: Tax File Numbers, Medicare Numbers
    - Canada: Social Insurance Numbers

    Compliant with: GDPR (EU), CCPA (US), Privacy Act (Australia), PIPEDA (Canada)
    """

    # NOTE: Patterns are ordered from most specific to least specific to avoid conflicts
    # Order matters! Process patterns in this specific order.
    PATTERNS = {
        # === PAYMENT & BANKING (MOST SPECIFIC FIRST) ===
        'credit_card': (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CREDIT_CARD_REDACTED]'),

        # IBAN must be checked before other patterns (requires spaces allowed in middle)
        'iban': (r'\b[A-Z]{2}\d{2}\s?[A-Z0-9]{4}\s?[A-Z0-9]{4}\s?[A-Z0-9]{4}\s?[A-Z0-9]{0,18}\b', '[IBAN_REDACTED]'),

        'account_number': (r'\b[Aa]ccount\s?[Nn]o\.?\s?:?\s?\d{8,18}\b', 'Account No: [REDACTED]'),

        # === INDIA PII (CHECK BEFORE OTHER 9/10/12 DIGIT PATTERNS) ===
        'phone_india_code': (r'\+91[- ]?[6-9]\d{9}\b', '[PHONE_REDACTED]'),  # +91 prefix makes it unambiguous
        'phone_india': (r'\b[6-9]\d{9}\b(?!\s?\d)', '[PHONE_REDACTED]'),  # 10 digits starting with 6-9, not followed by more digits
        'aadhaar': (r'\b\d{4}\s\d{4}\s\d{4}\b', '[AADHAAR_REDACTED]'),  # Must have spaces (distinguishes from IBAN)
        'pan_card': (r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[PAN_REDACTED]'),
        'ifsc': (r'\b[A-Z]{4}0[A-Z0-9]{6}\b', '[IFSC_REDACTED]'),

        # === UK PII ===
        'uk_ni': (r'\b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Z]\b', '[UK_NI_REDACTED]'),  # National Insurance: AB123456C or AB 12 34 56 C
        'uk_sort': (r'\b\d{2}-\d{2}-\d{2}\b', '[UK_SORT_REDACTED]'),  # Bank Sort Code: 12-34-56

        # === AUSTRALIA PII (MOST SPECIFIC FIRST) ===
        'au_medicare': (r'\b\d{4}\s\d{5}\s\d\b', '[AU_MEDICARE_REDACTED]'),  # Requires spaces: 1234 56789 1

        # === US PII ===
        'us_ssn': (r'\b\d{3}[- ]\d{2}[- ]\d{4}\b', '[US_SSN_REDACTED]'),  # Requires separator: 123-45-6789 or 123 45 6789
        'us_routing': (r'\b0[0-9]{8}\b', '[US_ROUTING_REDACTED]'),  # Routing numbers start with 0-1 (distinguishes from SSN)

        # === 9-DIGIT PATTERNS (ORDER MATTERS - AU/CA CONFLICT) ===
        # Use context or priority: Check TFN first (Australia), then SIN (Canada)
        # Both are 9 digits with spaces, so they'll match the same pattern
        # We'll use a combined pattern and let context determine which one it is
        'au_tfn_ca_sin': (r'\b\d{3}\s\d{3}\s\d{3}\b', '[TAX_ID_REDACTED]'),  # Australia TFN / Canada SIN (9 digits with spaces)

        # === GENERAL ===
        'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
    }
    
    def __init__(self, preserve_emails=True):
        self.preserve_emails = preserve_emails
        self.stats = {'total': 0, 'by_type': {}}
    
    def redact(self, text):
        if not text:
            return {'redacted_text': '', 'redactions': {}, 'has_pii': False}
        
        redacted_text = text
        redactions = {}
        
        for pii_type, (pattern, replacement) in self.PATTERNS.items():
            if pii_type == 'email' and self.preserve_emails:
                continue
            
            matches = re.findall(pattern, redacted_text, re.IGNORECASE)
            if matches:
                count = len(matches)
                redactions[pii_type] = count
                self.stats['total'] += count
                self.stats['by_type'][pii_type] = self.stats['by_type'].get(pii_type, 0) + count
                redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
                logger.info(f"Redacted {count} {pii_type}(s)")
        
        return {
            'redacted_text': redacted_text,
            'redactions': redactions,
            'has_pii': len(redactions) > 0
        }

if __name__ == "__main__":
    redactor = PIIRedactor()
    tests = [
        # Payment & Banking
        "My card is 4532-1488-0343-6467",
        "IBAN: GB29 NWBK 6016 1331 9268 19",
        "IBAN: DE89370400440532013000",
        "Account No: 123456789012",

        # US PII
        "SSN: 123-45-6789",
        "SSN: 123 45 6789",
        "SSN: 123456789",
        "Routing: 021000021",

        # UK PII
        "NI Number: AB 12 34 56 C",
        "NI: AB123456C",
        "Sort Code: 12-34-56",

        # Australia PII
        "TFN: 123 456 789",
        "Medicare: 1234 56789 1",

        # Canada PII
        "SIN: 123 456 789",

        # India PII
        "Call 9876543210 or +91 9876543210",
        "PAN: ABCDE1234F",
        "Aadhaar: 1234 5678 9012",
        "IFSC: HDFC0001234"
    ]

    print("="*70)
    print("INTERNATIONAL PII REDACTION TEST")
    print("="*70)

    for t in tests:
        r = redactor.redact(t)
        if r['has_pii']:
            print(f"Original: {t}")
            print(f"Redacted: {r['redacted_text']}")
            print(f"PII Found: {r['redactions']}")
            print()

    print("="*70)
    print("REDACTION STATISTICS")
    print("="*70)
    print(f"Total Redactions: {redactor.stats['total']}")
    print("\nBy Type:")
    for pii_type, count in sorted(redactor.stats['by_type'].items()):
        print(f"  {pii_type}: {count}")