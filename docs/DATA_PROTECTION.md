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

## Logging & Audit Trail

- ✅ Logs stored in `/logs/django.log` (not publicly accessible, 404)
- ✅ PII masking filter active on all handlers
- ✅ Log rotation configured via server (not in Django)
- ⚠️ Log file not encrypted (OS-level file permissions only)

## Backup & Disaster Recovery

- 📋 **Database backups**: Handled by PostgreSQL provider (Render)
- 📋 **Backup encryption**: Provider default (check with hosting provider)
- 📋 **Backup retention**: Document in ops manual
- 📋 **Recovery testing**: Schedule quarterly

## Data Retention & Deletion

- 📋 **No automated retention policies** currently implemented
- 📋 **Recommended**: 
  - OTP records: delete after 24 hours
  - Login logs: delete after 90 days
  - Payment logs: keep per compliance (check local regs)
  - User data: honor deletion requests (GDPR/CCPA)

## Media Files & Supabase Storage

- ✅ **Supabase**: Provider-managed encryption
- ✅ **Secure URLs**: Signed tokens prevent direct access
- ⚠️ **Backup**: Supabase handles (verify in provider dashboard)
- 📋 **Retention policy**: Not yet defined

## Future Improvements
- Field-level encryption for phone numbers (if PCI-DSS audit required)
- Database-level encryption at rest (AWS RDS encryption, etc.)
- Log file encryption (OS-level or application-level)
- Implement automated data retention policies
- Key rotation policy for encryption keys
- Document backup/recovery procedures
- GDPR right-to-be-forgotten implementation
