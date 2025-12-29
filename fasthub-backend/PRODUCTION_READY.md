# Production-Ready Features

This document describes the production-ready features implemented in the AutoFlow backend.

---

## 🚀 Overview

Five critical features have been implemented to make the backend production-ready:

1. **Rate Limiting** - Protects against abuse and DDoS attacks
2. **Monitoring** - Error tracking with Sentry + health checks
3. **Subscription Checks** - Revenue protection with automatic validation
4. **Token Blacklist** - Secure logout and token revocation
5. **API Documentation** - Comprehensive Swagger/ReDoc documentation

---

## 1. ⚡ Rate Limiting

### What It Does

Protects API endpoints from abuse by limiting the number of requests per time window.

### Implementation

- **Library:** `slowapi` (FastAPI-compatible rate limiting)
- **Storage:** Redis (production) or in-memory (development)
- **Strategy:** Fixed-window rate limiting
- **Headers:** Automatic rate limit headers in responses

### Rate Limits

| Endpoint Type | Limit | Description |
|--------------|-------|-------------|
| Auth Login | 5/minute | Prevents brute force attacks |
| Auth Register | 3/hour | Prevents spam registrations |
| Password Reset | 3/hour | Prevents email flooding |
| Magic Link | 5/hour | Prevents abuse of passwordless login |
| API Token Create | 10/hour | Limits token generation |
| Protected Read | 200/minute | Normal authenticated requests |
| Protected Write | 60/minute | Write operations |
| Admin | 100/minute | Admin operations |
| Webhooks | 1000/hour | External webhooks (Stripe, etc.) |

### Configuration

```python
# app/core/rate_limit.py
from app.core.rate_limit import RateLimits, limiter

# Apply to endpoint
@router.post("/login")
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(request: Request, ...):
    ...
```

### Environment Variables

```bash
# Redis URL for distributed rate limiting
REDIS_URL=redis://localhost:6379/0

# For in-memory (development only)
REDIS_URL=memory://
```

### Response Headers

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1640000000
```

### Error Response

```json
{
  "detail": "Rate limit exceeded: 5 per 1 minute"
}
```

---

## 2. 🔍 Monitoring

### What It Does

Tracks errors, performance, and system health for production debugging and alerting.

### Implementation

- **Error Tracking:** Sentry SDK with FastAPI integration
- **Health Checks:** `/api/v1/health` and `/api/v1/ready` endpoints
- **Metrics:** Basic metrics endpoint at `/api/v1/metrics`

### Sentry Integration

**Features:**
- Automatic error capture
- Performance monitoring (10% sample rate)
- Request context (URL, method, user)
- Sensitive data filtering (Authorization, Cookie, tokens)
- SQLAlchemy query tracking
- Logging integration (ERROR level)

**Configuration:**

```bash
# .env
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
```

**Manual Error Capture:**

```python
from app.core.monitoring import capture_exception, capture_message, set_user_context

# Capture exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e, context={"user_id": user.id})

# Capture message
capture_message("Important event occurred", level="warning")

# Set user context
set_user_context(user_id=str(user.id), email=user.email)
```

### Health Check Endpoints

#### `/api/v1/health` - Basic Health Check

**Purpose:** Quick liveness check (no dependencies)

**Response:**
```json
{
  "status": "healthy",
  "service": "AutoFlow",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Use Case:** Kubernetes liveness probe

#### `/api/v1/ready` - Readiness Check

**Purpose:** Full readiness check (checks dependencies)

**Checks:**
- Database connection (PostgreSQL/MySQL)
- Redis connection (if configured)

**Response (healthy):**
```json
{
  "status": "ready",
  "service": "AutoFlow",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00",
  "checks": {
    "database": {
      "status": "healthy",
      "type": "postgresql"
    },
    "redis": {
      "status": "healthy"
    }
  }
}
```

**Response (unhealthy):**
```json
{
  "status": "not_ready",
  "checks": {
    "database": {
      "status": "unhealthy",
      "error": "Connection refused"
    }
  }
}
```

**Use Case:** Kubernetes readiness probe

#### `/api/v1/metrics` - Basic Metrics

**Purpose:** Simple metrics for monitoring

**Response:**
```json
{
  "service": "AutoFlow",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Use Case:** Basic monitoring dashboard

### Kubernetes Configuration

```yaml
# deployment.yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## 3. 💰 Subscription Status Checks

### What It Does

Automatically validates user subscription status and blocks access to protected endpoints if subscription is invalid or expired.

### Implementation

- **Middleware:** Global subscription check for all authenticated requests
- **Dependency:** Per-endpoint subscription requirement
- **Endpoint:** `/api/v1/subscription/status` for checking status

### Subscription Statuses

| Status | Access | Description |
|--------|--------|-------------|
| `active` | ✅ Full | Subscription is active and paid |
| `trialing` | ✅ Full | User is in trial period |
| `past_due` | ⚠️ Grace Period | Payment failed, 7-day grace period |
| `canceled` | ❌ Blocked | Subscription canceled |
| `incomplete` | ❌ Blocked | Setup incomplete |
| `unpaid` | ❌ Blocked | Payment required |

### Grace Period

**Past Due Subscriptions:**
- **Grace Period:** 7 days after payment failure
- **Access:** Full access during grace period
- **Warning:** Logged to Sentry for monitoring
- **Action:** User receives email to update payment method

### Exempt Endpoints

The following endpoints do NOT require subscription check:

- `/api/v1/auth/*` - Authentication endpoints
- `/api/v1/health` - Health checks
- `/api/v1/ready` - Readiness checks
- `/api/v1/metrics` - Metrics
- `/api/v1/subscriptions/*` - Subscription management
- `/docs`, `/redoc` - API documentation

### Global Middleware

**Automatic Check:**
- Runs on every authenticated request
- Extracts user from JWT token
- Validates subscription status
- Returns 402 Payment Required if invalid

**Configuration:**
```python
# app/main.py
@app.middleware("http")
async def check_subscription_middleware(request: Request, call_next):
    # Automatic subscription check
    ...
```

### Per-Endpoint Dependency

**Explicit Requirement:**
```python
from app.core.dependencies import require_subscription

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(require_subscription)
):
    # Only accessible with valid subscription
    ...
```

### Status Check Endpoint

**GET `/api/v1/subscription/status`**

**Purpose:** Check current user's subscription status

**Response (active):**
```json
{
  "has_subscription": true,
  "is_valid": true,
  "status": "active",
  "plan": "pro",
  "current_period_start": "2024-01-01T00:00:00",
  "current_period_end": "2024-02-01T00:00:00",
  "trial_end": null,
  "expires_at": "2024-02-01T00:00:00",
  "stripe_subscription_id": "sub_123",
  "message": "Your subscription is active",
  "action": null
}
```

**Response (past_due):**
```json
{
  "has_subscription": true,
  "is_valid": true,
  "status": "past_due",
  "plan": "pro",
  "expires_at": "2024-01-08T00:00:00",
  "message": "Payment is overdue but you're still within the grace period",
  "action": "update_payment"
}
```

**Response (no subscription):**
```json
{
  "has_subscription": false,
  "status": "no_subscription",
  "message": "No subscription found",
  "action": "subscribe",
  "subscription_url": "/api/v1/subscriptions"
}
```

### Error Responses

**402 Payment Required:**
```json
{
  "detail": {
    "message": "No active subscription found",
    "action": "subscribe",
    "subscription_url": "/api/v1/subscriptions"
  }
}
```

**Actions:**
- `subscribe` - Create new subscription
- `update_payment` - Update payment method
- `resubscribe` - Reactivate canceled subscription
- `complete_setup` - Complete incomplete setup
- `contact_support` - Contact support for help

### Frontend Integration

**Check Subscription Status:**
```typescript
// Check subscription before accessing protected features
const response = await fetch('/api/v1/subscription/status', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const status = await response.json();

if (!status.is_valid) {
  // Show upgrade modal
  showUpgradeModal(status.action, status.message);
}
```

**Handle 402 Errors:**
```typescript
// Catch 402 errors globally
fetch('/api/v1/protected', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(response => {
  if (response.status === 402) {
    return response.json().then(error => {
      // Show subscription required modal
      showSubscriptionModal(error.detail);
    });
  }
  return response.json();
});
```

---

## 🔧 Configuration Summary

### Required Environment Variables

```bash
# Sentry (monitoring)
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Redis (rate limiting)
REDIS_URL=redis://localhost:6379/0

# Database (both PostgreSQL and MySQL supported)
DATABASE_URL=postgresql://user:pass@host:5432/db
# OR
DATABASE_URL=mysql://user:pass@host:3306/db
```

### Optional Environment Variables

```bash
# Rate limiting (defaults)
RATE_LIMIT_ENABLED=true

# Monitoring (defaults)
SENTRY_ENABLED=true

# Subscription checks (defaults)
SUBSCRIPTION_CHECK_ENABLED=true
SUBSCRIPTION_GRACE_PERIOD_DAYS=7
```

---

## 📊 Monitoring Dashboard

### Key Metrics to Track

1. **Rate Limiting:**
   - Rate limit hits per endpoint
   - Blocked requests per hour
   - Top blocked IPs

2. **Errors (Sentry):**
   - Error rate per endpoint
   - Error types distribution
   - User-impacting errors

3. **Health:**
   - Health check success rate
   - Database connection latency
   - Redis connection latency

4. **Subscriptions:**
   - Active subscriptions count
   - Past due subscriptions count
   - Subscription churn rate
   - Grace period expirations

### Alerting Rules

**Critical Alerts:**
- Health check failures > 3 in 5 minutes
- Database connection failures
- Error rate > 5% for 5 minutes
- Subscription check failures > 10%

**Warning Alerts:**
- Rate limit hits > 1000/hour
- Past due subscriptions > 10
- Grace period expirations > 5/day

---

## ✅ Production Checklist

Before deploying to production:

### Rate Limiting
- [ ] Redis configured and accessible
- [ ] Rate limits tested for each endpoint
- [ ] Rate limit monitoring dashboard setup
- [ ] Alert on excessive rate limit hits

### Monitoring
- [ ] Sentry DSN configured
- [ ] Sentry environment set to "production"
- [ ] Health checks tested
- [ ] Kubernetes probes configured
- [ ] Alert on health check failures
- [ ] Alert on error rate spikes

### Subscription Checks
- [ ] Subscription statuses tested
- [ ] Grace period logic verified
- [ ] Exempt endpoints documented
- [ ] Frontend handles 402 errors
- [ ] Alert on subscription check failures
- [ ] Monitor grace period expirations

### General
- [ ] All environment variables set
- [ ] Database migrations applied
- [ ] SSL/TLS enabled
- [ ] CORS configured correctly
- [ ] Security headers enabled
- [ ] Logging configured
- [ ] Backup strategy in place

---

## 🚀 Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/autoflow
      - REDIS_URL=redis://redis:6379/0
      - SENTRY_DSN=${SENTRY_DSN}
      - SENTRY_ENVIRONMENT=production
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=autoflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autoflow-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autoflow-backend
  template:
    metadata:
      labels:
        app: autoflow-backend
    spec:
      containers:
      - name: autoflow-backend
        image: autoflow/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: autoflow-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        - name: SENTRY_DSN
          valueFrom:
            secretKeyRef:
              name: autoflow-secrets
              key: sentry-dsn
        - name: SENTRY_ENVIRONMENT
          value: "production"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 📝 Additional Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [slowapi Documentation](https://slowapi.readthedocs.io/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Stripe Subscription Webhooks](https://stripe.com/docs/billing/subscriptions/webhooks)

---

## 4. 🎫 Token Blacklist

### What It Does

Provides server-side token invalidation for secure logout and token revocation using Redis.

### Implementation

- **Storage:** Redis with automatic TTL
- **Strategy:** Fail-open (if Redis unavailable, tokens are accepted)
- **Endpoints:** Logout + admin token management

### Features

**User Features:**
- Logout invalidates current token
- Token cannot be reused after logout

**Admin Features:**
- Manual token revocation
- Blacklist statistics
- Clear blacklist (testing)

### Configuration

```bash
# .env
REDIS_URL=redis://localhost:6379/0
```

### API Endpoints

**POST `/api/v1/auth/logout`** - Logout and blacklist token

**GET `/api/v1/admin/tokens/blacklist/stats`** - Get blacklist stats (admin)

**POST `/api/v1/admin/tokens/revoke-token`** - Manually revoke token (admin)

**POST `/api/v1/admin/tokens/blacklist/clear`** - Clear blacklist (admin)

### How It Works

1. User logs out
2. Extract token from Authorization header
3. Decode JWT to get expiration time
4. Add to Redis: `blacklist:{token}` with TTL
5. On next request, check Redis before validating JWT
6. If blacklisted, return 401 "Token has been revoked"

### Security

**Fail-Open Design:**
- If Redis unavailable, tokens are accepted (availability over security)
- Mitigation: Monitor Redis health, use replication

**Automatic Cleanup:**
- Tokens automatically removed when they expire (TTL)
- Prevents memory bloat

**Full Documentation:** See `TOKEN_BLACKLIST.md`

---

## 5. 📚 API Documentation

### What It Does

Provides comprehensive API documentation using Swagger UI and ReDoc.

### Implementation

- **Swagger UI:** Interactive API explorer at `/api/v1/docs`
- **ReDoc:** Alternative documentation at `/api/v1/redoc`
- **OpenAPI Schema:** Machine-readable spec at `/api/v1/openapi.json`

### Features

**Swagger UI:**
- Interactive API testing
- Try endpoints directly in browser
- Authentication support
- Request/response examples

**ReDoc:**
- Clean, readable documentation
- Search functionality
- Code samples in multiple languages
- Responsive design

### Configuration

Documentation is always enabled (production and development).

```python
# app/main.py
app = FastAPI(
    title="AutoFlow",
    version="1.0.0",
    description="Universal SaaS Boilerplate",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)
```

### Access

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### Authentication in Docs

1. Get access token from `/api/v1/auth/login`
2. Click "Authorize" button in Swagger UI
3. Enter: `Bearer <your_token>`
4. Click "Authorize"
5. All requests will include the token

---

## 🐛 Troubleshooting

### Rate Limiting Not Working

**Problem:** Requests not being rate limited

**Solutions:**
1. Check Redis connection: `redis-cli ping`
2. Verify REDIS_URL in environment
3. Check rate limiter initialization in `main.py`
4. Verify `@limiter.limit()` decorator on endpoints

### Sentry Not Capturing Errors

**Problem:** Errors not appearing in Sentry

**Solutions:**
1. Verify SENTRY_DSN is correct
2. Check SENTRY_ENVIRONMENT matches
3. Test with manual capture: `capture_exception(Exception("test"))`
4. Check Sentry project settings

### Subscription Checks Blocking Valid Users

**Problem:** Users with valid subscriptions getting 402 errors

**Solutions:**
1. Check subscription status in database
2. Verify grace period logic
3. Check exempt paths configuration
4. Review subscription middleware logs
5. Test with `/api/v1/subscription/status` endpoint

### Health Checks Failing

**Problem:** `/ready` endpoint returning 503

**Solutions:**
1. Check database connection
2. Verify Redis connection (if configured)
3. Check database credentials
4. Review health check logs
5. Test database query: `SELECT 1`

---

**Last Updated:** 2024-01-01
**Version:** 1.0.0
