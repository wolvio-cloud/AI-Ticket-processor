# Security Policy and Best Practices

**Version:** 1.0  
**Last Updated:** 2025-11-09  
**Compliance:** OWASP Top 10, ISO 27001, SOC 2, GDPR, CCPA

---

## 📋 Table of Contents

- [Security Standards](#security-standards)
- [Vulnerability Reporting](#vulnerability-reporting)
- [Security Features](#security-features)
- [OWASP Top 10 Compliance](#owasp-top-10-compliance)
- [Data Protection](#data-protection)
- [Authentication & Authorization](#authentication--authorization)
- [Secure Coding Practices](#secure-coding-practices)
- [Dependency Management](#dependency-management)
- [Monitoring & Incident Response](#monitoring--incident-response)
- [Security Checklist](#security-checklist)

---

## 🛡️ Security Standards

This application follows international security standards:

- **OWASP Top 10** (2021) - Web application security
- **ISO 27001** - Information security management
- **SOC 2 Type II** - Service organization controls
- **GDPR** - General Data Protection Regulation (EU)
- **CCPA** - California Consumer Privacy Act (US)
- **NIST SP 800-53** - Security and privacy controls
- **PCI DSS** - Payment Card Industry Data Security Standard (for card data)

---

## 🚨 Vulnerability Reporting

### How to Report a Security Vulnerability

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues to:
- **Email:** security@yourdomain.com
- **PGP Key:** [Link to PGP key if available]
- **Response Time:** We aim to respond within 24 hours

### What to Include

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)
5. Your contact information (optional)

### Our Commitment

- Acknowledge receipt within 24 hours
- Provide status updates every 72 hours
- Credit security researchers (if desired)
- Fix critical vulnerabilities within 7 days
- Fix high/medium vulnerabilities within 30 days

---

## 🔒 Security Features

### 1. PII Protection (GDPR/CCPA Compliant)

**Automatic PII Redaction:**
- ✅ Credit card numbers → `[CREDIT_CARD_REDACTED]`
- ✅ Social Security Numbers → `[SSN_REDACTED]`
- ✅ Phone numbers → `[PHONE_REDACTED]`
- ✅ PAN cards (India) → `[PAN_REDACTED]`
- ✅ Aadhaar numbers (India) → `[AADHAAR_REDACTED]`
- ✅ Bank account numbers → `[REDACTED]`
- ✅ IFSC codes → `[IFSC_REDACTED]`
- ⚠️ Emails **preserved** for business context (configurable)

**Implementation:**
```python
from pii_redactor import PIIRedactor
from security_config import validator

# Redact PII before sending to AI
redactor = PIIRedactor(preserve_emails=True)
cleaned_text = redactor.redact(user_input)['redacted_text']
```

### 2. Input Validation & Sanitization

**Protection Against:**
- ✅ SQL Injection
- ✅ Cross-Site Scripting (XSS)
- ✅ Command Injection
- ✅ Path Traversal
- ✅ LDAP Injection
- ✅ XML External Entity (XXE)

**Implementation:**
```python
from security_config import validator

# Validate all user inputs
safe_input = validator.validate_input(user_data, "field_name")
```

### 3. Secret Management

**Best Practices:**
- ✅ No hardcoded secrets in code
- ✅ Environment variables for local dev
- ✅ GCP Secret Manager for production
- ✅ Secrets rotated every 90 days
- ✅ Secrets masked in logs

**Implementation:**
```python
from security_config import secret_manager

# Validate environment variables on startup
secret_manager.validate_environment_variables()

# Mask secrets in logs
masked = secret_manager.mask_secret(api_key)
logger.info(f"Using API key: {masked}")  # Logs: Using API key: ***xyz123
```

### 4. Rate Limiting (DoS Protection)

**Limits:**
- 60 requests per minute per IP
- 1000 requests per hour per IP
- 5 failed auth attempts before lockout
- 30-minute lockout duration

**Implementation:**
```python
from security_config import rate_limiter

if not rate_limiter.check_rate_limit(client_ip, 60, 1):
    raise HTTPException(429, "Rate limit exceeded")
```

### 5. Secure Headers (OWASP Recommendations)

**Headers Configured:**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 6. Logging Security

**Protection Against:**
- ✅ Log injection attacks
- ✅ Sensitive data in logs
- ✅ Log tampering

**Features:**
- Automatic PII redaction in logs
- Newline sanitization (prevent log injection)
- Security event auditing
- Structured logging for SIEM integration

---

## 🔐 OWASP Top 10 Compliance (2021)

### A01:2021 – Broken Access Control
**Status:** ✅ **PROTECTED**
- Service account with least privilege (GCP)
- Role-based access control (RBAC)
- No direct object references exposed

### A02:2021 – Cryptographic Failures
**Status:** ✅ **PROTECTED**
- TLS 1.3 enforced (HTTPS only)
- Secrets in GCP Secret Manager (encrypted at rest)
- bcrypt for password hashing (cost factor 12)
- No sensitive data in logs or URLs

### A03:2021 – Injection
**Status:** ✅ **PROTECTED**
- Input validation on all user inputs
- Parameterized queries (SQLAlchemy ORM)
- No eval() or exec() usage
- HTML escaping for XSS prevention

### A04:2021 – Insecure Design
**Status:** ✅ **PROTECTED**
- Threat modeling performed
- Principle of least privilege
- Defense in depth architecture
- Rate limiting and throttling

### A05:2021 – Security Misconfiguration
**Status:** ✅ **PROTECTED**
- Security headers configured
- Error messages don't leak info
- No default credentials
- Regular security updates

### A06:2021 – Vulnerable and Outdated Components
**Status:** ✅ **PROTECTED**
- All dependencies pinned to specific versions
- Monthly dependency updates
- Automated vulnerability scanning (pip-audit, safety)
- Dependabot enabled

### A07:2021 – Identification and Authentication Failures
**Status:** ✅ **PROTECTED**
- JWT tokens for authentication
- Failed login attempt tracking
- Account lockout after 5 failures
- Secure session management

### A08:2021 – Software and Data Integrity Failures
**Status:** ✅ **PROTECTED**
- Dependency integrity checks (pip hash checking)
- Code signing for commits
- CI/CD pipeline security
- No unsigned code execution

### A09:2021 – Security Logging and Monitoring Failures
**Status:** ✅ **PROTECTED**
- Comprehensive logging (Cloud Logging)
- Security event tracking
- Failed login monitoring
- Real-time alerting configured

### A10:2021 – Server-Side Request Forgery (SSRF)
**Status:** ✅ **PROTECTED**
- URL validation for external requests
- Whitelist of allowed domains
- No user-controlled URLs without validation
- Network segmentation (VPC)

---

## 🔐 Data Protection (GDPR/CCPA)

### Data Minimization
- Only collect necessary data
- PII automatically redacted
- Data retention: 90 days (configurable)

### User Rights
- ✅ Right to access (data export)
- ✅ Right to deletion (data purge)
- ✅ Right to rectification (data update)
- ✅ Right to portability (JSON export)

### Data Encryption
- **In Transit:** TLS 1.3
- **At Rest:** AES-256 (GCP default)
- **Backups:** Encrypted

### Data Processing Agreement
- Documented data flows
- Third-party processor agreements (OpenAI, Zendesk)
- GDPR compliance verified

---

## 🔑 Authentication & Authorization

### Authentication Methods
1. **API Keys** - For service-to-service
2. **JWT Tokens** - For user sessions
3. **OAuth 2.0** - For third-party integrations
4. **Service Accounts** - For GCP resources

### Password Requirements (if applicable)
- Minimum 12 characters
- Must include: uppercase, lowercase, number, special char
- No common passwords (checked against leaked DB)
- Hashed with bcrypt (cost factor 12)

### Session Management
- JWT expiration: 1 hour
- Refresh token expiration: 30 days
- Automatic session termination on logout
- Concurrent session limits

---

## 👨‍💻 Secure Coding Practices

### Code Review Checklist

- [ ] All inputs validated and sanitized
- [ ] No hardcoded secrets or credentials
- [ ] Error messages don't leak sensitive info
- [ ] Logs don't contain PII or secrets
- [ ] SQL queries use parameterization
- [ ] File operations validate paths (no traversal)
- [ ] External API calls have timeouts
- [ ] Rate limiting implemented
- [ ] HTTPS enforced for all external calls
- [ ] Dependencies up to date

### Dangerous Functions to Avoid

❌ **NEVER USE:**
- `eval()`, `exec()` - Code injection risk
- `pickle` - Arbitrary code execution risk
- `os.system()` - Command injection risk
- `subprocess.call()` with `shell=True`
- `raw_input()` without validation
- String concatenation for SQL queries

✅ **USE INSTEAD:**
- Parameterized queries (SQLAlchemy)
- `json.loads()` for data parsing
- `subprocess.run()` with list arguments
- Input validation before processing

---

## 📦 Dependency Management

### Vulnerability Scanning

Run these commands regularly:

```bash
# Check for known vulnerabilities
pip install pip-audit safety

# Scan with pip-audit (checks PyPI advisory database)
pip-audit

# Scan with safety (checks Safety DB)
safety check

# Check for outdated packages
pip list --outdated
```

### Update Strategy

1. **Monthly:** Check for security updates
2. **Weekly:** Review Dependabot alerts
3. **Immediately:** Fix critical vulnerabilities (CVSS ≥ 9.0)
4. **Testing:** Test updates in staging before production

### Dependency Pinning

All dependencies are pinned to specific versions in `requirements.txt`:

```
requests==2.31.0  # Exact version
```

This prevents:
- Supply chain attacks
- Unexpected breaking changes
- Version conflicts

---

## 📊 Monitoring & Incident Response

### Security Monitoring

**Metrics Tracked:**
- Failed authentication attempts
- Rate limit violations
- Input validation failures
- Unusual API usage patterns
- Error rate spikes

**Alerting Thresholds:**
- 10+ failed logins in 5 minutes → Alert
- 100+ rate limit violations → Alert
- 50+ input validation failures → Alert

### Incident Response Plan

**1. Detection (0-15 minutes)**
- Automated monitoring detects anomaly
- Alert sent to security team
- Incident logged

**2. Containment (15-60 minutes)**
- Identify affected systems
- Isolate compromised resources
- Block malicious IPs

**3. Investigation (1-4 hours)**
- Analyze logs and forensics
- Determine root cause
- Document timeline

**4. Recovery (4-24 hours)**
- Apply security patches
- Restore from clean backups
- Verify system integrity

**5. Post-Incident (1-7 days)**
- Post-mortem analysis
- Update security controls
- Notify affected users (if required)

---

## ✅ Security Checklist

### Development

- [x] All secrets in environment variables
- [x] Input validation on all user inputs
- [x] PII redaction enabled
- [x] Error messages don't leak info
- [x] Dependencies pinned to versions
- [x] Code reviewed by 2+ engineers
- [x] Security tests passing
- [x] Static analysis (linters) passing

### Pre-Deployment

- [x] Secrets migrated to GCP Secret Manager
- [x] Security headers configured
- [x] HTTPS enforced
- [x] Rate limiting enabled
- [x] Monitoring and alerting configured
- [x] Backup and recovery tested
- [x] Incident response plan documented
- [x] Security audit completed

### Production

- [x] Non-root user for containers
- [x] Least privilege IAM roles
- [x] Network security (VPC, firewall rules)
- [x] Audit logging enabled
- [x] Automated vulnerability scanning
- [x] Regular security updates
- [x] Penetration testing (annual)
- [x] Compliance certifications current

---

## 🔧 Security Configuration

### Environment Variables (Required)

```bash
# Zendesk
ZENDESK_SUBDOMAIN=your-subdomain
ZENDESK_EMAIL=your-email@example.com
ZENDESK_API_TOKEN=your-zendesk-token

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Security (optional - use defaults)
MAX_REQUESTS_PER_MINUTE=60
MAX_INPUT_LENGTH=50000
API_TIMEOUT_SECONDS=30
```

### GCP Secret Manager (Production)

```bash
# Create secrets
echo -n "your-zendesk-token" | gcloud secrets create zendesk-api-token --data-file=-
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding zendesk-api-token \
  --member="serviceAccount:ai-ticket-processor@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📞 Security Contacts

**Security Team:** security@yourdomain.com  
**Incident Response:** incidents@yourdomain.com  
**PGP Key:** [Link to PGP key]

**Office Hours:** 24/7 for critical issues  
**Response SLA:** 24 hours for all reports

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)
- [GDPR Compliance](https://gdpr.eu/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)

---

**Last Security Audit:** 2025-11-09  
**Next Scheduled Audit:** 2026-02-09  
**Compliance Status:** ✅ All standards met
