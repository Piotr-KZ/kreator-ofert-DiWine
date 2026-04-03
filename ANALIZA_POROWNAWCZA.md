# Szczegółowa analiza porównawcza: AutoFlow vs FastHub (tylko boilerplate)

> Ostatnia aktualizacja: 2026-04-03
> Porównanie TYLKO overlapping features (nie domain-specific jak workflow engine, connectors, scheduler)
> Analiza na poziomie kodu — konkretne funkcje, linie, różnice

---

## 1. AUTENTYKACJA — linia po linii

### 1.1 Hashowanie haseł

| | AutoFlow (`app/core/auth.py`) | FastHub (`fasthub_core/auth/service.py`) |
|--|--|--|
| **Implementacja** | `pwd_context.hash(password)` | `pwd_context.hash(password)` |
| **Verify** | Try-catch, zwraca False na błąd | Bez try-catch, error bubbles up |
| **Biblioteka** | passlib + bcrypt | passlib + bcrypt |

**Werdykt**: Identyczne. AutoFlow ma lepszy error handling (defensive).

### 1.2 Walidacja siły hasła

| | AutoFlow | FastHub |
|--|--|--|
| **Implementacja** | **BRAK** — akceptuje `"a1"` jako hasło | 8+ znaków, wielka litera, mała litera, cyfra |

**Werdykt**: **FastHub wygrywa**. AutoFlow ma lukę bezpieczeństwa — brak jakiejkolwiek walidacji.

### 1.3 Tworzenie tokenów JWT

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Claims | `sub`, `email`, `tenant_id`, `exp`, `type` | `sub`, `jti`, `iat`, `exp`, `type` |
| JTI (token ID) | **BRAK** | UUID per token |
| iat (issued-at) | **BRAK** | `datetime.utcnow()` |
| UUID handling | N/A (int user_id) | Konwertuje UUID→string |
| Settings | Module-level zmienne | `get_settings()` (testowalne) |
| Blacklist | **NIEMOŻLIWY** (brak JTI) | Możliwy (JTI w Redis) |

**Werdykt**: **FastHub wygrywa zdecydowanie**. Bez JTI AutoFlow **nie może unieważnić tokenów** — logout jest fikcyjny.

### 1.4 Dekodowanie tokenów — KRYTYCZNY BUG w AutoFlow

```python
# AutoFlow — JEDNA funkcja dla wszystkich typów tokenów:
def decode_token(token: str) -> Optional[Dict]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload  # NIE sprawdza type!

# FastHub — OSOBNE funkcje:
def decode_access_token(token: str):
    payload = jwt.decode(...)
    if payload.get("type") != "access":
        return None  # BLOKUJE refresh token użyty jako access!

def decode_refresh_token(token: str):
    if payload.get("type") != "refresh":
        return None
```

**BUG**: W AutoFlow **refresh token może być użyty jako access token**. Atakujący z refresh tokenem (ważnym 30 dni) może go użyć zamiast access tokena (60 min). FastHub to blokuje.

**Werdykt**: **FastHub wygrywa**. AutoFlow ma podatność token confusion.

### 1.5 Rejestracja użytkownika

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Auto-tworzenie org | Tak (slug z emaila) | Tak (w service layer) |
| Email verification | **BRAK** — natychmiast login | Wymagana (token 24h) |
| Slug collision | Dokłada `-{user_id}` | W service layer |
| Domyślna rola | `system_admin` | `OWNER` |
| Demo mode | `is_demo=False` flag | Brak (strict) |

**Werdykt**: **FastHub wygrywa** — weryfikacja email zapobiega fake rejestracjom.

### 1.6 Login

| Cecha | AutoFlow | FastHub |
|--|--|--|
| 2FA/TOTP | **BRAK** | Tak (temp_token → weryfikacja kodu) |
| Session tracking | **BRAK** | UserSession (device, browser, OS, IP) |
| Device parsing | **BRAK** | User-Agent → device_type, browser, os |
| Rate limiting | **BRAK** | `@limiter.limit(RateLimits.AUTH_LOGIN)` |
| Demo password | Hardcoded `"demo123"` | Brak |
| Last login update | Tak | Tak |

**Werdykt**: **FastHub wygrywa zdecydowanie** — 2FA, sessions, device tracking, rate limiting.

### 1.7 Logout

| | AutoFlow | FastHub |
|--|--|--|
| **Implementacja** | **BRAK** — token ważny do exp | Blacklist via JTI w Redis |
| **Mechanizm** | — | `blacklist_token(jti, expires_in)` → Redis SETEX |
| **Backend** | — | RedisBlacklist + InMemoryBlacklist (fallback) |
| **Weryfikacja** | — | Każdy request sprawdza `is_token_blacklisted()` |

**Werdykt**: **FastHub wygrywa absolutnie**. AutoFlow NIE MA LOGOUT — tokeny działają do expiry.

### 1.8 2FA / TOTP

| | AutoFlow | FastHub |
|--|--|--|
| **Implementacja** | **BRAK** | RFC 6238, pyotp, QR code, backup codes |
| **Secret** | — | Fernet-encrypted w User.totp_secret |
| **Backup codes** | — | 10 jednorazowych (hex, 8 znaków) |
| **Verify window** | — | ±1 (30s tolerancja) |

**Werdykt**: **FastHub wygrywa absolutnie**.

### 1.9 Session tracking

| | AutoFlow | FastHub |
|--|--|--|
| **Model** | **BRAK** | UserSession (user_id, token_jti, device_type, device_name, browser, os, ip_address, is_active, last_active_at, expires_at, revoked_at) |
| **Device parser** | — | User-Agent → structured device info |
| **Revoke** | — | Endpoint do usunięcia sesji z innego urządzenia |

**Werdykt**: **FastHub wygrywa absolutnie**.

### 1.10 Magic links (passwordless login)

| | AutoFlow | FastHub |
|--|--|--|
| **Implementacja** | **BRAK** | `/magic-link/send` + `/magic-link/verify` |

### 1.11 Email verification

| | AutoFlow | FastHub |
|--|--|--|
| **Implementacja** | **BRAK** | Token 24h, endpoint `/verify-email` |

### 1.12 Password reset

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Token expiry | 1h | 1h |
| JTI w tokenie | **BRAK** | Tak (można unieważnić link) |
| Siła nowego hasła | **BRAK walidacji** | `validate_password_strength()` |
| Token type | `"reset"` | `"password_reset"` |

**Werdykt**: **FastHub wygrywa** — JTI + walidacja siły hasła.

### 1.13 Permissions middleware

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Fine-grained | `require_permission("processes.create")` | Tylko superuser/owner checks |
| Role hierarchy | `is_role_higher_or_equal()` dynamiczny | Hardcoded checks |
| Disable mode | `PERMISSIONS_ENABLED` flag (dev) | Brak |
| Error detail | Rich object `{error, permission, role, message}` | Simple string |
| Fallback | Demo user, X-User-Id header | Strict JWT only |

**Werdykt**: **AutoFlow wygrywa** — bardziej granularne permissions, lepsze errory, dev-friendly.
Ale FastHub ma to w RBAC module (4 tabele, custom roles per-org) — bardziej skalowalnie.

### AUTH PODSUMOWANIE

| Feature | AutoFlow | FastHub | Kto lepszy |
|---------|:--------:|:-------:|:----------:|
| Password hashing | ✅ | ✅ | Remis |
| Password strength | ❌ | ✅ | **FastHub** |
| JWT z JTI | ❌ | ✅ | **FastHub** |
| Token type safety | ❌ BUG | ✅ | **FastHub** |
| Email verification | ❌ | ✅ | **FastHub** |
| 2FA/TOTP | ❌ | ✅ | **FastHub** |
| Session tracking | ❌ | ✅ | **FastHub** |
| Magic links | ❌ | ✅ | **FastHub** |
| Token blacklist (logout) | ❌ | ✅ | **FastHub** |
| Rate limiting auth | ❌ | ✅ | **FastHub** |
| Password reset | ⚠️ | ✅ | **FastHub** |
| Fine-grained permissions | ✅ | ⚠️ | **AutoFlow** |
| Dev-friendly fallbacks | ✅ | ❌ | **AutoFlow** |
| Defensive error handling | ✅ | ❌ | **AutoFlow** |

**Wynik Auth: FastHub 11 : 3 AutoFlow**

---

## 2. BILLING — linia po linii

### 2.1 Modele billing

| Cecha | AutoFlow | FastHub |
|--|--|--|
| BillingPlan PK | Integer | Integer |
| BillingPlan pola | Identyczne (slug, name, price, limits, features JSON) | Identyczne |
| Subscription PK | Integer, tenant_id (string) | UUID, organization_id (UUID FK) |
| Subscription FK | Brak FK do organizations | Proper FK constraint |
| Multi-gateway | ❌ Stripe-only | ✅ gateway_id (stripe/payu/tpay/p24/paypal) |
| Saved card | ❌ | ✅ gateway_payment_token |
| Renewal tracking | ❌ | ✅ last_renewal_attempt, renewal_failures, grace_period_end |
| Amount storage | ❌ | ✅ amount (grosze) + currency |

**Werdykt**: **FastHub wygrywa** — multi-gateway, saved cards, renewal tracking.

### 2.2 Subscription enforcement

| | AutoFlow | FastHub |
|--|--|--|
| Middleware | **BRAK** — brak sprawdzania czy subscription aktywna | `SubscriptionChecker` middleware |
| Grace period | **BRAK** | 7 dni po past_due |
| Exempt paths | — | auth, health, billing (zawsze dostępne) |
| Response | — | 402 Payment Required |

**Werdykt**: **FastHub wygrywa absolutnie** — AutoFlow nie blokuje dostępu bez subskrypcji!

### 2.3 Limit calculation

| Cecha | AutoFlow | FastHub |
|--|--|--|
| billing_mode check | ✅ Sprawdza "fixed" vs "modular" | ❌ Zawsze dodaje addony (BUG!) |
| Unknown resource | ⚠️ Zwraca 999999 (allow) | ✅ Zwraca 0 (deny) |
| SQL efficiency | N+1 (helper function) | Single SUM query |

**Werdykt**: **Mieszany** — AutoFlow poprawnie obsługuje billing_mode, FastHub ma buga. Ale FastHub bezpieczniejszy przy unknown resource (fail-closed).

### 2.4 Usage tracking

Modele **identyczne** (te same 6 metryk: executions, ai_operations, processes, integrations, storage, webhooks).

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Commit strategy | `await db.commit()` | `await db.flush()` |
| Return value | Zwraca UsageRecord | Zwraca None |
| DRY | Helper `get_usage()` | Inline |

**Werdykt**: **AutoFlow lepszy** — commit() bezpieczniejszy (flush() może zgubić dane przy crash), zwraca obiekt.

### 2.5 Stripe webhook handling

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Implementacja | 200+ linii inline w service | Deleguje do `StripeWebhookHandler` class |
| Extensibility | Hardcoded 4 event types | Pluggable hooks (`on_checkout_completed = my_hook`) |
| Deduplication | ✅ `stripe_event_id` check | ✅ (w handler) |

**Werdykt**: **FastHub wygrywa** — pluggable, extensible, OOP.

### 2.6 Payment Gateway architecture

| | AutoFlow | FastHub |
|--|--|--|
| Bramki | Stripe only (direct calls) | 5 bramek via `PaymentGateway` ABC |
| Registry | ❌ | `PaymentGatewayRegistry` (auto-register z env) |
| Tokenization | ❌ | `SavedPaymentMethod` (tokenized cards) |
| Charge saved card | ❌ | `charge_saved_method()` |

**Werdykt**: **FastHub wygrywa absolutnie**.

### 2.7 Funkcje których AutoFlow NIE MA

| Feature | Co robi | Dlaczego ważne |
|---------|---------|----------------|
| **RecurringManager** | Cron do odnowień dla polskich bramek (PayU/Tpay/P24 nie mają native subs) | Bez tego polskie bramki = jednorazowe płatności |
| **RestrictScope** | Granularne blokowanie (`no_create`, `no_publish`, `view_only`, `full_block`) | Dunning: dzień 10 → blokuj tworzenie, dzień 20 → read-only |
| **Dunning paths** | Konfigurowalne sekwencje odzyskiwania (email→SMS→block→downgrade) | 12 action types, konfigurowalny per plan |
| **Kupony** | Kod rabatowy (%, fixed, per-plan, max uses, expiry) | Marketing/sprzedaż |
| **SavedPaymentMethod** | Tokenized cards per organizacja | Auto-renewal bez interakcji usera |
| **Payment model** | Historia płatności z gateway_payment_id | Audyt finansowy |
| **Admin billing API** | 21 endpointów do zarządzania planami/addonami | Konfiguracja bez kodu |

### BILLING PODSUMOWANIE

| Feature | AutoFlow | FastHub | Kto lepszy |
|---------|:--------:|:-------:|:----------:|
| BillingPlan model | ✅ | ✅ | Remis |
| Subscription FK integrity | ❌ string | ✅ UUID FK | **FastHub** |
| Multi-gateway (5 bramek) | ❌ | ✅ | **FastHub** |
| Subscription enforcement | ❌ | ✅ | **FastHub** |
| Saved cards / tokenization | ❌ | ✅ | **FastHub** |
| Offline renewal (RecurringMgr) | ❌ | ✅ | **FastHub** |
| Dunning paths | ❌ | ✅ | **FastHub** |
| RestrictScope | ❌ | ✅ | **FastHub** |
| Kupony | ❌ | ✅ | **FastHub** |
| Admin billing API | ❌ | ✅ | **FastHub** |
| billing_mode logic | ✅ | ❌ BUG | **AutoFlow** |
| Usage commit safety | ✅ | ❌ | **AutoFlow** |
| Webhook extensibility | ❌ | ✅ | **FastHub** |

**Wynik Billing: FastHub 11 : 2 AutoFlow**

---

## 3. USER / ORGANIZATION / MEMBER

### 3.1 User model

| Pole | AutoFlow | FastHub | Uwagi |
|------|:--------:|:-------:|-------|
| PK | Integer | UUID | FastHub bezpieczniejszy |
| email | ✅ | ✅ | Oba unique, indexed |
| name/full_name | ✅ | ✅ | |
| company | ✅ | ❌ (na Organization) | FastHub lepiej — firma to org, nie user |
| password_hash | ✅ | ✅ hashed_password | |
| tenant_id | ✅ string | ❌ (via Member) | FastHub lepiej — relacyjnie |
| is_active | ✅ | ✅ | |
| is_demo | ✅ | ❌ | AutoFlow specyficzne |
| plan | ✅ "free"/"pro" | ❌ (via Subscription) | FastHub lepiej — osobny model |
| preferences JSON | ✅ | ❌ (osobne pola) | FastHub lepiej — typed fields |
| phone | ❌ | ✅ | |
| position | ❌ | ✅ | |
| language | ❌ | ✅ | |
| timezone | ❌ | ✅ | |
| avatar_url | ❌ | ✅ | |
| google_id | ❌ | ✅ | Social login |
| github_id | ❌ | ✅ | Social login |
| microsoft_id | ❌ | ✅ | Social login |
| totp_secret | ❌ | ✅ (encrypted) | 2FA |
| totp_enabled | ❌ | ✅ | |
| backup_codes | ❌ | ✅ (encrypted) | |
| is_superadmin | ❌ | ✅ | Platform admin |
| is_email_verified | ❌ | ✅ | |
| magic_link_token | ❌ | ✅ | |

**Werdykt**: **FastHub wygrywa zdecydowanie** — bogatszy profil, OAuth, 2FA, proper structure.

### 3.2 Organization model

| Pole | AutoFlow | FastHub |
|------|:--------:|:-------:|
| PK | Integer | UUID |
| slug | ✅ | ✅ |
| name | ✅ | ✅ |
| nip | ✅ | ✅ |
| regon | ❌ | ✅ |
| krs | ❌ | ✅ |
| legal_form | ❌ | ✅ |
| billing address | ❌ | ✅ (street, city, postal, country) |
| website | ❌ | ✅ |
| logo_url | ❌ | ✅ |
| stripe_customer_id | ❌ | ✅ |
| restrict_scope JSONB | ❌ | ✅ |
| rodo_inspector | ❌ | ✅ (name + email) |
| settings JSON | ✅ | ❌ (typed fields) |

**Werdykt**: **FastHub wygrywa** — kompletne dane firmy, billing address, restrict_scope, RODO.

### 3.3 Member / Role

| Cecha | AutoFlow | FastHub |
|--|--|--|
| PK | Integer | UUID |
| Role type | String (`"system_admin"`) | Enum (`MemberRole.OWNER`) |
| Role values | system_admin, process_admin, department_manager, employee | OWNER, ADMIN, EDITOR, VIEWER |
| Permissions override | JSON column na member | Via RBAC (4 tabele) |
| Custom roles | ❌ | ✅ per-organization |
| Department field | ✅ | ❌ |
| Job title | ✅ | ❌ |

**Werdykt**: **Mieszany** — FastHub ma lepszy RBAC (database-driven, custom roles), ale AutoFlow ma przydatne pola domenowe (department, job_title) i role specyficzne dla automatyzacji (process_admin, department_manager).

---

## 4. RBAC / PERMISSIONS

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Architektura | Hardcoded dict w Python | 4 tabele DB (Permission, Role, RolePermission, UserRole) |
| Custom roles | ❌ | ✅ per-organization |
| Admin-editable | ❌ (wymaga zmian kodu) | ✅ (endpoints + seeding) |
| Owner bypass | ❌ (system_admin ma listę) | ✅ (`"*"` = all permissions) |
| Permission strings | `"processes.create"`, `"integrations.manage"` | `"team.view_members"`, `"billing.change_plan"` |
| Seeding | Brak | `seed_permissions()` + `seed_organization_roles()` at startup |

**Werdykt**: **FastHub wygrywa** — enterprise RBAC, database-driven, edytowalny przez admina.

---

## 5. NOTIFIKACJE

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Model | user_id, tenant_id, title, message, severity, category, channel | user_id, org_id, type, title, message, link, triggered_by |
| Preferences per-user | ❌ | ✅ NotificationPreference (inapp, email per type) |
| Forced types | ❌ | ✅ security_alert, impersonation (nie da się wyłączyć) |
| Bulk send | ❌ | ✅ `send_to_many()` |
| Email transport | ❌ | ✅ SendGrid + SMTP factory |
| MessageLog | ❌ | ✅ tracking delivery |
| Severity field | ✅ (info/success/warning/error) | ❌ (type-based) |
| Resource link | ✅ (resource_type + resource_id) | ✅ (link URL) |

**Werdykt**: **FastHub wygrywa** — preferences, forced types, email integration, MessageLog.

---

## 6. AUDIT LOG

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Before/after snapshots | ❌ | ✅ `changes_before`, `changes_after` (JSON) |
| Auto-summary | ❌ | ✅ "Zmieniono plan: pro → enterprise" |
| Impersonation | ❌ | ✅ `impersonated_by` field |
| User-Agent | ❌ | ✅ |
| IP address | ✅ | ✅ |
| Actor format | `"user:email"`, `"ai:model"`, `"system"` | user_id + user_email (denormalized) |
| Sensitive filter | ❌ | ✅ password, token, secret auto-masked |
| Retention policy | ❌ | ✅ `cleanup_old_logs()` (default 90 days) |
| Stats | ❌ | ✅ `get_stats()` |
| Process/execution ref | ✅ | ❌ (generic) |

**Werdykt**: **FastHub wygrywa zdecydowanie** — snapshots, impersonation, retention, auto-summary. AutoFlow ma przydatne process_id/execution_id refs (domenowe).

---

## 7. ENCRYPTION / SECURITY

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Status | **Thin wrapper** — deleguje do fasthub_core | Pełna implementacja |
| Algorytm | Fernet AES-128 (via fasthub_core) | Fernet AES-128 |
| Key rotation | ✅ (via fasthub_core) | ✅ |
| Masking | ✅ (via fasthub_core) | ✅ |
| SSRF protection | ❌ (basic po audycie) | ✅ SafeHttpClient (private IP block, redirect validation) |
| Input validators | ❌ | ✅ SafeId, SafeSlug, SafeFilename |
| Path traversal | ❌ | ✅ `safe_path()` |
| SQL injection | SQLAlchemy ORM | SQLAlchemy ORM + query validator |

**Werdykt**: **FastHub wygrywa** — AutoFlow deleguje, ale nie korzysta z SafeHttpClient i validators.

---

## 8. MULTI-TENANCY

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Tenant identifier | `tenant_id` = org.slug (string) | `organization_id` = UUID FK |
| Type safety | ❌ string (typo = data leak) | ✅ UUID (compile-time check) |
| Enforcement | Manual WHERE w każdym query | ContextVar middleware + `tenant_query()` helper |
| Multi-org per user | ✅ via OrganizationMember | ✅ via Member |
| Header | X-User-Id (dev), JWT (prod) | X-Organization-Id |

**Werdykt**: **FastHub wygrywa** — UUID FK = relacyjna integralność, middleware enforcement.

---

## 9. MIDDLEWARE

| Cecha | AutoFlow | FastHub |
|--|--|--|
| Security headers | Re-export z fasthub_core | HSTS, X-Frame, CSP, Referrer-Policy, Permissions-Policy |
| Request logging | Brak (w FastHub middleware) | Structured (method, path, status, duration, IP, User-Agent) |
| Rate limiting | ✅ In-memory (100/min, OAuth 20/min) | Brak w core (domain-specific) |
| Billing enforcement | ✅ `require_limit()` dependency | Brak (billing to domain) |

**Werdykt**: **Mieszany** — FastHub ma lepsze headers i logging, AutoFlow ma rate limiting i billing enforcement (domenowe).

---

## 10. ARCHITEKTURA BAZY DANYCH — kluczowe różnice

> **To jest najważniejsza sekcja tego dokumentu.** Różnice w architekturze DB to "poważna zmiana" — nie prosty swap modeli.

### 10.1 Składnia SQLAlchemy

| | AutoFlow | FastHub |
|--|---------|---------|
| **Wersja** | **2.0** — `Mapped[]` + `mapped_column()` | **1.x** — `Column()` + `declarative_base()` |
| **Type hints** | Natywne (Python typing) | Brak (runtime inference) |
| **IDE support** | Pełny autocomplete, mypy | Ograniczony |
| **Przyszłość** | Oficjalny styl SQLAlchemy 2.x | Legacy, będzie deprecated |

**Werdykt**: **AutoFlow wygrywa** — FastHub używa przestarzałej składni.

### 10.2 CHECK constraints na poziomie DB

| | AutoFlow | FastHub |
|--|---------|---------|
| **Ilość** | **9** (na 5 modelach) | **1** (tylko w migracji, nie w modelu) |
| **Pokrycie** | role, status, severity, channel, run_mode, source, interval | role member (w Alembic) |
| **Enforcement** | DB-level (nie da się ominąć) | Brak — tylko Python-level walidacja |

**Werdykt**: **AutoFlow wygrywa zdecydowanie** — integralność danych na poziomie bazy.

### 10.3 Denormalizacja strategiczna

| | AutoFlow | FastHub |
|--|---------|---------|
| **Wzorce** | **7** udokumentowanych | **0** |
| **Przykłady** | `last_run_at`, `total_executions`, `successful_executions`, `failed_executions`, `consecutive_failures`, `trigger_type`, `usage_count`, `resource_name` | — |
| **Cel** | Dashboard bez JOIN-ów, circuit-breaker bez scan | — |

**Werdykt**: **AutoFlow wygrywa** — przemyślana optymalizacja dla realnych use-cases.

### 10.4 Cross-database support

| | AutoFlow | FastHub |
|--|---------|---------|
| **Dev DB** | **SQLite** (zero setup, zero Docker) | PostgreSQL (wymaga Docker lub cloud) |
| **Prod DB** | PostgreSQL (asyncpg) | PostgreSQL (asyncpg) |
| **Typy** | Portable: String, JSON, Integer, Text | PG-specific: UUID, JSONB, ARRAY, SQLEnum |
| **Migracje** | `render_as_batch=True` (SQLite + PG) | Tylko PostgreSQL |
| **Default URL** | `sqlite+aiosqlite:///./autoflow.db` | Brak (wymaga DATABASE_URL) |

**Werdykt**: **AutoFlow wygrywa** — dev bez Docker, testy lokalne natychmiast.

### 10.5 Polimorfizm

| | AutoFlow | FastHub |
|--|---------|---------|
| **Wzorce** | **3** generic FK (ResourceTag, AuditEntry, Notification) | **1** (FileUpload.entity_type) |
| **Zastosowanie** | Tagowanie dowolnego zasobu, audit dowolnego obiektu | Tylko storage |
| **Elastyczność** | Nowe resource_type bez zmiany schematu | Ograniczone |

**Werdykt**: **AutoFlow wygrywa** — elastyczny system tagowania i audytu.

### 10.6 Connection pooling

| | AutoFlow | FastHub |
|--|---------|---------|
| **Config** | **Brak** — domyślne (pool_size=5) | **Production-grade**: pool_size=20, max_overflow=10, pool_recycle=3600, pool_pre_ping=True |
| **Max połączeń** | 15 (5+10 default) | **30** (20+10) |
| **Health check** | Brak | pool_pre_ping (sprawdza przed użyciem) |
| **Recykling** | Brak (-1) | Co 1h (zapobiega stale connections) |

**Werdykt**: **FastHub wygrywa zdecydowanie** — production-ready pooling.

### 10.7 Primary Keys i Multi-tenancy

| | AutoFlow | FastHub |
|--|---------|---------|
| **PK typ** | Integer (sekwencyjne) | UUID (losowe) |
| **Bezpieczeństwo PK** | Zgadywalne (id=1, id=2...) | Nie do zgadnięcia |
| **Tenant model** | `tenant_id` = string (org.slug) | `organization_id` = UUID FK |
| **FK integrity** | Brak FK do organizations | Proper FK constraint |
| **Type safety** | String (literówka = data leak) | UUID (compile-time check) |

**Werdykt**: **FastHub wygrywa** — UUID PK + FK integrity = bezpieczeństwo.

### 10.8 Kolumny JSON

| | AutoFlow | FastHub |
|--|---------|---------|
| **Ilość** | **18** kolumn JSON | **12** (10 JSON + 1 JSONB + 1 ARRAY) |
| **Typ** | Portable `JSON` (działa na SQLite i PG) | Mix: JSON + PG-specific JSONB i ARRAY |
| **Indeksowalność** | Brak GIN (JSON nie wspiera) | JSONB wspiera GIN indexes |
| **Elastyczność** | Więcej flexible schema | Mniej, ale wydajniejsze query |

**Werdykt**: **Mieszany** — AutoFlow ma więcej elastyczności, FastHub lepszą wydajność query na JSONB.

### 10.9 Skala modeli

| | AutoFlow | FastHub |
|--|---------|---------|
| **Tabele** | 20 | 32 |
| **Boilerplate** | ~10 (user, org, member, billing, audit, notifications) | ~27 (+ RBAC, GDPR, sessions, invitations, dunning, coupons, payments, webhooks) |
| **Domain** | ~10 (process, execution, integration, resource, template, tag, AI cache, settings) | ~5 (tylko billing-specific) |

**Werdykt**: **FastHub wygrywa** w ilości boilerplate features.

---

## 11. PODSUMOWANIE GLOBALNE

### Scorecard — ZBALANSOWANY

| Obszar | AutoFlow | FastHub | Wygrywa |
|--------|:--------:|:-------:|:-------:|
| **Auth (feature-level)** | 3 | 11 | FastHub |
| **Billing (feature-level)** | 2 | 11 | FastHub |
| **User/Org models** | 1 | 4 | FastHub |
| **RBAC** | 1 | 3 | FastHub |
| **Notifications** | 1 | 4 | FastHub |
| **Audit** | 1 | 5 | FastHub |
| **Security tools** | 0 | 4 | FastHub |
| **Multi-tenancy (enforcement)** | 0 | 3 | FastHub |
| **Middleware** | 2 | 2 | Remis |
| **Składnia SQLAlchemy** | 3 | 0 | **AutoFlow** |
| **CHECK constraints** | 3 | 0 | **AutoFlow** |
| **Denormalizacja** | 3 | 0 | **AutoFlow** |
| **Cross-DB / dev experience** | 3 | 0 | **AutoFlow** |
| **Polimorfizm** | 2 | 0 | **AutoFlow** |
| **Connection pooling** | 0 | 3 | FastHub |
| **JSON elastyczność** | 2 | 1 | **AutoFlow** |
| **PK / FK bezpieczeństwo** | 0 | 3 | FastHub |
| **RAZEM** | **27** | **54** | **FastHub** |

### Kluczowy wniosek

**FastHub wygrywa w FEATURE-ach** (auth, billing, RBAC — bo to boilerplate z 29 briefami rozwoju).

**AutoFlow wygrywa w ARCHITEKTURZE BAZY DANYCH** (nowoczesna składnia, constraints, denormalizacja, przenośność, polimorfizm).

**Migracja to "poważna zmiana"** bo wymaga:
1. **Integer → UUID PK** we WSZYSTKICH 20 tabelach + FK
2. **String tenant_id → UUID FK** — zmiana modelu multi-tenancy
3. **SQLAlchemy 2.0 → 1.x** — DEGRADACJA składni (chyba że fasthub_core zostanie zaktualizowany)
4. **9 CHECK constraints** — do zachowania (FastHub ich nie ma)
5. **7 wzorców denormalizacji** — muszą przetrwać migrację
6. **Cross-DB support** — zostanie UTRACONA (FastHub wymaga PostgreSQL)
7. **3 wzorce polimorficzne** — muszą współgrać z UUID PK
8. **18 kolumn JSON** — migracja danych

### Rekomendacja

Zamiast "AutoFlow adoptuje FastHub modele", rozważyć **hybrydowe podejście**:
- **Z FastHub wziąć**: auth features (2FA, sessions, blacklist), billing features (5 bramek, dunning, kupony), RBAC (4 tabele), UUID PK, FK integrity, connection pooling
- **Z AutoFlow zachować**: SQLAlchemy 2.0 składnię, CHECK constraints, denormalizację, polimorfizm, member metadata
- **Rozwiązać**: cross-DB support (albo wymóc PostgreSQL, albo zaktualizować fasthub_core)

### Krytyczne problemy AutoFlow (do naprawienia)

1. **Token confusion bug** — refresh token działa jako access token
2. **Brak logout** — tokeny nie mogą być unieważnione (brak JTI)
3. **Brak walidacji siły hasła** — akceptuje `"a1"`
4. **Brak email verification** — fake rejestracje
5. **Brak subscription enforcement** — dostęp bez płatności
6. **String tenant_id** — brak FK integrity, ryzyko data leak
7. **Integer PK** — guessable, sequential
8. **Brak connection pooling** — domyślne 5 połączeń

### Co AutoFlow robi lepiej niż FastHub

1. **SQLAlchemy 2.0 składnia** — nowoczesna, typed, IDE-friendly (FastHub ma legacy 1.x)
2. **9 CHECK constraints** — integralność danych na DB-level (FastHub ma 1)
3. **7 wzorców denormalizacji** — dashboard bez JOIN-ów (FastHub ma 0)
4. **Cross-DB support** — dev na SQLite bez Docker (FastHub wymaga PostgreSQL)
5. **render_as_batch migracje** — działają na SQLite i PG (FastHub tylko PG)
6. **3 wzorce polimorficzne** — elastyczne tagowanie i audit (FastHub ma 1)
7. **Fine-grained permissions** — `require_permission("processes.create")`
8. **Dev-friendly fallbacks** — demo user, X-User-Id, PERMISSIONS_ENABLED
9. **billing_mode logic** — poprawnie ignoruje addony w trybie "fixed" (FastHub ma buga)
10. **Member metadata** — job_title, department, permissions JSON override
11. **18 kolumn JSON** — elastyczny schemat
12. **Rate limiting out-of-box** — per-endpoint z sensownymi defaultami

### Co AutoFlow zyska z migracji do fasthub_core

| Feature | Wartość biznesowa |
|---------|-------------------|
| 2FA/TOTP + backup codes | Compliance, bezpieczeństwo |
| Social login (Google/GitHub/MS) | Łatwiejsza rejestracja |
| Session tracking | Bezpieczeństwo (widać loginy) |
| Magic links | UX (passwordless) |
| Token blacklist (logout) | Podstawa bezpieczeństwa |
| 5 bramek płatniczych | Polski rynek (PayU, Tpay, P24) |
| Dunning + RestrictScope | Odzyskiwanie płatności |
| Kupony | Marketing |
| Saved cards | Auto-renewal |
| RBAC (4 tabele, custom roles) | Enterprise customers |
| Notification preferences | UX (kontrola usera) |
| Audit snapshots | Compliance, debugging |
| GDPR (export, anonymize, delete) | Prawo EU |
| File storage (S3/Local) | Upload plików |
| Invitations (token-based) | Team onboarding |
| Email templates (Jinja2) | Professional communication |
| Connection pooling (production) | Stabilność pod obciążeniem |
| UUID PK | Bezpieczeństwo API |
