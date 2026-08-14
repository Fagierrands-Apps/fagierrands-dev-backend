# Data Protection Strategy

## Encryption at Rest

### ✅ Already Implemented
- **OTP codes**: Hashed with SHA256 before storage (not plaintext)
- **JWT tokens**: Blacklisted on logout (tokens.Token_Blacklist table)
- **Passwords**: Django's PBKDF2 hashing (configurable cost)
- **SSL/TLS**: HTTPS enforced in production, HSTS enabled
- **Supabase storage**: Files encrypted by Supabase (provider-managed)

### ⚠️ Gaps (Not Encrypted at Rest)
- **Phone numbers**: Stored plaintext (needed for SMS/lookup; encryption adds complexity)
- **Payment amounts**: Stored in Order model (needed for reporting; consider field-level encryption if PCI-DSS required)
- **Rider verification documents**: URLs stored (actual files are on Supabase encrypted storage)

### 📋 Logging
- **PII masking**: All phone numbers, emails, payment amounts, auth tokens redacted from logs
- Log file location: `/logs/django.log` (protected via file permissions)

## Data in Transit
- ✅ HTTPS/TLS enforced (SECURE_SSL_REDIRECT=True)
- ✅ HSTS enabled (31536000 seconds)
- ✅ Secure cookies (HttpOnly, SameSite, Secure flags)

## Database Access
- ✅ PostgreSQL with SSL required (ssl_require=True)
- ✅ Credentials in environment variables (never in code)
- ✅ Connection pooling enabled

## Future Improvements
- Field-level encryption for phone numbers (if PCI-DSS audit required)
- Database-level encryption (AWS RDS encryption, etc.)
- Key rotation policy for encryption keys
- Data retention/deletion policies (GDPR compliance)
