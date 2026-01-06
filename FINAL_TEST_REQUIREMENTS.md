# FastHub Backend - FINAL Test Requirements for 100% Coverage

**Generated:** 2026-01-06  
**Status:** 106 tests exist (66 unit + 40 integration), 94 passing, 12 failing

---

## ✅ EXISTING TESTS (106 total)

### Unit Tests (66 tests - ALL PASSING ✅)

| Test File | Tests | Covers | Status |
|-----------|-------|--------|--------|
| `test_admin_service.py` | 7 | `app/services/admin_service.py` | ✅ |
| `test_api_token_service.py` | 9 | `app/services/api_token_service.py` | ✅ |
| `test_audit_service.py` | 7 | `app/services/audit_service.py` | ✅ |
| `test_auth_service.py` | 10 | `app/services/auth_service.py` | ✅ |
| `test_config.py` | 4 | `app/core/config.py` | ✅ |
| `test_organization_model.py` | 4 | `app/models/organization.py` | ✅ |
| `test_organization_service.py` | 8 | `app/services/organization_service.py` | ✅ |
| `test_security_utils.py` | 4 | `app/core/security.py` | ✅ |
| `test_user_model.py` | 5 | `app/models/user.py` | ✅ |
| `test_user_service.py` | 8 | `app/services/user_service.py` | ✅ |

### Integration Tests (40 tests - 28 passing, 12 failing)

| Test File | Tests | Covers | Passing | Failing |
|-----------|-------|--------|---------|---------|
| `test_admin_api.py` | 6 | `app/api/v1/endpoints/admin.py` | 6 | 0 |
| `test_api_tokens_api.py` | 5 | `app/api/v1/endpoints/api_tokens.py` | 0 | 5 |
| `test_auth_api.py` | 14 | `app/api/v1/endpoints/auth.py` | 14 | 0 |
| `test_members_api.py` | 4 | `app/api/v1/endpoints/members.py` | 0 | 4 |
| `test_organizations_api.py` | 4 | `app/api/v1/endpoints/organizations.py` | 1 | 3 |
| `test_users_api.py` | 7 | `app/api/v1/endpoints/users.py` | 7 | 0 |

---

## ❌ MISSING TESTS (80 tests needed)

### 1. Core Infrastructure (24 tests)

#### `tests/unit/test_cache.py` → `app/core/cache.py` (4 tests)
```python
async def test_cache_set_and_get():
    """Test setting and retrieving cached values from Redis"""

async def test_cache_expiration():
    """Test cache entries expire after TTL"""

async def test_cache_delete():
    """Test deleting cached entries"""

async def test_cache_connection_failure():
    """Test graceful handling when Redis is unavailable"""
```

#### `tests/unit/test_rate_limit.py` → `app/core/rate_limit.py` (4 tests)
```python
def test_rate_limit_enforcement():
    """Test requests are blocked after exceeding rate limit"""

def test_rate_limit_reset_after_window():
    """Test rate limit counter resets after time window"""

def test_rate_limit_per_endpoint():
    """Test different endpoints have different rate limits"""

def test_rate_limit_bypass():
    """Test whitelisted IPs bypass rate limiting"""
```

#### `tests/unit/test_token_blacklist.py` → `app/core/token_blacklist.py` (4 tests)
```python
async def test_add_token_to_blacklist():
    """Test adding JWT token to blacklist after logout"""

async def test_is_token_blacklisted():
    """Test checking if token is blacklisted"""

async def test_blacklist_expiration():
    """Test blacklisted tokens expire after JWT expiration time"""

async def test_blacklist_redis_failure():
    """Test graceful handling when Redis is unavailable"""
```

#### `tests/unit/test_monitoring.py` → `app/core/monitoring.py` (4 tests)
```python
def test_metric_collection():
    """Test metrics are collected and stored"""

def test_error_tracking():
    """Test errors are tracked with context"""

def test_performance_monitoring():
    """Test request duration is monitored"""

def test_health_metrics():
    """Test health check metrics are collected"""
```

#### `tests/unit/test_request_logging.py` → `app/middleware/request_logging.py` (4 tests)
```python
async def test_request_logging_format():
    """Test request logs contain method, path, status code"""

async def test_response_time_tracking():
    """Test response time is logged for each request"""

async def test_error_request_logging():
    """Test failed requests are logged with error details"""

async def test_sensitive_data_masking():
    """Test passwords and tokens are masked in logs"""
```

#### `tests/integration/test_health_api.py` → `app/api/v1/endpoints/health.py` (4 tests)
```python
async def test_health_check_endpoint():
    """Test GET /health returns 200 OK"""

async def test_database_connection_check():
    """Test health check verifies database connectivity"""

async def test_redis_connection_check():
    """Test health check verifies Redis connectivity"""

async def test_readiness_probe():
    """Test readiness probe returns ready status"""
```

---

### 2. Repository Layer (10 tests)

#### `tests/unit/test_user_repository.py` → `app/services/user_repository.py` (5 tests)
```python
async def test_get_user_by_email():
    """Test retrieving user by email address"""

async def test_get_user_by_id():
    """Test retrieving user by UUID"""

async def test_update_user_profile():
    """Test updating user profile fields"""

async def test_delete_user():
    """Test soft-deleting user account"""

async def test_search_users():
    """Test searching users by name or email"""
```

#### `tests/unit/test_organization_repository.py` → `app/services/organization_repository.py` (5 tests)
```python
async def test_get_organization_by_slug():
    """Test retrieving organization by slug"""

async def test_update_organization():
    """Test updating organization fields"""

async def test_delete_organization():
    """Test deleting organization"""

async def test_list_user_organizations():
    """Test listing all organizations user belongs to"""

async def test_slug_uniqueness():
    """Test slug generation ensures uniqueness"""
```

---

### 3. Model Tests (11 tests)

#### `tests/unit/test_api_token_model.py` → `app/models/api_token.py` (3 tests)
```python
def test_token_hash_validation():
    """Test token hash is validated correctly"""

def test_token_expiration_check():
    """Test expired tokens are detected"""

def test_last_used_timestamp_update():
    """Test last_used_at is updated on token use"""
```

#### `tests/unit/test_member_model.py` → `app/models/member.py` (3 tests)
```python
def test_member_role_validation():
    """Test member role must be admin or viewer"""

def test_member_permissions_check():
    """Test member permissions based on role"""

def test_member_joined_date():
    """Test joined_at is set automatically"""
```

#### `tests/unit/test_audit_log_model.py` → `app/models/audit_log.py` (3 tests)
```python
async def test_audit_log_creation():
    """Test audit log entry is created with all fields"""

async def test_audit_log_query_by_user():
    """Test querying audit logs by user_id"""

async def test_audit_log_query_by_action():
    """Test querying audit logs by action type"""
```

#### `tests/unit/test_base_model.py` → `app/models/base.py` (2 tests)
```python
def test_base_model_id_generation():
    """Test UUID is auto-generated for new models"""

def test_base_model_timestamps():
    """Test created_at and updated_at are set automatically"""
```

---

### 4. Schema Validation Tests (15 tests)

#### `tests/unit/test_schemas_validation.py` (15 tests)
```python
def test_user_schema_required_fields():
    """Test UserCreate requires email and password"""

def test_user_schema_email_validation():
    """Test UserCreate validates email format"""

def test_user_schema_password_length():
    """Test UserCreate validates password minimum length"""

def test_organization_schema_name_required():
    """Test OrganizationCreate requires name field"""

def test_organization_schema_name_length():
    """Test OrganizationCreate validates name length (max 255)"""

def test_member_schema_email_required():
    """Test MemberCreate requires email field"""

def test_member_schema_role_enum():
    """Test MemberCreate validates role is admin or viewer"""

def test_api_token_schema_name_required():
    """Test APITokenCreate requires name field"""

def test_api_token_schema_name_length():
    """Test APITokenCreate validates name length (max 255)"""

def test_auth_schema_email_format():
    """Test LoginRequest validates email format"""

def test_auth_schema_password_required():
    """Test LoginRequest requires password field"""

def test_admin_schema_user_id_uuid():
    """Test AdminUpdateUser validates user_id is valid UUID"""

def test_user_update_schema_optional_fields():
    """Test UserUpdate allows partial updates"""

def test_organization_update_schema_optional_fields():
    """Test OrganizationUpdate allows partial updates"""

def test_member_update_schema_role_only():
    """Test MemberUpdate only allows role field"""
```

---

### 5. Edge Cases & Error Handling (20 tests)

#### `tests/integration/test_auth_edge_cases.py` (5 tests)
```python
async def test_invalid_jwt_token():
    """Test request with malformed JWT returns 401"""

async def test_expired_jwt_token():
    """Test request with expired JWT returns 401"""

async def test_missing_authorization_header():
    """Test protected endpoint without auth header returns 401"""

async def test_invalid_credentials():
    """Test login with wrong password returns 401"""

async def test_unverified_email_access():
    """Test unverified user cannot access protected endpoints"""
```

#### `tests/integration/test_database_errors.py` (5 tests)
```python
async def test_database_connection_failure():
    """Test graceful error when database is unavailable"""

async def test_duplicate_key_violation():
    """Test creating user with existing email returns 400"""

async def test_foreign_key_constraint_violation():
    """Test deleting user with members returns error"""

async def test_transaction_rollback():
    """Test transaction rollback on error"""

async def test_null_constraint_violation():
    """Test creating record with missing required field returns 400"""
```

#### `tests/integration/test_rate_limiting_api.py` (5 tests)
```python
async def test_rate_limit_exceeded():
    """Test 429 error after exceeding rate limit"""

async def test_rate_limit_reset():
    """Test rate limit resets after time window"""

async def test_rate_limit_per_user():
    """Test rate limit is tracked per authenticated user"""

async def test_rate_limit_per_ip():
    """Test rate limit is tracked per IP address for anonymous requests"""

async def test_rate_limit_headers():
    """Test rate limit headers are returned (X-RateLimit-*)"""
```

#### `tests/integration/test_authorization_edge_cases.py` (5 tests)
```python
async def test_access_other_user_profile():
    """Test user cannot access another user's profile"""

async def test_access_other_organization():
    """Test user cannot access organization they don't belong to"""

async def test_non_admin_cannot_delete_members():
    """Test viewer role cannot delete organization members"""

async def test_non_owner_cannot_delete_organization():
    """Test admin cannot delete organization (only owner can)"""

async def test_blacklisted_token_rejected():
    """Test logged-out token is rejected"""
```

---

## 📊 FINAL SUMMARY

### Current State
- **Total Tests:** 106 (66 unit + 40 integration)
- **Passing:** 94 tests (88.7%)
- **Failing:** 12 tests (11.3%)

### Required to Add
- **Total Missing:** 80 tests
- **Breakdown:**
  - Core Infrastructure: 24 tests
  - Repository Layer: 10 tests
  - Model Tests: 11 tests
  - Schema Validation: 15 tests
  - Edge Cases: 20 tests

### Target for 100% Coverage
- **Total Tests:** 186 tests
- **Unit Tests:** 126 (66 existing + 60 new)
- **Integration Tests:** 60 (40 existing + 20 new)

---

## 🎯 PRIORITY ORDER FOR CLAUDE

### Phase 1: High Priority (28 tests)
1. `test_token_blacklist.py` (4 tests) - Security critical
2. `test_rate_limit.py` (4 tests) - Security critical
3. `test_health_api.py` (4 tests) - Production monitoring
4. `test_cache.py` (4 tests) - Performance critical
5. `test_user_repository.py` (5 tests) - Core functionality
6. `test_organization_repository.py` (5 tests) - Core functionality
7. `test_auth_edge_cases.py` (2 tests) - Security

### Phase 2: Medium Priority (27 tests)
1. `test_monitoring.py` (4 tests)
2. `test_request_logging.py` (4 tests)
3. `test_api_token_model.py` (3 tests)
4. `test_member_model.py` (3 tests)
5. `test_audit_log_model.py` (3 tests)
6. `test_base_model.py` (2 tests)
7. `test_database_errors.py` (5 tests)
8. `test_authorization_edge_cases.py` (3 tests)

### Phase 3: Low Priority (25 tests)
1. `test_schemas_validation.py` (15 tests)
2. `test_rate_limiting_api.py` (5 tests)
3. `test_auth_edge_cases.py` (3 remaining tests)
4. `test_authorization_edge_cases.py` (2 remaining tests)

---

## 📝 NOTES FOR CLAUDE

1. **All test names are final** - use exactly as written above
2. **All file paths are correct** - create files in specified locations
3. **All docstrings are provided** - copy exactly as written
4. **No email/invoice/subscription tests** - out of scope
5. **Use async/await** where specified
6. **Follow existing test patterns** in the codebase
7. **Mock external dependencies** (Redis, database) appropriately
8. **Each test should be independent** and not rely on test order

---

**Last Updated:** 2026-01-06
**Ready for:** Claude to implement all 80 missing tests
