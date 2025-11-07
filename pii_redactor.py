"""PII Redactor - Protects sensitive information before sending to LLM"""
import re
import logging

logger = logging.getLogger(__name__)

class PIIRedactor:
    """Redact sensitive PII before sending to LLM"""
    
    PATTERNS = {
        'credit_card': (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CREDIT_CARD_REDACTED]'),
        'ssn': (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),
        'phone_india': (r'\b[6-9]\d{9}\b', '[PHONE_REDACTED]'),
        'phone_india_code': (r'\+91[- ]?[6-9]\d{9}\b', '[PHONE_REDACTED]'),
        'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
        'pan_card': (r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[PAN_REDACTED]'),
        'aadhaar': (r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[AADHAAR_REDACTED]'),
        'account_number': (r'\b[Aa]ccount\s?[Nn]o\.?\s?:?\s?\d{8,18}\b', 'Account No: [REDACTED]'),
        'ifsc': (r'\b[A-Z]{4}0[A-Z0-9]{6}\b', '[IFSC_REDACTED]')
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
        "My card is 4532-1488-0343-6467",
        "Call 9876543210 or +91 9876543210",
        "PAN: ABCDE1234F, Aadhaar: 1234 5678 9012"
    ]
    for t in tests:
        r = redactor.redact(t)
        print(f"Original: {t}")
        print(f"Redacted: {r['redacted_text']}\n")