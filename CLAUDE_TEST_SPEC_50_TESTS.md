# Test Specification for Claude - 50 Missing Tests

**Project:** FastHub Backend  
**Current Coverage:** 65% (144/194 tests)  
**Missing:** 50 tests for 100% coverage

---

## ⚠️ CRITICAL: Common Errors to AVOID

### 1. **VERIFY Model Fields Before Writing Tests**
```python
# ❌ WRONG - Assuming fields exist
from app.models.audit_log import AuditLog, AuditAction  # AuditAction doesn't exist!
log = AuditLog(
    action=AuditAction.USER_LOGIN,  # ❌ action is String, not Enum!
    organization_id=uuid4()  # ❌ organization_id field doesn't exist!
)

# ✅ CORRECT - Check actual model first
# Read app/models/audit_log.py to see actual fields:
# - action: String(100) - not enum!
# - No organization_id field!
log = AuditLog(
    action="user.login",  # ✅ String value
    user_id=uuid4()  # ✅ Field exists
)
```

### 2. **Check Import Paths - Use Actual Project Structure**
```python
# ❌ WRONG - Guessing paths
from app.repositories.user_repository import UserRepository  # doesn't exist!

# ✅ CORRECT - Verify with ls app/services/
from app.services.user_repository import UserRepository  # exists in services/
```

### 3. **Always Import pytest**
```python
# ❌ WRONG - Missing import
@pytest.mark.asyncio  # NameError: name 'pytest' is not defined
async def test_something():
    pass

# ✅ CORRECT
import pytest

@pytest.mark.asyncio
async def test_something():
    pass
```

### 4. **Check Existing Fixtures in conftest.py**
```python
# ❌ WRONG - Creating duplicate fixtures
@pytest.fixture
async def db_session():  # Already exists in conftest.py!
    pass

# ✅ CORRECT - Use existing fixtures
async def test_something(db_session):  # Use from conftest.py
    pass
```

### 5. **Verify Service/Repository Method Signatures**
```python
# ❌ WRONG - Assuming method exists
result = await invoice_service.calculate_total(invoice_id)  # method doesn't exist!

# ✅ CORRECT - Read app/services/invoice_service.py first
# Check what methods actually exist and their signatures
result = await invoice_service.get_invoice(invoice_id)  # actual method
```

### 6. **Use Correct Async/Sync Patterns**
```python
# ❌ WRONG - Mixing async/sync
def test_async_function():  # Missing async
    result = await some_async_function()  # SyntaxError!

# ✅ CORRECT
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
```

### 7. **Mock External Dependencies (Redis, SendGrid, Stripe)**
```python
# ❌ WRONG - Calling real external services in tests
async def test_send_email():
    result = await email_service.send_email(...)  # Calls real SendGrid!

# ✅ CORRECT - Mock external services
@pytest.fixture
def mock_sendgrid(monkeypatch):
    async def fake_send(*args, **kwargs):
        return {"status": "sent"}
    monkeypatch.setattr("app.services.email_service.sendgrid_client.send", fake_send)

async def test_send_email(mock_sendgrid):
    result = await email_service.send_email(...)  # Uses mock
```

### 8. **Check Schema Field Names Match Model**
```python
# ❌ WRONG - Schema field names don't match model
class InvoiceCreate(BaseModel):
    total_amount: Decimal  # Model has 'amount', not 'total_amount'!

# ✅ CORRECT - Read model first, match field names
class InvoiceCreate(BaseModel):
    amount: Decimal  # Matches model field name
```

---

## 📋 50 MISSING TESTS - DETAILED SPECIFICATION

### HIGH PRIORITY: Invoice & Billing (15 tests)

#### File: `tests/unit/test_invoice_service.py` (10 tests)

**BEFORE WRITING:** Read these files first:
- `app/services/invoice_service.py` - check all method signatures
- `app/models/invoice.py` - check all fields (id, user_id, organization_id, amount, status, etc.)
- `app/schemas/invoice.py` - check schema field names

**Tests to write:**

1. `test_create_invoice_success()`
   - Create invoice with valid data
   - Assert invoice.id, invoice.amount, invoice.status == "pending"
   - **Avoid:** Don't assume field names, read model first!

2. `test_create_invoice_invalid_amount()`
   - Try to create invoice with negative amount
   - Assert raises ValueError or ValidationError
   - **Avoid:** Check what exception invoice_service actually raises

3. `test_get_invoice_by_id()`
   - Create invoice, then get by ID
   - Assert returned invoice matches created
   - **Avoid:** Don't assume get_invoice() method exists, check service file

4. `test_get_invoice_not_found()`
   - Try to get non-existent invoice
   - Assert returns None or raises NotFoundError
   - **Avoid:** Check actual behavior in service

5. `test_list_user_invoices()`
   - Create 3 invoices for user
   - List invoices for that user
   - Assert returns 3 invoices
   - **Avoid:** Check if method is list_invoices() or get_user_invoices()

6. `test_update_invoice_status()`
   - Create invoice with status="pending"
   - Update to status="paid"
   - Assert invoice.status == "paid"
   - **Avoid:** Check if status field is enum or string

7. `test_delete_invoice()`
   - Create invoice, then delete
   - Assert get_invoice() returns None after deletion
   - **Avoid:** Check if delete is soft delete (is_deleted flag) or hard delete

8. `test_calculate_invoice_total()`
   - Create invoice with line items
   - Calculate total
   - Assert total matches sum of line items
   - **Avoid:** Check if invoice has line_items field or separate table

9. `test_invoice_belongs_to_user()`
   - Create invoice for user A
   - Try to access as user B
   - Assert raises PermissionError
   - **Avoid:** Check authorization logic in service

10. `test_invoice_date_range_filter()`
    - Create invoices with different dates
    - Filter by date range
    - Assert returns only invoices in range
    - **Avoid:** Check if method accepts date_from/date_to parameters

#### File: `tests/integration/test_invoices_api.py` (5 tests)

**BEFORE WRITING:** Read these files:
- `app/api/v1/endpoints/invoices.py` - check all routes and their HTTP methods
- Check if routes require authentication (use auth_headers fixture)

**Tests to write:**

1. `test_create_invoice_api()`
   - POST /api/v1/invoices/ with valid data
   - Assert status 201, response has invoice.id
   - **Avoid:** Check actual route path in invoices.py

2. `test_get_invoice_api()`
   - GET /api/v1/invoices/{invoice_id}
   - Assert status 200, response has invoice data
   - **Avoid:** Check if route requires auth (use auth_headers)

3. `test_list_invoices_api()`
   - GET /api/v1/invoices/
   - Assert status 200, response is list
   - **Avoid:** Check if response is list or {"invoices": [...], "total": N}

4. `test_update_invoice_api()`
   - PATCH /api/v1/invoices/{invoice_id}
   - Assert status 200, invoice updated
   - **Avoid:** Check if it's PATCH or PUT

5. `test_delete_invoice_api_forbidden()`
   - Try to delete invoice as non-owner
   - Assert status 403
   - **Avoid:** Check authorization logic in endpoint

---

### HIGH PRIORITY: Subscription & Billing (10 tests)

#### File: `tests/unit/test_subscription_service.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/services/subscription_service.py` (if exists, otherwise check where subscription logic is)
- `app/models/subscription.py` - check fields (plan, status, expires_at, etc.)
- `app/core/subscription_check.py` - check middleware logic

**Tests to write:**

1. `test_check_subscription_active()`
   - Create subscription with status="active", expires_at=future
   - Check if active
   - Assert returns True
   - **Avoid:** Check actual method name (is_active? check_active?)

2. `test_check_subscription_expired()`
   - Create subscription with expires_at=past
   - Check if active
   - Assert returns False
   - **Avoid:** Check if expired subscriptions have status="expired" or just past date

3. `test_subscription_upgrade()`
   - Create subscription with plan="basic"
   - Upgrade to plan="pro"
   - Assert subscription.plan == "pro"
   - **Avoid:** Check if plan is enum or string

4. `test_subscription_cancel()`
   - Create active subscription
   - Cancel subscription
   - Assert subscription.status == "cancelled"
   - **Avoid:** Check if cancel sets status or just expires_at

5. `test_subscription_renewal()`
   - Create subscription expiring soon
   - Renew subscription
   - Assert expires_at extended
   - **Avoid:** Check renewal logic (adds 30 days? 1 month?)

#### File: `tests/integration/test_subscription_api.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/api/v1/endpoints/subscription_status.py` - check routes

**Tests to write:**

1. `test_get_subscription_status_api()`
   - GET /api/v1/subscription/status
   - Assert status 200, returns subscription data
   - **Avoid:** Check actual route path

2. `test_upgrade_subscription_api()`
   - POST /api/v1/subscription/upgrade
   - Assert status 200, subscription upgraded
   - **Avoid:** Check if it's POST or PATCH

3. `test_cancel_subscription_api()`
   - POST /api/v1/subscription/cancel
   - Assert status 200, subscription cancelled
   - **Avoid:** Check HTTP method

4. `test_subscription_required_middleware()`
   - Try to access protected endpoint without active subscription
   - Assert status 403 or 402
   - **Avoid:** Check actual status code returned by middleware

5. `test_subscription_check_allows_active()`
   - Access protected endpoint with active subscription
   - Assert status 200
   - **Avoid:** Check which endpoints require subscription

---

### HIGH PRIORITY: Token Blacklist (5 tests)

#### File: `tests/unit/test_token_blacklist_service.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/core/token_blacklist.py` - check class/functions and Redis usage

**Tests to write:**

1. `test_blacklist_token()`
   - Blacklist a token
   - Assert token is in blacklist
   - **Avoid:** Check if it's class method or function

2. `test_check_blacklisted_token()`
   - Blacklist token, then check if blacklisted
   - Assert returns True
   - **Avoid:** Check method name (is_blacklisted? check_blacklisted?)

3. `test_check_non_blacklisted_token()`
   - Check token that's not blacklisted
   - Assert returns False
   - **Avoid:** Don't assume Redis is available, mock it

4. `test_blacklist_token_with_ttl()`
   - Blacklist token with TTL
   - Assert token expires after TTL
   - **Avoid:** Check if TTL is in seconds or milliseconds

5. `test_blacklist_multiple_tokens()`
   - Blacklist 3 tokens
   - Check all are blacklisted
   - Assert all return True
   - **Avoid:** Mock Redis to avoid real connections

---

### HIGH PRIORITY: Rate Limiting (5 tests)

#### File: `tests/unit/test_rate_limit_service.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/core/rate_limit.py` - check limiter configuration

**Tests to write:**

1. `test_rate_limit_not_exceeded()`
   - Make 5 requests (limit is 10)
   - Assert all succeed
   - **Avoid:** Mock Redis, don't use real rate limiter

2. `test_rate_limit_exceeded()`
   - Make 11 requests (limit is 10)
   - Assert 11th request raises RateLimitExceeded
   - **Avoid:** Check actual exception type

3. `test_rate_limit_reset_after_window()`
   - Exceed limit, wait for window to reset
   - Assert new requests succeed
   - **Avoid:** Don't use sleep(), mock time

4. `test_rate_limit_per_user()`
   - User A makes 10 requests
   - User B makes 10 requests
   - Assert both succeed (separate limits)
   - **Avoid:** Check if limit is per-user or per-IP

5. `test_rate_limit_different_endpoints()`
   - Check if different endpoints have different limits
   - Assert limits are independent
   - **Avoid:** Read rate_limit.py to see endpoint configs

---

### MEDIUM PRIORITY: Monitoring (5 tests)

#### File: `tests/unit/test_monitoring_service.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/core/monitoring.py` - check Sentry integration

**Tests to write:**

1. `test_capture_exception()`
   - Capture exception
   - Assert Sentry called
   - **Avoid:** Mock Sentry, don't send real events

2. `test_capture_message()`
   - Capture message
   - Assert Sentry called
   - **Avoid:** Mock sentry_sdk.capture_message

3. `test_set_user_context()`
   - Set user context
   - Assert context set
   - **Avoid:** Mock Sentry scope

4. `test_add_breadcrumb()`
   - Add breadcrumb
   - Assert breadcrumb added
   - **Avoid:** Mock Sentry

5. `test_monitoring_disabled_in_tests()`
   - Check monitoring is disabled in test env
   - Assert Sentry not initialized
   - **Avoid:** Check SENTRY_DSN env var

---

### MEDIUM PRIORITY: Dependencies (5 tests)

#### File: `tests/unit/test_dependencies.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/core/dependencies.py` - check all dependency functions

**Tests to write:**

1. `test_get_current_user_dependency()`
   - Mock valid token
   - Call get_current_user()
   - Assert returns user
   - **Avoid:** Check actual function signature

2. `test_get_current_user_invalid_token()`
   - Mock invalid token
   - Call get_current_user()
   - Assert raises HTTPException 401
   - **Avoid:** Check exception type

3. `test_get_current_active_user_dependency()`
   - Mock user with is_active=True
   - Call get_current_active_user()
   - Assert returns user
   - **Avoid:** Check if it also checks is_verified

4. `test_get_current_active_user_inactive()`
   - Mock user with is_active=False
   - Assert raises HTTPException 403
   - **Avoid:** Check actual status code

5. `test_require_admin_dependency()`
   - Mock user with role="admin"
   - Call require_admin()
   - Assert returns user
   - **Avoid:** Check if role is enum or string

---

### LOW PRIORITY: Email Service (5 tests)

#### File: `tests/unit/test_email_service_unit.py` (5 tests)

**BEFORE WRITING:** Read:
- `app/services/email_service.py` - check SendGrid integration

**Tests to write:**

1. `test_send_email_success(mock_sendgrid)`
   - Send email
   - Assert SendGrid called with correct params
   - **Avoid:** MUST mock SendGrid, never call real API

2. `test_send_email_with_template(mock_sendgrid)`
   - Send email with template
   - Assert template_id passed
   - **Avoid:** Mock SendGrid

3. `test_send_email_failure(mock_sendgrid)`
   - Mock SendGrid failure
   - Assert raises EmailSendError
   - **Avoid:** Check actual exception type

4. `test_send_bulk_emails(mock_sendgrid)`
   - Send multiple emails
   - Assert all sent
   - **Avoid:** Mock SendGrid batch send

5. `test_email_validation()`
   - Try to send to invalid email
   - Assert raises ValidationError
   - **Avoid:** Check validation logic

---

## ✅ VERIFICATION CHECKLIST (Use this before submitting tests!)

### Before Writing ANY Test:
- [ ] Read the actual source file (model/service/endpoint)
- [ ] List all fields/methods that exist
- [ ] Check field types (String vs Enum, UUID vs int)
- [ ] Check method signatures (async vs sync, parameters)
- [ ] Check import paths (services/ vs repositories/)
- [ ] Check existing fixtures in conftest.py
- [ ] Add `import pytest` at top of file

### For Model Tests:
- [ ] Read `app/models/{model}.py` completely
- [ ] List all Column() fields with their types
- [ ] Check for enums (are they defined?)
- [ ] Check relationships (ForeignKey, relationship())
- [ ] Don't assume fields exist - verify first!

### For Service Tests:
- [ ] Read `app/services/{service}.py` completely
- [ ] List all async def methods
- [ ] Check method parameters and return types
- [ ] Check what exceptions are raised
- [ ] Mock external dependencies (Redis, SendGrid, etc.)

### For API Tests:
- [ ] Read `app/api/v1/endpoints/{endpoint}.py`
- [ ] List all @router.get/post/patch/delete routes
- [ ] Check route paths (trailing slashes!)
- [ ] Check if auth required (use auth_headers fixture)
- [ ] Check response schema (list vs object with total)

### For Integration Tests:
- [ ] Use `async_client` fixture from conftest.py
- [ ] Use `auth_headers` fixture for authenticated requests
- [ ] Check actual HTTP methods (GET/POST/PATCH/DELETE)
- [ ] Check response status codes (200/201/400/403/404)
- [ ] Add trailing slashes to URLs if needed

---

## 📦 DELIVERABLE FORMAT

Create ONE file per test category:
- `tests/unit/test_invoice_service.py`
- `tests/integration/test_invoices_api.py`
- `tests/unit/test_subscription_service.py`
- `tests/integration/test_subscription_api.py`
- `tests/unit/test_token_blacklist_service.py`
- `tests/unit/test_rate_limit_service.py`
- `tests/unit/test_monitoring_service.py`
- `tests/unit/test_dependencies.py`
- `tests/unit/test_email_service_unit.py`

Each file must:
1. Start with `import pytest`
2. Import only modules that exist
3. Use correct field names from models
4. Mock external dependencies
5. Use existing fixtures from conftest.py
6. Follow async/sync patterns correctly

---

## 🎯 SUCCESS CRITERIA

**Test must:**
- ✅ Import without errors
- ✅ Run without collection errors
- ✅ Pass when code is correct
- ✅ Fail when code has bugs
- ✅ Use real field names from models
- ✅ Mock external services (Redis, SendGrid, Stripe)
- ✅ Follow project conventions

**Test must NOT:**
- ❌ Assume fields exist without checking
- ❌ Use wrong import paths
- ❌ Call real external APIs
- ❌ Have missing pytest import
- ❌ Use wrong async/sync patterns
- ❌ Create duplicate fixtures

---

## 📞 QUESTIONS TO ASK BEFORE WRITING:

1. Does this model field actually exist? (Read model file)
2. Is this field a String or Enum? (Check Column type)
3. What's the correct import path? (Check with ls app/services/)
4. Does this method exist? (Read service file)
5. Is this method async or sync? (Check def vs async def)
6. What exception does this raise? (Read service code)
7. Do I need to mock this? (Is it external: Redis/SendGrid/Stripe?)
8. What fixtures exist? (Read tests/conftest.py)

**GOLDEN RULE:** When in doubt, READ THE SOURCE CODE FIRST! 📖
