"""
Logging filters to prevent PII (Personally Identifiable Information)
from being logged.
"""

import re
import logging


class PIIMaskingFilter(logging.Filter):
    """
    Redact sensitive data from log records.
    Masks: phone numbers, emails, credit card-like patterns, amounts.
    """
    
    # Regex patterns for sensitive data
    PATTERNS = {
        'phone': r'(?:\+?\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'auth_header': r'Authorization["\']?\s*[:=]\s*["\']?Bearer\s+[A-Za-z0-9._\-]*',
        'amount': r'(?:amount|price|total|cost|payment)\s*[:=]\s*(\d+(?:\.\d{2})?)',
    }
    
    def filter(self, record):
        """Redact PII from log record message and args"""
        if record.msg:
            record.msg = self._redact(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._redact(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._redact(str(arg)) for arg in record.args)
        return True
    
    def _redact(self, text):
        """Redact sensitive patterns from text"""
        # Phone numbers: show only last 4 digits
        text = re.sub(
            self.PATTERNS['phone'],
            r'***-***-\3',
            text
        )
        
        # Email: show only domain
        text = re.sub(
            self.PATTERNS['email'],
            lambda m: f'[***@{m.group(0).split("@")[1]}]',
            text
        )
        
        # Credit cards: show only last 4 digits
        text = re.sub(
            self.PATTERNS['card'],
            '****-****-****-XXXX',
            text
        )
        
        # Authorization headers: redact token
        text = re.sub(
            self.PATTERNS['auth_header'],
            'Authorization: Bearer [REDACTED]',
            text,
            flags=re.IGNORECASE
        )
        
        # Amounts in requests (show as [***])
        text = re.sub(
            self.PATTERNS['amount'],
            r'\1: [***]',
            text,
            flags=re.IGNORECASE
        )
        
        return text
