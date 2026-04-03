# Analiza porównawcza: AutoFlow vs FastHub

> Ostatnia aktualizacja: 2026-04-03
> Cel: Pełne porównanie obu systemów moduł po module. Baza wiedzy do migracji.

---

## 1. PODSUMOWANIE

| Aspekt | AutoFlow | FastHub |
|--------|----------|---------|
| **Przeznaczenie** | Automatyzacja procesów biznesowych (BPA) | Uniwersalny boilerplate SaaS |
| **Skala** | ~125 plików Python, ~62k LoC | ~376 plików (315 Py + 61 TS), ~47k LoC |
| **Endpointy** | 18 routerów, ~145 endpointów | 23 routery, ~80 endpointów |
| **Modele DB** | 23 tabele, Integer PK | 29 modeli, UUID PK |
| **Testy** | ~80+ (głównie e2e) | 645+ (unit + integration) |
| **Frontend** | React 18 + Tailwind (JSX) | React 19 + TypeScript + Tailwind 4 (TSX) |
| **Produkcja** | Render (Docker) | Render (Docker) |

---

## 2. PORÓWNANIE MODUŁ PO MODULE

### 2.1 Autentykacja (Auth)

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Password hashing | bcrypt (passlib) | bcrypt (passlib) | **Identyczne** |
| JWT algorytm | HS256 | HS256 | **Identyczne** |
| JWT claims | sub, email, tenant_id, exp | sub, jti, exp, iat, type | **FastHub** (JTI = blacklist) |
| Token expiry | 60min access / 30d refresh | 15-30min access / 7-30d refresh | **FastHub** (krótsze = bezpieczniejsze) |
| Token blacklist | Brak | Redis (via JTI) | **FastHub** |
| 2FA/TOTP | Brak | RFC 6238, backup codes | **FastHub** |
| Social login | Brak | Google, GitHub, Microsoft (PKCE) | **FastHub** |
| Magic links | Brak | Tak | **FastHub** |
| Session tracking | Brak | UserSession (device, IP, browser) | **FastHub** |
| Password reset | Własny (1h token) | Własny + magic link | **FastHub** |
| Password validation | Brak | 8+ chars, upper, lower, digit | **FastHub** |
| Demo mode | demo@autoflow.pl / demo123 | Konfigurowalny | **AutoFlow** (wygodniejsze dev) |

**Wniosek**: FastHub jest znacznie lepszy — JTI, 2FA, social login, sessions. AutoFlow ma tylko podstawy.

### 2.2 Użytkownicy i organizacje (Users/Org)

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| User PK | Integer (autoincrement) | UUID (uuid4) | **FastHub** (bezpieczniejsze) |
| User pola | email, name, company, plan, preferences | email, full_name, phone, position, language, timezone, avatar, OAuth IDs, 2FA | **FastHub** (bogatsze) |
| Organization pola | slug, name, company_name, nip, settings | slug, name, nip, regon, krs, billing address, logo, stripe_customer_id, restrict_scope | **FastHub** (pełniejsze) |
| Member role | String: system_admin, process_admin, department_manager, employee | Enum: OWNER, ADMIN, EDITOR, VIEWER | **Zależy** — AutoFlow ma role domenowe, FastHub generyczne |
| Member junction | OrganizationMember z permissions JSON override | Member z role enum | **AutoFlow** (permissions override jest elastyczniejszy) |
| Multi-org | Tak (tenant_id) | Tak (Member junction, wiele org per user) | **FastHub** (user w wielu org jednocześnie) |

**Wniosek**: FastHub lepszy w core (UUID, bogate pola, multi-org). AutoFlow ma lepsze role domenowe (process_admin, department_manager) — do zachowania jako warstwa nad FastHub.

### 2.3 RBAC (Role-Based Access Control)

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| System | 4 string roles + permissions JSON | Permission + Role + RolePermission + UserRole (4 tabele) | **FastHub** (enterprise RBAC) |
| Granularność | processes.create, integrations.manage | processes.edit, billing.view, team.manage (dowolne) | **FastHub** (dowolne permissions) |
| Custom roles | Brak (4 stałe role) | Tak (per-organizacja) | **FastHub** |
| Permission override | JSON na OrganizationMember | Via custom Role | **AutoFlow** (prostsze), **FastHub** (skalowalniejsze) |
| Hierarchia | system_admin > process_admin > dept_manager > employee | Owner > Admin > Editor > Viewer | **Podobne** |

**Wniosek**: FastHub ma enterprise-grade RBAC. AutoFlow wystarczy dla prostych scenariuszy ale nie skaluje się.

### 2.4 Billing (Płatności)

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Bramki | Stripe (via fasthub_core, częściowo) | Stripe + PayU + Tpay + P24 + PayPal | **FastHub** (5 bramek) |
| Subscription model | Podstawowy (plan + status) | Pełny (gateway_id, grace_period, renewal_failures) | **FastHub** |
| Recurring | Stripe native only | RecurringManager (cron dla polskich bramek) | **FastHub** |
| Dunning | Brak | DunningPath + DunningStep + DunningEvent (12 action types) | **FastHub** |
| Kupony | Brak | Coupon + CouponUsage (%, fixed, per-plan) | **FastHub** |
| Payment methods | Brak | SavedPaymentMethod (tokenized cards) | **FastHub** |
| Feature flags | Brak | check_feature(), require_feature(), get_plan_features() | **FastHub** |
| Restrict scope | Brak | RestrictScope (no_create, view_only, full_block) | **FastHub** |
| Invoices | Brak | Invoice + PDF + Stripe sync + Fakturownia + KSeF | **FastHub** |
| Usage tracking | UsageRecord (prosty) | UsageRecord + BillingEvent + audit | **FastHub** |
| Billing plans | BillingPlan (basic) | BillingPlan + BillingAddon + TenantAddon | **FastHub** |

**Wniosek**: FastHub ZDECYDOWANIE lepszy — pełny system billing z dunning, kupony, 5 bramek, invoices, feature flags. AutoFlow ma tylko szkielet.

### 2.5 Notifikacje

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Kanały | in_app, email, sms, all | in_app + email (SendGrid) + SMS (SMSAPI) | **Podobne** |
| Preferencje | Brak | NotificationPreference per user per type | **FastHub** |
| MessageLog | Brak | MessageLog (tracking email/SMS delivery) | **FastHub** |
| Event-driven | Event bus handlers | Event bus + notification routing | **FastHub** |

### 2.6 Audit Log

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Pola | action, resource_type/id, actor, details, ip | action, resource_type/id, user_id, org_id, before/after, ip, user_agent, impersonation | **FastHub** (before/after snapshots!) |
| Sensitive filter | Brak | Automatyczne ukrywanie password, token, secret | **FastHub** |
| Auto-summary | Brak | Generowane z changes | **FastHub** |

### 2.7 Bezpieczeństwo (Security)

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Encryption | Fernet AES (thin wrapper z fasthub_core) | Fernet AES + mask_credentials + key rotation | **Identyczne** (AutoFlow używa fasthub_core) |
| SSRF protection | Brak (po audycie: basic) | SafeHttpClient (private IP block, redirect validation) | **FastHub** |
| Rate limiting | Per-IP (100/min) | Per-endpoint (auth: 5/min, API: 100/min) | **FastHub** (per-endpoint) |
| Security headers | Middleware (basic) | HSTS, X-Frame-Options, CSP, X-Content-Type-Options | **FastHub** |
| Input validation | Pydantic | Pydantic + SafeId, SafeSlug, SafeFilename validators | **FastHub** |
| SQL injection | SQLAlchemy ORM | SQLAlchemy ORM + query validator | **FastHub** |

### 2.8 Event Bus

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Implementacja | Redis pub/sub (thin wrapper) | EventBus singleton z wildcard patterns (fnmatch) | **Identyczne** (AutoFlow re-exportuje fasthub_core) |
| Handlers | Notification handlers | Notification + audit + webhook routing | **FastHub** (więcej integracji) |

### 2.9 Storage (Pliki)

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Implementacja | Brak | FileUpload model + Local/S3 backend + signed URLs + MIME validation | **FastHub** |

### 2.10 GDPR

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Export | Brak | ZIP export per-module (user, billing, audit, notifications) | **FastHub** |
| Anonymization | Brak | Irreversible anonymization | **FastHub** |
| Deletion | Brak | Scheduled with 14-day grace period | **FastHub** |
| DeletionRequest | Brak | Model + service + auto-export | **FastHub** |

### 2.11 Invitations

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Implementacja | Brak (invited_by field only) | Invitation model + token + expiry + accept/reject/cancel | **FastHub** |

### 2.12 Background Tasks

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Queue | Redis LPUSH (własny) | ARQ (async Redis) + Sync fallback | **FastHub** (ARQ production-grade) |
| Scheduler | Asyncio loop (własny, prosty) | ARQ cron + maintenance_tasks | **Podobne** — AutoFlow potrzebuje własny scheduler dla procesów |

### 2.13 Multi-tenancy

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Identyfikator | tenant_id = org.slug (string) | organization_id = UUID FK | **FastHub** (UUID FK = type-safe, relational) |
| Middleware | Custom (X-User-Id header fallback) | TenantMiddleware (ContextVar, JWT) | **FastHub** |
| Query isolation | Manual WHERE tenant_id = ... | tenant_query() helper | **FastHub** |

### 2.14 Email

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Transport | Brak (planowany) | SMTP + SendGrid + Console (factory) | **FastHub** |
| Templates | Brak | Jinja2, 8 szablonów HTML+TXT | **FastHub** |
| Tracking | Brak | MessageLog + SendGrid webhooks (bounce/complaint) | **FastHub** |

### 2.15 CLI

| Cecha | AutoFlow | FastHub | Który lepszy |
|-------|----------|---------|--------------|
| Implementacja | Brak | Typer: seed, create-admin, check, show-config, shell | **FastHub** |

---

## 3. CO JEST UNIKALNE DLA AUTOFLOW (nie ma w FastHub)

Te moduły są **domenowe** — specyficzne dla automatyzacji procesów:

### 3.1 Workflow Execution Engine
- `app/executor/context.py` — ExecutionContext, StepResult
- `app/executor/data_flow.py` — Variable resolution ({{step_N.field}})
- `app/executor/handlers.py` — ConnectorActionHandler, ConditionHandler, HttpRequestHandler
- `app/services/workflow_executor.py` — Orkiestrator workflow

### 3.2 Connector Registry (62+ providers)
- `app/services/connector_registry.py` — Registry pattern
- `app/integrations/` — 62+ native providers:
  - Google (Gmail, Drive, Calendar, Sheets, Contacts, Analytics, Ads, Meet, Translate, Vision)
  - Microsoft (Outlook, OneDrive, Teams, Excel, SharePoint, Planner, Power BI)
  - Polish: Fakturownia, KSeF, SMSAPI, LiveSpace, Bitrix24, mBank, ING, PKO BP
  - Marketing: HubSpot, Mailchimp, ActiveCampaign, SendGrid, Brevo, GetResponse, FreshMail, ConvertKit
  - AI: Claude API, OCR (Tesseract)
  - Email: IMAP/SMTP

### 3.3 Process Templates
- 20+ pre-built templates (email→invoice, CRM sync, etc.)
- Category-based organization
- Fork from template → custom process

### 3.4 Scheduler (Process-Aware)
- Cron expression parser
- Continuous mode (interval polling)
- Email trigger (polling inbox)
- Webhook trigger
- Error recovery with exponential backoff

### 3.5 Full-Text Search
- PostgreSQL tsvector + GIN indexes
- Search across processes, templates, integrations, tags

### 3.6 AI Result Cache
- SHA-256 content hashing
- TTL-based expiry
- Hit count tracking
- Schema-aware (same content, different schema = different cache)

### 3.7 Tagging System
- Polymorphic (tag any resource type)
- AI auto-tagging (confidence score)
- Manual + system tags

### 3.8 WebSocket Real-Time
- Channel-based subscriptions (process:5, execution:123, monitoring)
- Redis bridge for multi-worker
- Live execution log streaming

### 3.9 OAuth Integration Flow (for connectors)
- Google, Microsoft OAuth dance
- Token refresh, encrypted storage
- Resource discovery (folders, channels)

---

## 4. CO FASTHUB MA A AUTOFLOW NIE POTRZEBUJE

- **Frontend admin panel** (AdminShell.tsx) — AutoFlow ma własny UI
- **SuperAdmin panel** — AutoFlow będzie miał własny
- **Onboarding wizard** — AutoFlow ma inny flow

---

## 5. PORÓWNANIE TECHNOLOGII

| Aspekt | AutoFlow | FastHub | Uwagi |
|--------|----------|---------|-------|
| Python | 3.11 | 3.11 | Identyczne |
| FastAPI | 0.109 | 0.109 | Identyczne |
| SQLAlchemy | 2.0.25 async | 2.0.25 async | Identyczne |
| Alembic | 1.13 | 1.13 | Identyczne |
| Redis | 5.0.1 | 5.0.1 | Identyczne |
| JWT lib | python-jose | PyJWT | **FastHub lepszy** (python-jose deprecated) |
| Frontend | React 18, JSX, Tailwind | React 19, TypeScript, Tailwind 4 | **FastHub lepszy** (TS + nowsze wersje) |
| State mgmt | Context API | Zustand 5 | **FastHub lepszy** |
| Testy | pytest 7.4 | pytest 7.4 | Identyczne |
| HTTP client | httpx 0.26 | httpx 0.26 + requests | Identyczne |

---

## 6. ANALIZA JAKOŚCI KODU

| Aspekt | AutoFlow | FastHub | Ocena |
|--------|----------|---------|-------|
| Architektura | Clean (API→Service→Executor→Model) | Clean (API→Service→Core→Model) | Oba dobre |
| Async | Pełne async I/O | Pełne async I/O | Identyczne |
| Type hints | Python (dobre) | Python + TypeScript (pełne) | FastHub lepszy |
| Error handling | Dobre (graceful degradation) | Bardzo dobre (custom exceptions, audit) | FastHub lepszy |
| Logging | Podstawowe | structlog (JSON prod, colored dev) | FastHub lepszy |
| Testy | ~80 (e2e głównie) | 645+ (unit + integration + e2e) | FastHub DUŻO lepszy |
| Security | Dobre (po audycie) | Bardzo dobre (6 narzędzi security) | FastHub lepszy |
| Documentation | Docstrings | Docstrings + 3 pliki .md + AI docs | FastHub lepszy |
| Performance | Brak optymalizacji (N+1 queries) | Redis cache, pool, batch | FastHub lepszy |
| Technical debt | Scheduler (asyncio loop), brak ARQ | Minimalne | AutoFlow więcej debt |

---

## 7. PODSUMOWANIE — CO MIGRACJA DAJE

### AutoFlow zyska z fasthub_core:
1. **Auth**: 2FA, social login, sessions, magic links, JTI blacklist
2. **RBAC**: Enterprise permissions (4 tabele, custom roles per-org)
3. **Billing**: 5 bramek, dunning, kupony, payment methods, restrict scope, invoices
4. **Notifications**: Preferences, MessageLog, SendGrid tracking
5. **Audit**: Before/after snapshots, sensitive filter, IP+user-agent
6. **GDPR**: Export, anonymization, deletion
7. **Storage**: File uploads (S3/Local)
8. **Invitations**: Token-based team invites
9. **Security**: SSRF protection, SafeId/Slug/Filename validators
10. **Email**: Templates, SendGrid, SMTP, tracking
11. **CLI**: seed, create-admin, check, shell

### AutoFlow zachowa własne:
1. Workflow Execution Engine (core domain)
2. Connector Registry (62+ providers)
3. Process Templates + Scheduler
4. Full-Text Search
5. AI Result Cache
6. Tagging System
7. WebSocket Real-Time
8. OAuth Integration Flow (for connectors — osobny od social login!)
9. Frontend (React 18 — osobny od FastHub frontend)

### Kolizje do rozwiązania:
1. **Role**: AutoFlow ma role domenowe (process_admin, department_manager) — trzeba zmapować na FastHub RBAC
2. **Tenant ID**: String slug → UUID FK
3. **PK typ**: Integer → UUID
4. **JWT format**: Stare tokeny (bez JTI) → nowe (z JTI)
5. **Billing**: AutoFlow ma własny billing (kopiowany) — zastąpić fasthub_core
6. **Notification model**: Różne schematy — migracja danych
7. **Audit log**: Różne schematy — migracja danych

---

## 8. METRYKI PORÓWNAWCZE

| Metryka | AutoFlow | FastHub | Stosunek |
|---------|----------|---------|----------|
| Modele DB | 23 | 29 | 0.79x |
| Endpointy | ~145 | ~80 | 1.8x (AF ma więcej bo domain-heavy) |
| Testy | ~80 | 645+ | 0.12x (AF potrzebuje więcej testów) |
| Migracje Alembic | 8 | 18 | 0.44x |
| Payment gateways | 1 (Stripe partial) | 5 (pełne) | 0.2x |
| Integrations/Connectors | 62+ providers | 0 (nie dotyczy) | Unikalny AF |
| Security tools | 0 (thin wrappers) | 6 | FastHub dostarcza |
| Email templates | 0 | 8 | FastHub dostarcza |
| Frontend components | ~20 JSX | ~40 TSX | FastHub bogatszy |
