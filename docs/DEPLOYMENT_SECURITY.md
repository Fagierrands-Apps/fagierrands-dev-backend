# Deployment & Infrastructure Security

## Auto-Deployment Pipeline

**Flow:** Commit to `main` → GitHub Actions → FTP to cPanel → App Restarts

### ✅ Protections in Place

- FTPS (encrypted) for file transfer
- Protected files excluded: `.env`, `db.sqlite3`, `logs/`
- Passenger WSGI isolation
- GitHub Actions secrets (credentials never in plaintext)

### ⚠️ High-Risk Areas

**1. GitHub Branch Protection**
- [ ] TODO: Enable branch protection on `main`
  - Require pull request reviews (minimum 1)
  - Require status checks (GitHub Actions CI)
  - Require code owner review (if applicable)
  - Require up-to-date branches
- [ ] TODO: Restrict force pushes
- [ ] TODO: Require PRs before merges (no direct commits)

**2. GitHub Secrets Management**
- ✅ Stored in GitHub Settings → Secrets
- [ ] TODO: Document secret rotation schedule (quarterly minimum)
- [ ] TODO: Audit who has access to secrets

**3. Deployment Credentials**
- [ ] TODO: Use deploy-only account with minimal cPanel permissions
- [ ] TODO: Rotate FTP credentials quarterly
- [ ] TODO: Monitor failed deployments

## Environment Configuration

### ✅ Strict Validation
- `DEBUG`: Defaults to False (safe), warns if not set
- `ALLOWED_HOSTS`: Requires explicit config in production
- `SECRET_KEY`: Warns if not set (dev only)

### 📋 Missing Pieces
- [ ] No Web Application Firewall (WAF) — consider Cloudflare
- [ ] No DDoS protection — consider Cloudflare or AWS Shield
- [ ] No WAF rules for attack patterns

## cPanel Security

- ✅ FTPS (encrypted transfer)
- [ ] TODO: Disable unnecessary cPanel services
- [ ] TODO: Audit cPanel user permissions
- [ ] TODO: Document firewall rules
- [ ] TODO: Monitor cPanel access logs

## CI/CD Pipeline

### Current Setup
```
Push to main
  ↓
GitHub Actions runs:
  - pip install requirements
  - python manage.py collectstatic
  - python manage.py migrate
  - python manage.py createcachetable
  - Create admin user (if needed)
  ↓
Deploy to cPanel via FTP
  ↓
Passenger restarts app
```

### Risks
- [ ] No pre-deployment tests running (security tests, linting)
- [ ] No rollback mechanism documented
- [ ] No deployment notifications/alerts

## Recommended Immediate Actions

1. **Enable GitHub branch protection** (HIGH PRIORITY)
   - Require PR review
   - Require CI checks to pass
   - Restrict force pushes

2. **Secrets rotation policy** (HIGH PRIORITY)
   - Rotate FTP credentials quarterly
   - Rotate SECRET_KEY if possible
   - Document process

3. **Monitoring & Alerts**
   - Monitor cPanel for failed deployments
   - Monitor app crashes/errors
   - Alert on failed authentication attempts

4. **WAF / DDoS Protection** (MEDIUM)
   - Consider Cloudflare Free tier
   - Or AWS Shield for DDoS
   - Protects against common attacks

## Deployment Checklist

Before any production push:
- [ ] All tests passing
- [ ] Security scan complete
- [ ] No secrets in code
- [ ] CHANGELOG updated
- [ ] Backup created
- [ ] Rollback plan documented
- [ ] Team notified of deployment window
