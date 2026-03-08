# FastHub - Automated Tests

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (db_session, test_user, async_client, etc.)
├── unit/                    # Unit tests (151 tests)
│   ├── test_admin_service.py
│   ├── test_api_token_model.py
│   ├── test_audit_service.py
│   ├── test_base_model.py
│   ├── test_cache.py
│   ├── test_email_invitations.py
│   ├── test_member_model.py
│   ├── test_organization_service.py
│   └── test_request_logging.py
├── integration/             # Integration tests (49 tests)
│   ├── test_admin_api.py
│   ├── test_api_tokens_api.py
│   ├── test_auth_api.py
│   ├── test_auth_edge_cases.py
│   ├── test_authorization_edge_cases.py
│   ├── test_database_errors.py
│   ├── test_health_api.py
│   ├── test_members_api.py
│   ├── test_organizations_api.py
│   ├── test_rate_limiting_api.py
│   └── test_users_api.py
```

## Running Tests

### With Docker:

```bash
# All tests
docker-compose exec backend pytest

# Unit tests only
docker-compose exec backend pytest tests/unit/ -v

# Integration tests only
docker-compose exec backend pytest tests/integration/ -v

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

### Without Docker:

```bash
cd fasthub-backend
pytest
pytest --cov=app --cov-report=html
```

## CI/CD

Tests run automatically via GitHub Actions on every push and PR:
- **Backend Tests** workflow: runs unit + integration tests with PostgreSQL
- **Frontend Tests** workflow: runs `npm run build`

Both checks must pass before merging to main (branch protection).

## Test Results

```
Unit Tests:        151 passed (100%)
Integration Tests:  49 passed (100%)
TOTAL:             200 passed
Coverage:           55%
```

## Key Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `db_session` | Async SQLAlchemy session with auto-cleanup (TRUNCATE) |
| `test_user` | User test@example.com with membership in test_organization |
| `test_admin` | SuperUser admin@example.com |
| `test_organization` | Organization "Test Organization" |
| `async_client` | AsyncClient with rate limiter disabled |
| `auth_headers` | JWT Bearer headers for test_user |
| `admin_headers` | JWT Bearer headers for test_admin |
| `test_api_token` | API token for test_user |
| `test_subscription` | Active subscription for test_organization |
| `test_invoice` | Paid invoice INV-TEST-001 |
