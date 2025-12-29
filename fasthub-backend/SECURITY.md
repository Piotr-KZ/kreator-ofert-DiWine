# Security Guide

## Overview

This boilerplate implements security best practices following OWASP Top 10 and industry standards.

---

## Implemented Security Features

### 1. Authentication & Authorization ✅

**JWT Tokens:**
- Access tokens (30 min expiry)
- Refresh tokens (7 days expiry)
- Secure token generation (HS256)
- Token validation on every request

**Password Security:**
- bcrypt hashing (cost factor 12)
- Minimum 8 characters
- Password reset with time-limited tokens
- Password change requires current password

**Multi-factor Authentication:**
- Magic links (passwordless login)
- Email verification
- API tokens for programmatic access

**Role-Based Access Control (RBAC):**
- Admin, User, Viewer roles
- Protected endpoints with `@require_admin`
- Organization-level isolation

---

### 2. Input Validation ✅

**Pydantic Schemas:**
- All inputs validated with Pydantic models
- Type checking
- Email validation
- String length limits
- Pattern matching (regex)

**SQL Injection Protection:**
- SQLAlchemy ORM (parameterized queries)
- No raw SQL queries
- Input sanitization

**XSS Protection:**
- Content-Type validation
- HTML escaping in responses
- X-XSS-Protection header

---

### 3. Rate Limiting ✅

**Application Level (slowapi):**
```python
# Global rate limit
@limiter.limit("10/minute")

# Auth endpoints (stricter)
@limiter.limit("5/minute")
```

**Nginx Level:**
```nginx
# API endpoints: 10 req/s
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Auth endpoints: 5 req/min
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;
```

---

### 4. Security Headers ✅

All responses include:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Content-Security-Policy: default-src 'self'
```

---

### 5. CORS Configuration ✅

**Development:**
```python
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

**Production:**
```python
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
allow_credentials=True
max_age=600
```

---

### 6. HTTPS/TLS ✅

**Nginx SSL Configuration:**
- TLS 1.2 and 1.3 only
- Strong cipher suites
- HSTS enabled
- HTTP → HTTPS redirect

**Certificate Management:**
```bash
# Let's Encrypt (recommended)
certbot certonly --standalone -d yourdomain.com

# Or self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem
```

---

### 7. Database Security ✅

**Connection Security:**
- SSL/TLS connections
- Encrypted credentials
- Connection pooling
- Prepared statements (SQLAlchemy)

**Multi-tenancy Isolation:**
- Organization-level data separation
- Row-level filtering
- Foreign key constraints

**Secrets Management:**
- Environment variables
- Never commit `.env` files
- Use secrets management service (AWS Secrets Manager, etc.)

---

### 8. Logging & Monitoring ✅

**Request Logging:**
- All requests logged with timestamp
- Response time tracking
- Error logging with stack traces

**Security Events:**
- Failed login attempts
- Invalid tokens
- Rate limit violations

**Log Format:**
```
INFO: POST /api/v1/auth/login - 200 - 0.123s
ERROR: Invalid token: user_id=123
WARNING: Rate limit exceeded: IP=1.2.3.4
```

---

## Security Checklist

### Before Production

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `DEBUG=false`
- [ ] Configure `ALLOWED_HOSTS` (remove `*`)
- [ ] Configure `BACKEND_CORS_ORIGINS` (specific domains)
- [ ] Enable HTTPS/TLS
- [ ] Set up SSL certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerting
- [ ] Review and restrict API documentation access
- [ ] Enable database backups
- [ ] Set up log aggregation
- [ ] Configure firewall rules
- [ ] Review environment variables
- [ ] Scan for vulnerabilities (`docker scan`)
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure DDoS protection

---

## Environment Variables Security

### Required (Production)

```env
# Strong random key (generate with: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-64-characters-minimum

# Database (use managed service with SSL)
DATABASE_URL=mysql+aiomysql://user:password@host:3306/db?ssl=true

# CORS (specific domains only)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Allowed hosts (specific domains only)
ALLOWED_HOSTS=yourdomain.com,app.yourdomain.com

# Disable debug mode
DEBUG=false
```

### Optional (Services)

```env
# Stripe (use live keys)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# SendGrid
SENDGRID_API_KEY=SG.xxx

# Redis (with password)
REDIS_URL=redis://:password@host:6379/0
```

---

## Common Vulnerabilities & Mitigations

### 1. SQL Injection ✅
**Mitigation:** SQLAlchemy ORM, parameterized queries

### 2. XSS (Cross-Site Scripting) ✅
**Mitigation:** Input validation, output encoding, CSP headers

### 3. CSRF (Cross-Site Request Forgery) ✅
**Mitigation:** JWT tokens (stateless), SameSite cookies

### 4. Authentication Bypass ✅
**Mitigation:** JWT validation, password hashing, rate limiting

### 5. Sensitive Data Exposure ✅
**Mitigation:** HTTPS, encrypted database, secure headers

### 6. Broken Access Control ✅
**Mitigation:** RBAC, organization isolation, dependency injection

### 7. Security Misconfiguration ✅
**Mitigation:** Secure defaults, environment-based config

### 8. Insecure Deserialization ✅
**Mitigation:** Pydantic validation, type checking

### 9. Using Components with Known Vulnerabilities ✅
**Mitigation:** Regular updates, dependency scanning

### 10. Insufficient Logging & Monitoring ✅
**Mitigation:** Request logging, error tracking, security events

---

## Incident Response

### If Security Breach Detected:

1. **Immediate Actions:**
   - Rotate all secrets (SECRET_KEY, database passwords, API keys)
   - Revoke all active tokens
   - Block suspicious IPs
   - Take affected services offline if necessary

2. **Investigation:**
   - Review logs for attack vectors
   - Identify compromised data
   - Determine scope of breach

3. **Remediation:**
   - Patch vulnerabilities
   - Notify affected users
   - Update security measures
   - Document incident

4. **Prevention:**
   - Implement additional monitoring
   - Update security policies
   - Conduct security audit
   - Train team on security best practices

---

## Security Testing

### Automated Scanning

```bash
# Dependency vulnerabilities
pip install safety
safety check

# Docker image scanning
docker scan autoflow-api

# OWASP ZAP (API security testing)
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000
```

### Manual Testing

- [ ] Test authentication bypass
- [ ] Test authorization bypass
- [ ] Test SQL injection
- [ ] Test XSS
- [ ] Test CSRF
- [ ] Test rate limiting
- [ ] Test session management
- [ ] Test password reset flow
- [ ] Test API token security

---

## Security Updates

**Regular Maintenance:**
- Update dependencies monthly
- Review security advisories
- Scan for vulnerabilities
- Rotate secrets quarterly
- Review access logs weekly
- Update SSL certificates before expiry

**Stay Informed:**
- Subscribe to security mailing lists
- Follow OWASP updates
- Monitor CVE databases
- Review FastAPI security advisories

---

## Contact

For security issues, please email: security@yourdomain.com

**Do not** open public GitHub issues for security vulnerabilities.

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
