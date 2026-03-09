# FastHub — Testy

> 200 testow (151 unit + 49 integration), 100% PASS
> CI: GitHub Actions (backend + frontend)

---

## Uruchamianie

```bash
# Backend — unit testy
cd fasthub-backend
pytest tests/unit/ -v

# Backend — integration testy (wymaga PostgreSQL + Redis)
pytest tests/integration/ -v

# Backend — wszystkie
pytest tests/ -v

# Frontend — build check (TypeScript + Vite)
cd fasthub-frontend
npm run build
```

---

## Struktura testow

```
fasthub-backend/tests/
├── conftest.py                          # Fixtures: db_session, test_user, auth_headers itp.
├── unit/                                # 16 plikow, ~151 testow
│   ├── test_admin_service.py
│   ├── test_api_token_model.py
│   ├── test_api_token_service.py
│   ├── test_audit_service.py
│   ├── test_auth_service.py
│   ├── test_base_model.py
│   ├── test_cache.py
│   ├── test_config.py
│   ├── test_email_invitations.py
│   ├── test_gdpr.py
│   ├── test_member_model.py
│   ├── test_organization_model.py
│   ├── test_organization_service.py
│   ├── test_request_logging.py
│   ├── test_security_utils.py
│   ├── test_user_model.py
│   └── test_user_service.py
├── integration/                         # 11 plikow, ~49 testow
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
└── fixtures/                            # Shared fixtures

tests/                                   # fasthub_core testy (root level, 22 pliki)
├── test_admin.py
├── test_audit_trail.py
├── test_auth_improvements.py
├── test_background_tasks.py
├── test_billing_system.py
├── test_contracts.py
├── test_events_bus.py
├── test_file_storage.py
├── test_infrastructure_redis.py
├── test_integrations_oauth.py
├── test_integrations_webhooks.py
├── test_ksef.py
├── test_notifications.py
├── test_payment_gateway.py
├── test_polish_gateways.py
├── test_production_infrastructure.py
├── test_rbac.py
├── test_realtime_security.py
├── test_security_encryption.py
├── test_security_headers_comparison.py
├── test_social_login.py
└── test_tenancy.py
```

---

## Fixtures (conftest.py)

| Fixture | Opis |
|---------|------|
| `db_session` | Async SQLAlchemy session, auto-rollback + TRUNCATE po tescie |
| `test_organization` | Organizacja "Test Organization" z stripe_customer_id |
| `test_user` | User z membership (admin) w test_organization |
| `test_admin` | SuperAdmin user z membership w test_organization |
| `owner_user` | Owner user (bez membership) |
| `auth_headers` | `{"Authorization": "Bearer ..."}` dla test_user |
| `admin_headers` | `{"Authorization": "Bearer ..."}` dla test_admin |
| `test_subscription` | Aktywna subskrypcja (30 dni) |
| `test_invoice` | Faktura "INV-TEST-001" (paid) |
| `test_api_token` | API token dla test_user |
| `async_client` | AsyncClient z wylaczonym rate limiterem |
| `client` | Sync TestClient |

---

## CI/CD (GitHub Actions)

### Backend Tests (`.github/workflows/backend-tests.yml`)
- **Trigger:** push do main/develop, PR do main
- **Services:** PostgreSQL 15 + Redis 7
- **Python:** 3.11
- **Steps:**
  1. Install fasthub_core (`pip install -e .`)
  2. Install backend dependencies
  3. Run Alembic migrations
  4. Run unit tests + coverage
  5. Run integration tests
  6. Coverage check (min 40%)
  7. Lint (Ruff, non-blocking)

### Frontend Tests (`.github/workflows/frontend-tests.yml`)
- **Trigger:** push do main/develop, PR do main
- **Node:** 18
- **Steps:**
  1. `npm ci`
  2. `npm run build` (TypeScript check + Vite build)

### Wymagania do merge
- Main branch jest chroniony — wymaga obu CI checkow (backend + frontend) do merge.

---

## Env vars dla testow

```env
DATABASE_URL=postgresql://postgres:testpass@localhost:5432/testdb
SECRET_KEY=test-secret-key-for-ci-testing
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=testing
```

---

## Uwagi

- Root-level testy (`fasthub-backend/tests/test_*.py`) sa legacy — nie uruchamiane w CI (problemy z transakcjami)
- `test_subscriptions_api.py` jest ignorowany w CI (`--ignore`)
- Rate limiter jest wylaczony w testach integracyjnych (fixture `async_client`)
- Testy uzywaja TRUNCATE zamiast DROP/CREATE tabel — szybsze
