# FastHub — Dokumentacja Techniczna AI

> Dla AI agentow i programistow. Kompletna referencja systemu.
> Wersja: 4.0 | Data: 2026-03-09
> Stan: Po mergu briefow 1-21 + Briefy 24-28 (extended models, GUS, 2FA, dunning, frontend konto)

---

## 1. Czym jest FastHub

Uniwersalny fundament SaaS. Nie jest aplikacja koncowa — jest platforma na ktorej buduje sie aplikacje (np. WebCreator, AutoFlow). Dostarcza 27+ modulow: auth (2FA, sesje), billing (dunning, historia platnosci), RBAC, GDPR, 5 bramek platnosci, social login, email templates, KSeF, task queue, multi-tenancy, GUS API, webhooks per organizacja.

---

## 2. Stos technologiczny

### Backend
| Warstwa | Technologia |
|---------|------------|
| Framework | FastAPI 0.109+ |
| Baza danych | PostgreSQL (asyncpg) |
| ORM | SQLAlchemy 2.0 (async) |
| Migracje | Alembic |
| Cache | Redis 7 |
| Auth | JWT (python-jose) + bcrypt 4.1.2 + TOTP (pyotp + qrcode) |
| Task Queue | ARQ (async Redis) / SyncBackend (dev) |
| Platnosci | Stripe, PayU, Tpay, P24, PayPal |
| Email | SMTP + Jinja2 HTML templates |
| Faktury | Fakturownia API + ReportLab PDF |
| Monitoring | Sentry (opcjonalny) |
| Logi | structlog (JSON prod / kolorowy dev) |
| Rate Limiting | slowapi |
| HTTP Clients | httpx (async, retry) |
| GUS API | gusregon (pobieranie danych firm z GUS/REGON) |
| Device Parser | user-agents (parsowanie User-Agent dla sesji) |
| CLI | Typer |

### Frontend
| Warstwa | Technologia |
|---------|------------|
| Framework | React 19 + TypeScript |
| Build | Vite 7 |
| CSS | Tailwind CSS 4 |
| Font | Outfit (Google Fonts, wagi 300-800) |
| UI Components | Wlasne: Btn, Fld, Tile, Chk, Rad, Toggle, SectionCard, StatusBadge, Lbl |
| Routing | React Router DOM 7 |
| State | Zustand 5 (authStore, orgStore, billingStore) |
| HTTP Client | Axios (interceptory: auto-refresh token, X-Organization-Id header) |
| Formularze | React Hook Form + Zod (dostepne, nie wszedzie uzywane) |
| Wykresy | Recharts 3 (dostepne) |

**UWAGA:** Frontend NIE uzywa Ant Design. Zostal zmigrowany na Tailwind + wlasne komponenty w Brief 1.

---

## 3. Struktura projektu

```
Fasthub/
├── fasthub-frontend/              # React SPA
│   ├── src/
│   │   ├── config/
│   │   │   └── app.config.ts      # Centralna konfiguracja (nazwa, logo, URL-e, design tokens)
│   │   ├── components/
│   │   │   ├── ui/                # Design system: Btn, Fld, Tile, Chk, Rad, Toggle, SectionCard, Lbl, StatusBadge
│   │   │   ├── layout/           # AppShell, SidebarLayout, WizardLayout
│   │   │   ├── shared/           # ErrorBoundary, Modal, EmptyState
│   │   │   └── auth/             # ProtectedRoute
│   │   ├── pages/                # LoginPage, DashboardPage, TeamPage, BillingPage, OnboardingPage, UsersPage, AccountPage, superadmin/
│   │   │   └── account/          # 9 zakladek konta: ProfileTab, CompanyTab, PlanTab, PaymentsTab, InvoicesTab, SecurityTab, TeamTab, NotificationsTab, ApiTab
│   │   ├── api/                  # Axios wrappers: auth, members, organizations, billing, users, superadmin, account, gus
│   │   ├── store/                # Zustand: authStore, orgStore, billingStore
│   │   ├── types/                # TypeScript interfaces: models.ts, api.ts
│   │   ├── router.tsx
│   │   └── App.tsx
│   └── package.json
│
├── fasthub-backend/               # FastAPI API server
│   ├── app/
│   │   ├── main.py               # Glowna aplikacja + middleware stack
│   │   ├── api/v1/
│   │   │   ├── api.py            # Router glowny (18 aktywnych routerow)
│   │   │   └── endpoints/        # auth, users, organizations, members, billing, invoices, admin, token_admin, api_tokens, health, subscription_status, gus, two_factor, sessions, dunning, payments, webhook_config
│   │   ├── models/               # Re-export z fasthub_core
│   │   ├── schemas/              # Pydantic DTOs: auth, user, organization, member, invoice, subscription, admin, api_token
│   │   ├── services/             # auth_service, organization_service, user_service, admin_service, email_service, invoice_service, audit_service
│   │   ├── core/                 # config (re-export), dependencies, rate_limit, cache, monitoring, logging
│   │   └── middleware/           # request_logging
│   ├── alembic/                  # Migracje bazy
│   └── tests/                    # unit/ + integration/
│
├── fasthub_core/                  # Uniwersalny pakiet (pip install)
│   ├── __init__.py               # Glowne eksporty
│   ├── config.py                 # Pydantic Settings (100+ pol konfiguracji)
│   ├── contracts.py              # 7 abstrakcyjnych interfejsow (ABC)
│   ├── contracts_impl.py         # Implementacje kontraktow
│   ├── auth/                     # JWT, bcrypt, blacklist, email verification, social login, social providers, social routes, TOTP (2FA), session_models, device_parser
│   ├── users/                    # User, Organization, Member modele + schemas
│   ├── rbac/                     # Permission, Role, RolePermission, UserRole, RBACService
│   ├── audit/                    # AuditLog, AuditService, request_context
│   ├── admin/                    # Super Admin dashboard
│   ├── billing/                  # Subscription, Invoice, BillingPlan, BillingService, API, subscription_check, feature_flags
│   │   ├── gateways/            # StripeGateway, PayUGateway, TpayGateway, P24Gateway, PayPalGateway
│   │   ├── payment_gateway.py   # PaymentGateway(ABC), PaymentStatus, PaymentMethod, PaymentResult
│   │   ├── payment_registry.py  # PaymentGatewayRegistry (multi-bramka singleton)
│   │   ├── stripe_webhooks.py   # StripeWebhookHandler (6 events, 4 hooks)
│   │   ├── recurring_manager.py # RecurringManager (cron, deleguje do DunningService)
│   │   ├── dunning_models.py    # DunningPath, DunningStep, DunningEvent
│   │   ├── dunning_service.py   # DunningService (konfigurowalne sciezki windykacji)
│   │   └── payment_models.py    # Payment (historia platnosci)
│   ├── clients/                  # BaseHTTPClient, StripeClient, PayUClient, TpayClient, P24Client, PayPalClient, FakturowniaClient, KSeFClient
│   ├── notifications/            # In-app + email, preferencje, templates
│   ├── realtime/                 # WebSocket ConnectionManager
│   ├── middleware/               # SecurityHeaders, RequestID, TenantMiddleware
│   ├── infrastructure/           # Redis service (pool, cache, pub/sub)
│   ├── events/                   # EventBus (emit, wildcard handlers)
│   ├── security/                 # Encryption (Fernet AES, key rotation)
│   ├── integrations/             # OAuth (PKCE), Webhooks (HMAC), GUS API, webhook_config, webhook_dispatcher
│   ├── storage/                  # FileUpload, LocalBackend, S3Backend, StorageService
│   ├── tasks/                    # TaskQueueBackend(ABC), ARQBackend, SyncBackend, worker
│   ├── tenancy/                  # TenantMiddleware, ContextVar, get_current_tenant
│   ├── gdpr/                     # ExportService, AnonymizeService, DeletionService, exporters/
│   ├── email/                    # TemplateEngine (Jinja2), templates/ (8 szablonow HTML)
│   ├── invitations/              # InvitationService, InvitationModel
│   ├── logging/                  # structlog config
│   ├── monitoring/               # Sentry init
│   ├── rate_limiting/            # slowapi limiter
│   ├── health/                   # HealthChecker, /health, /ready
│   ├── cli/                      # Typer commands: seed, create-admin, check, shell
│   └── db/                       # Async session, BaseModel, migrations
│
└── tests/                         # Testy fasthub_core (25 plikow, ~780 testow total)
```

---

## 4. Modele bazy danych

### User
```
Tabela: users
- id: UUID (PK)
- email: String(320) (unique, indexed)
- hashed_password: String(255)
- full_name: String(255) (nullable)
- phone: String(50) (nullable)                    ← Brief 24
- position: String(255) (nullable)                ← Brief 24
- language: String(10) (default: "pl")            ← Brief 24
- timezone: String(50) (default: "Europe/Warsaw") ← Brief 24
- is_active: Boolean (default: True)
- is_verified: Boolean (default: False)
- is_superuser: Boolean (default: False)
- is_superadmin: Boolean (default: False)
- is_email_verified: Boolean (default: False)
- email_verified_at: DateTime (nullable)
- magic_link_token: String(255) (nullable, indexed)
- magic_link_expires: DateTime (nullable)
- google_id: String(255) (unique, nullable, indexed)
- github_id: String(255) (unique, nullable, indexed)
- microsoft_id: String(255) (unique, nullable, indexed)
- oauth_provider: String(50) (nullable)
- avatar_url: String(500) (nullable)
- totp_secret: String(255) (nullable)             ← Brief 26
- totp_enabled: Boolean (default: False)           ← Brief 26
- totp_verified_at: DateTime (nullable)            ← Brief 26
- backup_codes: JSON (nullable)                    ← Brief 26
- created_at, updated_at: DateTime
Relacje: memberships → Member[], api_tokens → APIToken[], sessions → UserSession[]
```

### Organization
```
Tabela: organizations
- id: UUID (PK)
- name: String(255), slug: String(255) (unique, indexed)
- type: String(50) (nullable) — "business" | "individual"
- email: String(255), nip: String(50), phone: String(50) (nullable)
- legal_form: String(100) (nullable)                ← Brief 24
- regon: String(20) (nullable)                      ← Brief 24
- krs: String(20) (nullable)                        ← Brief 24
- website: String(500) (nullable)                   ← Brief 24
- logo_url: String(500) (nullable)                  ← Brief 24
- rodo_inspector_name: String(255) (nullable)       ← Brief 24
- rodo_inspector_email: String(255) (nullable)      ← Brief 24
- billing_street, billing_city, billing_postal_code, billing_country
- is_complete: Boolean (onboarding status)
- owner_id: UUID (FK → User)
- stripe_customer_id: String(255) (unique, nullable)
Relacje: members → Member[], subscriptions → Subscription[], invoices → Invoice[]
```

### Member
```
Tabela: members
- id: UUID (PK)
- user_id: UUID (FK → User, indexed)
- organization_id: UUID (FK → Organization, indexed)
- role: Enum("owner", "admin", "editor", "viewer")  ← Brief 24: rozszerzony enum
- joined_at: DateTime
UniqueConstraint: (user_id, organization_id)
```

### Subscription
```
Tabela: subscriptions
- id: UUID (PK)
- organization_id: UUID (FK → Organization)
- stripe_subscription_id: String(255) (unique)
- stripe_customer_id, stripe_price_id: String(255)
- status: Enum(active, canceled, incomplete, past_due, trialing, unpaid)
- current_period_start, current_period_end: DateTime
- cancel_at_period_end: Boolean
- canceled_at, trial_end: DateTime
- plan_id: Integer (FK → BillingPlan, nullable)
- billing_interval: String(20) (monthly | yearly)
- gateway_id: String(50) (nullable) — "stripe", "payu", "tpay", "p24", "paypal"
- amount: Integer (nullable) — kwota w groszach
- currency: String(3) (nullable)
```

### BillingPlan (Integer PK, nie UUID)
```
Tabela: billing_plans
- id: Integer (PK, auto)
- slug: String(50) (unique) — "free", "starter", "pro", "enterprise"
- name: String(100), description: Text
- billing_mode: String(20) — "fixed" | "modular"
- price_monthly, price_yearly: Float
- currency: String(3) (default: "PLN")
- stripe_price_monthly_id, stripe_price_yearly_id, stripe_product_id
- max_processes, max_executions_month, max_integrations, max_ai_operations_month, max_team_members, max_file_storage_mb: Integer
- features: JSON
- sort_order, badge, color, is_active, is_default, is_visible
```

### UserSession (Brief 26)
```
Tabela: user_sessions
- id: UUID (PK)
- user_id: UUID (FK → User, indexed)
- token_jti: String(255) (unique, indexed) — JWT ID
- device_name: String(255) (nullable) — np. "Chrome on Windows"
- device_type: String(50) (nullable) — "desktop" | "mobile" | "tablet"
- ip_address: String(45) (nullable)
- user_agent: Text (nullable)
- last_active_at: DateTime
- expires_at: DateTime
- is_active: Boolean (default: True)
- created_at: DateTime
```

### DunningPath / DunningStep / DunningEvent (Brief 27)
```
Tabela: dunning_paths
- id: UUID (PK), name: String(100), description: Text, is_default: Boolean, is_active: Boolean
- created_at, updated_at: DateTime

Tabela: dunning_steps
- id: UUID (PK), dunning_path_id: UUID (FK → DunningPath)
- day_offset: Integer — dzien od poczatku sciezki
- action_type: Enum (email_reminder, email_warning, email_final, retry_payment, restrict_access, block_access, downgrade_free, cancel_subscription, disable_sites, notify_admin, webhook)
- template_name: String(100) (nullable), metadata: JSON
- sort_order: Integer, is_active: Boolean

Tabela: dunning_events
- id: UUID (PK), subscription_id: UUID (FK → Subscription)
- dunning_step_id: UUID (FK → DunningStep, nullable)
- action_type: String(50), result: String(50) — "success" | "failed" | "skipped"
- details: JSON, executed_at: DateTime
```

### Payment (Brief 27)
```
Tabela: payments
- id: UUID (PK)
- organization_id: UUID (FK → Organization, indexed)
- subscription_id: UUID (FK → Subscription, nullable)
- amount: Integer — kwota w groszach
- currency: String(3) (default: "PLN")
- gateway_id: String(50), gateway_payment_id: String(255) (nullable)
- payment_method: String(50), payment_method_details: String(255) (nullable)
- status: String(20) — pending, completed, failed, refunded
- description: Text (nullable)
- completed_at, failed_at, refunded_at: DateTime (nullable)
- invoice_id: UUID (FK → Invoice, nullable)
- created_at: DateTime
```

### WebhookEndpoint / WebhookDelivery (Brief 27)
```
Tabela: webhook_endpoints
- id: UUID (PK)
- organization_id: UUID (FK → Organization, indexed)
- url: String(500), secret: String(255) — HMAC-SHA256 signing secret
- events: JSON — lista subskrybowanych eventow
- is_active: Boolean (default: True)
- consecutive_failures: Integer (default: 0) — auto-disable po 10
- created_at, updated_at: DateTime

Tabela: webhook_deliveries
- id: UUID (PK), endpoint_id: UUID (FK → WebhookEndpoint)
- event_type: String(100), payload: JSON
- status_code: Integer (nullable), response_body: Text (nullable)
- response_time_ms: Integer (nullable)
- success: Boolean, error: Text (nullable), attempt: Integer
- created_at: DateTime

13 typow eventow: subscription.created/updated/canceled, payment.completed/failed/refunded,
invoice.created/paid, member.added/removed, organization.updated, plan.changed, dunning.step_executed
```

### Inne tabele
- **Invoice** — organization_id, invoice_number, amount, status, stripe_invoice_id, fakturownia_id, pdf_url
- **AuditLog** — user_id, action, resource_type, resource_id, changes_before/after, ip_address, summary
- **Notification** — user_id, type, title, message, is_read
- **NotificationPreference** — user_id, notification_type, channel_inapp, channel_email
- **Permission, Role, RolePermission, UserRole** — RBAC (4 role systemowe: Wlasciciel, Admin, Edytor, Podglad)
- **APIToken** — user_id, token_hash, name, expires_at
- **BillingAddon, TenantAddon, UsageRecord, BillingEvent** — billing system
- **FileUpload** — organization_id, original_filename, mime_type, storage_backend, storage_path
- **DeletionRequest** — GDPR: user_id, status, execute_after, export_file_path
- **Invitation** — email, organization_id, role, token, expires_at, accepted_at

---

## 5. API Endpoints

### Auth — `/api/v1/auth`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/register` | Rejestracja (email + haslo + full_name) |
| POST | `/login` | Login → access_token + refresh_token |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Wylogowanie (blacklist token) |
| GET | `/me` | Profil zalogowanego usera |
| POST | `/verify-email` | Weryfikacja email tokenem |
| POST | `/password-reset/request` | Zadanie resetu hasla |
| POST | `/password-reset/confirm` | Potwierdzenie nowego hasla |
| POST | `/change-password` | Zmiana hasla (zalogowany) |
| POST | `/magic-link/send` | Wyslij magic link |
| POST | `/magic-link/verify` | Weryfikuj magic link |
| GET | `/{provider}/login` | Social login redirect (google/github/microsoft) |
| GET | `/{provider}/callback` | Social login callback → JWT |

### 2FA / TOTP — `/api/v1/auth/2fa` (Brief 26)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/setup` | Rozpocznij konfiguracje 2FA → QR code + manual key |
| POST | `/verify` | Zweryfikuj kod TOTP i aktywuj 2FA |
| POST | `/authenticate` | Weryfikuj TOTP przy logowaniu → pelny token |
| POST | `/disable` | Wylacz 2FA (wymaga hasla + kodu TOTP) |
| POST | `/regenerate-backup-codes` | Wygeneruj nowe kody zapasowe |

### Sessions — `/api/v1/sessions` (Brief 26)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/` | Lista aktywnych sesji usera (device, IP, last_active) |
| DELETE | `/{session_id}` | Wyloguj konkretna sesje |
| DELETE | `/all` | Wyloguj ze wszystkich urzadzen |

### GUS — `/api/v1/gus` (Brief 25)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/lookup` | Pobierz dane firmy z GUS/REGON po NIP |

### Users — `/api/v1/users`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/me` | Profil |
| PATCH | `/me` | Aktualizacja profilu (full_name) |
| GET | `/` | Lista userow (SuperAdmin, paginacja) |
| GET | `/{user_id}` | Szczegoly usera |
| PATCH | `/{user_id}` | Aktualizacja usera |
| DELETE | `/{user_id}` | Usun usera (SuperAdmin) |

### Organizations — `/api/v1/organizations`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/` | Utworz organizacje |
| GET | `/me` | Moja organizacja + statystyki (OrganizationWithStats: user_count, subscription_status) |
| GET | `/{org_id}` | Szczegoly (wymaga membership) |
| PATCH | `/{org_id}` | Aktualizuj (owner only) |
| DELETE | `/{org_id}` | Usun (owner only) |
| PATCH | `/{org_id}/complete` | Complete onboarding |
| POST | `/{org_id}/transfer-ownership` | Transfer ownership (owner only) |

### Members — (prefix="" w router)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/organizations/{org_id}/members` | Zapros czlonka (email + role) |
| GET | `/organizations/{org_id}/members` | Lista czlonkow (page, per_page, search, role) |
| DELETE | `/members/{member_id}` | Usun czlonka (member_id UUID, nie user_id) |
| PATCH | `/members/{member_id}` | Zmien role (member_id UUID) |

### Billing — (fasthub_core/billing/api.py, podlaczony w api.py)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/billing/subscription` | Subskrypcja organizacji (wymaga X-Organization-Id header) |
| GET | `/billing/usage` | Zuzycie zasobow |
| POST | `/billing/checkout` | Stripe Checkout Session |
| POST | `/billing/portal` | Stripe Customer Portal |
| POST | `/billing/webhook` | Stripe webhook handler |
| GET | `/catalog/plans` | Lista planow (publiczny) |
| GET | `/catalog/addons` | Lista addonow |

### Invoices — `/api/v1/invoices`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/` | Lista faktur organizacji |
| GET | `/{id}` | Szczegoly faktury |
| GET | `/{id}/pdf` | Pobierz PDF |

### Subscription Status
| GET | `/subscription/status` | Status subskrypcji z grace period info |

### Admin — `/api/v1/admin`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/stats` | Statystyki systemu |
| GET | `/users/recent` | Ostatni zarejestrowani |
| GET | `/organizations` | Lista organizacji |
| POST | `/broadcast` | Broadcast wiadomosc |

### Dunning (admin) — `/api/v1/admin/dunning` (Brief 27)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/paths` | Lista sciezek windykacji |
| GET | `/paths/{id}` | Szczegoly sciezki ze stepami |
| POST | `/paths` | Utworz sciezke windykacji |
| PATCH | `/paths/{id}` | Aktualizuj sciezke |
| DELETE | `/paths/{id}` | Usun sciezke |
| POST | `/paths/{id}/steps` | Dodaj krok do sciezki |
| PATCH | `/steps/{id}` | Aktualizuj krok |
| DELETE | `/steps/{id}` | Usun krok |
| GET | `/events` | Lista eventow windykacji |

### Payments — `/api/v1/billing/payments` (Brief 27)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/` | Historia platnosci organizacji (paginacja) |
| GET | `/{id}` | Szczegoly platnosci |

### Webhooks (per organizacja) — `/api/v1/webhooks` (Brief 27)
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/` | Lista webhookow organizacji |
| POST | `/` | Utworz webhook (URL + eventy) |
| PATCH | `/{id}` | Aktualizuj webhook |
| DELETE | `/{id}` | Usun webhook |
| POST | `/{id}/rotate-secret` | Rotacja HMAC secret |
| POST | `/{id}/test` | Wyslij testowy webhook |
| GET | `/{id}/deliveries` | Historia dostaw webhookow |

### Health
| GET | `/health` | Health check |
| GET | `/api/v1/health` | API health |

---

## 6. Architektura platnosci (Payment Gateway)

### Model multi-bramka
Bramki dzialaja JEDNOCZESNIE. Registry trzyma wszystkie aktywne:

```
PaymentGateway(ABC)
    ├── StripeGateway     → karta, BLIK, Google Pay, Apple Pay
    ├── PayUGateway       → BLIK, karta, przelew, Google Pay, Apple Pay
    ├── TpayGateway       → BLIK, karta, przelew, Google Pay, Apple Pay
    ├── P24Gateway        → BLIK, karta, przelew, Google Pay, Apple Pay
    └── PayPalGateway     → PayPal

PaymentGatewayRegistry.from_config() — auto-detect bramek z env
```

### Kluczowe klasy
- `PaymentGateway(ABC)` — kontrakt: gateway_id, get_payment_methods(), create_payment(), handle_webhook(), is_configured()
- `PaymentGatewayRegistry` — singleton, wiele bramek jednoczesnie, get_available_methods(), create_payment(gateway_id, ...)
- `PaymentStatus` — enum: pending, processing, completed, failed, canceled, refunded
- `PaymentResult` — dataclass: success, payment_id, payment_url, gateway_id, error
- `RecurringManager` — cron (co godzine): znajdz subskrypcje do odnowienia, deleguje do DunningService
- `DunningService` — konfigurowalne sciezki windykacji (default: 16 krokow od dnia 0 do 45), CRUD na sciezkach/krokach, historia eventow
- `WebhookDispatcher` — wysylka webhookow per organizacja, HMAC-SHA256, auto-disable po 10 kolejnych bledach

### Stripe Webhooks
StripeWebhookHandler: 6 eventow (checkout.completed, subscription.created/updated/deleted, payment.failed/succeeded), 4 hook points (on_checkout_completed, on_subscription_canceled, on_payment_failed, on_payment_succeeded), deduplication po stripe_event_id.

### Dodawanie nowej bramki
1. Stworz klase dziedziczaca po PaymentGateway
2. Zaimplementuj: gateway_id, get_payment_methods(), create_payment(), handle_webhook(), is_configured()
3. Zarejestruj w PaymentGatewayRegistry.from_config()
4. Dodaj klucze API do config.py

---

## 7. Kontrakty (fasthub_core/contracts.py)

| Kontrakt | Metody |
|----------|--------|
| AuthContract | hash_password, verify_password, create_access_token, create_refresh_token, decode_token, blacklist_token |
| UserContract | get_current_user, get_user, list_organization_users, get_user_role |
| PermissionContract | check_permission, get_user_permissions, assign_role, create_custom_role, register_app_permissions |
| BillingContract | get_subscription, check_limit, record_usage |
| AuditContract | log_action, get_audit_logs |
| NotificationContract | send_notification, send_email |
| EventBusContract | emit, on, off |
| DatabaseContract | get_db_session, get_engine |

---

## 8. Wymienne komponenty (pluggable)

| Komponent | Interfejs (ABC) | Implementacje | Config |
|-----------|----------------|---------------|--------|
| Email | EmailTransport | SMTPTransport, ConsoleTransport | SMTP_HOST |
| Storage | StorageBackend | LocalBackend, S3Backend | STORAGE_BACKEND |
| Task Queue | TaskQueueBackend | ARQBackend, SyncBackend | TASK_BACKEND |
| Platnosci | PaymentGateway | Stripe, PayU, Tpay, P24, PayPal | Klucze API per bramka |

---

## 9. GDPR / RODO

### Export (Art. 15, 20)
ExportRegistry + DataExporter(ABC). Kazdy modul rejestruje swoj eksporter. ZIP z JSON.

### Anonimizacja (Art. 17)
NIE kasowanie — zamiana danych na hash. email → "deleted_abc@anonymized.local", IP → "0.0.0.0". Faktury zachowane 5 lat.

### Deletion workflow
DeletionRequest → 14 dni grace → auto-export ZIP → anonimizacja → status=completed.

---

## 10. Frontend — design system

### Komponenty UI
| Komponent | Plik | Funkcja |
|-----------|------|---------|
| Btn | Btn.tsx | Przycisk (primary/secondary/ghost/danger, loading, type=submit) |
| Fld | Fld.tsx | Input/textarea (label, error, disabled, type) |
| Tile | Tile.tsx | Kafelek wyboru (green border gdy on) |
| Chk | Chk.tsx | Checkbox (green checkmark gdy on) |
| Rad | Rad.tsx | Radio (green dot gdy on) |
| Toggle | Toggle.tsx | Przelacznik on/off (green) |
| SectionCard | SectionCard.tsx | Karta sekcji (biala, border, title + desc) |
| Lbl | Lbl.tsx | Etykieta z numerem (indigo kolko + tytul) |
| StatusBadge | StatusBadge.tsx | Badge (success/warning/error/info/neutral) |

### Design tokens
```
Primary: indigo-600 (#4F46E5), hover: indigo-700
Selected: green-400 border + green-50 bg
Header: gray-950
Background: gray-50, Surface: white, Border: gray-200
Text: gray-900, Secondary: gray-500
Radius: rounded-xl, Font: Outfit 300-800
```

### Panel Konto — AccountPage (Brief 28)
9 zakladek w SidebarLayout:
| Zakladka | Plik | Funkcja |
|----------|------|---------|
| Profil | ProfileTab.tsx | Avatar, imie, email, telefon, stanowisko, jezyk, strefa czasowa |
| Firma | CompanyTab.tsx | GUS lookup (NIP), dane firmy, adres, logo, RODO inspektor |
| Plan | PlanTab.tsx | Aktualny plan, uzycie zasobow (progress bary), zmiana planu |
| Platnosci | PaymentsTab.tsx | Historia platnosci, timeline windykacji |
| Faktury | InvoicesTab.tsx | Lista faktur, PDF download, ustawienia emaila |
| Bezpieczenstwo | SecurityTab.tsx | Zmiana hasla, 2FA setup/disable, sesje, usuniecie konta |
| Zespol | TeamTab.tsx | Czlonkowie, zaproszenia, role, matryca uprawnien |
| Powiadomienia | NotificationsTab.tsx | 7 typow powiadomien, toggle email/app |
| API | ApiTab.tsx | Tokeny API (CRUD), webhook config, link do docs |

### Konfiguracja (app.config.ts)
Jedna zmiana nazwy/logo/kolorow → zmienia sie wszedzie. Zaden komponent nie ma hardcodowanej nazwy produktu.

---

## 11. Konfiguracja (.env)

Kluczowe zmienne:
```
# Obowiazkowe
DATABASE_URL=postgresql://user:pass@host:5432/fasthub
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL

# Stripe
STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET

# Polskie bramki (opcjonalne — auto-detect)
PAYU_POS_ID, PAYU_MD5_KEY, PAYU_CLIENT_ID, PAYU_CLIENT_SECRET, PAYU_SANDBOX=true
TPAY_CLIENT_ID, TPAY_CLIENT_SECRET, TPAY_SECURITY_CODE, TPAY_SANDBOX=true
P24_MERCHANT_ID, P24_POS_ID, P24_CRC_KEY, P24_SANDBOX=true
PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_SANDBOX=true

# Social Login (opcjonalne)
GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET

# Fakturownia (opcjonalne)
FAKTUROWNIA_API_TOKEN, FAKTUROWNIA_ACCOUNT

# GDPR
GDPR_DELETION_GRACE_DAYS=14
GDPR_AUTO_EXPORT_ON_DELETE=true

# Task Queue
TASK_BACKEND=arq  # arq | sync

# Recurring (polskie bramki)
RECURRING_GRACE_DAYS=14
RECURRING_REMINDER_DAYS=1,3,7

# 2FA / TOTP (Brief 26)
TOTP_ISSUER_NAME=FastHub
TOTP_TEMP_TOKEN_EXPIRE_MINUTES=5
SESSION_CLEANUP_DAYS=30

# GUS API (Brief 25)
GUS_API_KEY=your-gus-api-key

# Sentry (opcjonalne)
SENTRY_DSN=https://xxx@sentry.io/yyy
```

---

## 12. Testy

~780 testow (711 na main + 65 z briefow 25-28), CI: GitHub Actions.

```bash
# Wszystkie testy
python -m pytest tests/ -v

# Tylko unit
python -m pytest tests/ -v -k "not integration"

# Frontend build
cd fasthub-frontend && npm run build
```

---

## 13. Uwagi techniczne

- **bcrypt 5.0 NIE dziala z passlib 1.7.4** — uzywac bcrypt==4.1.2
- **WebSocket** — in-memory, jeden serwer. Multi-server wymaga Redis pub/sub (v2.1+)
- **HSTS** domyslnie wylaczony — wlaczyc po konfiguracji SSL
- **Migracje** uruchamiaja sie automatycznie na starcie (alembic upgrade head)
- **Redis graceful degradation** — gdy niedostepny, fallback na InMemory
- **Billing models** uzywaja Integer PK (nie UUID) — BillingPlan, BillingAddon, TenantAddon, UsageRecord, BillingEvent
- **RecurringManager** wymaga cron job (task queue) — co godzine process_renewals, deleguje do DunningService
- **DunningService** — konfigurowalne sciezki windykacji zamiast hardcodowanego grace period. 11 typow akcji, default 16 krokow (dzien 0-45)
- **WebhookDispatcher** — HMAC-SHA256 podpis, 10s timeout, auto-disable po 10 kolejnych bledach
- **2FA/TOTP** — pyotp + qrcode, kody zapasowe (hashed bcrypt), tymczasowy token (5 min) na weryfikacje przy logowaniu
- **UserSession** — sledzenie aktywnych sesji (device, IP, User-Agent), cleanup starszych niz 30 dni
- **GUS API** — gusregon, pobieranie danych firm po NIP (nazwa, adres, REGON, forma prawna)

---

*FastHub v4.0 | Dokumentacja AI | 2026-03-09 | Po briefach 1-28*
