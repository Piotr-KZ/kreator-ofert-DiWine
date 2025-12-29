# Complete Implementation Plan - FastAPI Boilerplate

## 🎯 GOAL
Create a **complete FastAPI boilerplate** with **100% feature parity** with Firebase boilerplate, following **ALL** Claude's recommendations.

---

## 📊 CURRENT STATUS

### ✅ COMPLETED (40%)
1. **Foundation** - DDD architecture, project structure
2. **Database** - MySQL/TiDB, SQLAlchemy, Alembic migrations
3. **Auth Module** - JWT, registration, login, password reset, email verification
4. **Users Module** - CRUD, role management, organization membership
5. **Organizations Module** - CRUD, ownership, team management
6. **Subscriptions Module (85%)** - Stripe integration, webhooks (partial)

### 🔄 IN PROGRESS (15%)
7. **Subscriptions** - Missing 3 use cases (failed payment, subscription cycle, check invoice)

### ⏳ TODO (45%)
8. **Invoices Module** - PDF generation, Fakturownia integration
9. **Admin Module** - Broadcast messaging, admin dashboard
10. **API Tokens** - Create, delete, manage API tokens
11. **Magic Links** - Passwordless login
12. **Email Service** - SendGrid integration
13. **Celery** - Async tasks, scheduled jobs
14. **Testing** - pytest, fixtures, mocks
15. **Docker** - Dockerfile, docker-compose
16. **Security** - CORS, rate limiting, input validation
17. **Performance** - Database indexes, caching, optimization
18. **Migration Script** - Firebase → PostgreSQL data migration

---

## 🚀 IMPLEMENTATION ROADMAP

### PHASE 1: Complete Core Features (3 hours)

#### 1.1 Finish Subscriptions Module (30 min)
**Firebase use cases:**
- [ ] `HandleFailedPaymentUseCase` - Handle failed Stripe payments
- [ ] `HandleSubscriptionCycleUseCase` - Handle successful payments
- [ ] `CheckSubscriptionInvoiceUseCase` - Check subscription invoice status

**Implementation:**
```python
# app/services/subscription_service.py
async def handle_failed_payment(stripe_invoice)
async def handle_subscription_cycle(stripe_invoice)
async def check_subscription_invoice(organization_id)
```

#### 1.2 Invoices Module (1 hour)
**Firebase use case:**
- [ ] `IssueInvoiceToNewPaymentUseCase` - Generate invoice for payment

**Features:**
- [ ] Invoice model (already exists)
- [ ] Invoice service
- [ ] PDF generation (ReportLab or WeasyPrint)
- [ ] Fakturownia integration (optional)
- [ ] Invoice endpoints (list, get, download PDF)

**Implementation:**
```python
# app/services/invoice_service.py
class InvoiceService:
    async def create_invoice(payment_data)
    async def generate_pdf(invoice_id)
    async def send_invoice_email(invoice_id)
    async def sync_with_fakturownia(invoice_id)  # Optional
```

#### 1.3 Admin Module (30 min)
**Firebase use case:**
- [ ] `BroadcastMessageUseCase` - Send message to all users

**Features:**
- [ ] Admin service
- [ ] Broadcast messaging (email/in-app notifications)
- [ ] Admin endpoints (admin-only routes)

**Implementation:**
```python
# app/services/admin_service.py
class AdminService:
    async def broadcast_message(title, content, recipients)
    async def get_system_stats()
```

#### 1.4 API Tokens (30 min)
**Firebase use cases:**
- [ ] `CreateApiTokenUseCase` - Create API token for user
- [ ] `DeleteApiTokenUseCase` - Delete API token

**Features:**
- [ ] API token model
- [ ] Token generation (secure random)
- [ ] Token authentication (dependency)
- [ ] Token endpoints (create, list, delete)

**Implementation:**
```python
# app/models/api_token.py
class APIToken(BaseModel):
    user_id, token_hash, name, expires_at
    
# app/core/dependencies.py
async def get_current_user_from_api_token(token: str)
```

#### 1.5 Magic Links (30 min)
**Firebase use case:**
- [ ] `SendLinkToLoginUseCase` - Send passwordless login link

**Features:**
- [ ] Magic link token generation
- [ ] Magic link email sending
- [ ] Magic link verification endpoint

**Implementation:**
```python
# app/services/auth_service.py
async def send_magic_link(email)
async def verify_magic_link(token)
```

---

### PHASE 2: Infrastructure & Quality (2 hours)

#### 2.1 Email Service (30 min)
**Claude Section 4 requirements:**
- [ ] SendGrid integration
- [ ] Email templates (Jinja2)
- [ ] Send verification emails
- [ ] Send password reset emails
- [ ] Send magic link emails
- [ ] Send invoice emails

**Implementation:**
```python
# app/services/email_service.py
class EmailService:
    async def send_verification_email(user, token)
    async def send_password_reset_email(user, token)
    async def send_magic_link_email(user, token)
    async def send_invoice_email(user, invoice)
```

#### 2.2 Celery (30 min)
**Claude Section 5 requirements:**
- [ ] Celery setup (Redis broker)
- [ ] Task definitions
- [ ] Email tasks (async)
- [ ] Invoice generation tasks
- [ ] Scheduled tasks (beat)

**Implementation:**
```python
# app/celery_app.py
from celery import Celery

celery = Celery('autoflow', broker='redis://localhost:6379/0')

@celery.task
def send_email_task(to, subject, body)

@celery.task
def generate_invoice_pdf_task(invoice_id)
```

#### 2.3 Testing (1 hour)
**Claude Section 7 requirements:**
- [ ] pytest setup
- [ ] Test fixtures (database, users)
- [ ] Auth tests (registration, login, JWT)
- [ ] User tests (CRUD)
- [ ] Subscription tests (Stripe mocks)
- [ ] Integration tests
- [ ] Coverage >80%

**Implementation:**
```python
# tests/conftest.py
@pytest.fixture
async def test_db()

@pytest.fixture
async def test_user()

# tests/test_auth.py
async def test_register()
async def test_login()
async def test_jwt_token()
```

---

### PHASE 3: Production Ready (1.5 hours)

#### 3.1 Docker (30 min)
**Claude Section 8 requirements:**
- [ ] Dockerfile (multi-stage build)
- [ ] docker-compose.yml (app + postgres + redis)
- [ ] .dockerignore
- [ ] Health checks
- [ ] Environment variables

**Implementation:**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.2 Security (30 min)
**Claude Section 9 (OWASP) requirements:**
- [ ] CORS configuration
- [ ] Rate limiting (slowapi)
- [ ] Input validation (Pydantic)
- [ ] SQL injection prevention (SQLAlchemy)
- [ ] XSS prevention (escape HTML)
- [ ] Security headers (helmet)
- [ ] Password strength validation

**Implementation:**
```python
# app/core/security.py
def validate_password_strength(password)
def sanitize_html(text)

# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
)
```

#### 3.3 Performance (30 min)
**Claude Section 9 requirements:**
- [ ] Database indexes (all foreign keys)
- [ ] Query optimization (select_related, joinedload)
- [ ] Redis caching (user sessions, frequently accessed data)
- [ ] Connection pooling (SQLAlchemy)
- [ ] Monitoring (logging, metrics)

**Implementation:**
```sql
-- Add indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org_id ON users(organization_id);
CREATE INDEX idx_subscriptions_org_id ON subscriptions(organization_id);
```

```python
# app/core/cache.py
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

async def get_cached_user(user_id):
    cached = cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    # Fetch from DB and cache
```

---

### PHASE 4: Optional Integrations (2 hours)

#### 4.1 Outlook IMAP (1 hour)
**Claude Section 4 requirements:**
- [ ] IMAP connection
- [ ] Email fetching
- [ ] Email parsing
- [ ] Attachment handling

#### 4.2 Fakturownia (30 min)
**Claude Section 4 requirements:**
- [ ] API integration
- [ ] Invoice creation
- [ ] Invoice syncing

#### 4.3 Google APIs (30 min)
**Claude Section 4 requirements:**
- [ ] OAuth2 flow
- [ ] Calendar integration
- [ ] Gmail integration

---

## 📋 DETAILED CHECKLIST

### Core Features (MUST HAVE)
- [x] Auth (JWT, registration, login)
- [x] Users (CRUD, roles)
- [x] Organizations (multi-tenancy)
- [ ] Subscriptions (complete all 10 use cases)
- [ ] Invoices (PDF generation)
- [ ] Admin (broadcast messaging)
- [ ] API Tokens
- [ ] Magic Links

### Infrastructure (MUST HAVE)
- [ ] Email Service (SendGrid)
- [ ] Celery (async tasks)
- [ ] Testing (pytest, >80% coverage)
- [ ] Docker (containerization)
- [ ] Security (CORS, rate limiting)
- [ ] Performance (indexes, caching)

### Optional (NICE TO HAVE)
- [ ] Outlook IMAP
- [ ] Fakturownia
- [ ] Google APIs
- [ ] Migration Script (Firebase → PostgreSQL)

---

## ⏱️ TIME ESTIMATE

**MUST HAVE (Core + Infrastructure):** ~6.5 hours
- Phase 1 (Core Features): 3 hours
- Phase 2 (Infrastructure): 2 hours
- Phase 3 (Production): 1.5 hours

**NICE TO HAVE (Optional):** ~2 hours
- Phase 4 (Integrations): 2 hours

**TOTAL:** ~8.5 hours for complete boilerplate

---

## 🎯 NEXT STEPS (Priority Order)

1. **Finish Subscriptions** (30 min) - 3 missing use cases
2. **Invoices Module** (1 hour) - PDF generation
3. **Admin Module** (30 min) - Broadcast messaging
4. **API Tokens** (30 min) - Token management
5. **Magic Links** (30 min) - Passwordless login
6. **Email Service** (30 min) - SendGrid
7. **Testing** (1 hour) - pytest
8. **Docker** (30 min) - Containerization
9. **Security** (30 min) - CORS, rate limiting
10. **Performance** (30 min) - Indexes, caching

**Start with:** Step 1 (Finish Subscriptions) - 30 minutes
