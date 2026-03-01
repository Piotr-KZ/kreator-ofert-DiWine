# FastHub — Dokumentacja Techniczna

> Dla AI agentow i programistow. Ostatnia aktualizacja: 2026-03-01.

---

## 1. Czym jest FastHub

FastHub to **uniwersalny fundament SaaS** (Software as a Service). Nie jest aplikacja koncowa — jest platformą, na ktorej buduje sie aplikacje biznesowe (np. AutoFlow, FastCRM).

Dostarcza gotowe moduly ktorych kazdy SaaS potrzebuje: autentykacja, organizacje, role, powiadomienia, billing, audit trail, WebSocket. Dzieki temu nowa aplikacja nie zaczyna od zera.

**Architektura:**
```
fasthub-frontend/     React + Vite + Ant Design (UI)
fasthub-backend/      FastAPI + PostgreSQL + Redis (API + baza danych)
fasthub_core/         Uniwersalny pakiet Python (pip install)
```

---

## 2. Stos technologiczny

### Backend
| Warstwa | Technologia | Wersja |
|---------|------------|--------|
| Framework | FastAPI | 0.109.0 |
| Baza danych | PostgreSQL (async) | asyncpg 0.29.0 |
| ORM | SQLAlchemy | 2.0.25 |
| Migracje | Alembic | 1.13.1 |
| Cache / Blacklist | Redis | 5.0.1 |
| Auth | JWT (python-jose) + bcrypt | HS256 |
| Email | SendGrid + SMTP | 6.11.0 |
| Platnosci | Stripe | 7.11.0 |
| Rate Limiting | slowapi | 0.1.9 |
| Monitoring | Sentry | 2.48.0 |
| Task Queue | Celery | 5.3.6 |
| Logi | structlog | 24.4.0 |

### Frontend
| Warstwa | Technologia | Wersja |
|---------|------------|--------|
| Framework | React | 19.2.0 |
| Jezyk | TypeScript | ~5.9.3 |
| Build | Vite | 7.2.4 |
| UI | Ant Design | 6.1.2 |
| CSS | Tailwind CSS | 4.1.18 |
| Routing | React Router DOM | 7.11.0 |
| State | Zustand | 5.0.9 |
| Formularze | React Hook Form + Zod | 7.69.0 / 4.2.1 |
| HTTP Client | Axios | 1.13.2 |
| Wykresy | Recharts | 3.6.0 |

---

## 3. Struktura projektu

```
Fasthub/
├── fasthub-backend/           # API serwer
│   ├── app/
│   │   ├── main.py            # Glowna aplikacja FastAPI
│   │   ├── api/v1/
│   │   │   ├── api.py         # Router glowny
│   │   │   └── endpoints/     # Endpointy API
│   │   ├── models/            # SQLAlchemy modele
│   │   ├── schemas/           # Pydantic DTOs
│   │   ├── services/          # Logika biznesowa
│   │   ├── core/              # Config, security, dependencies
│   │   ├── db/                # Session, base
│   │   └── middleware/        # Custom middleware
│   ├── alembic/               # Migracje bazy
│   ├── tests/                 # Testy backend
│   └── requirements.txt
│
├── fasthub-frontend/          # Aplikacja kliencka
│   ├── src/
│   │   ├── api/               # Axios wrappers
│   │   ├── components/        # Komponenty React
│   │   ├── pages/             # Strony
│   │   ├── store/             # Zustand stores
│   │   ├── types/             # TypeScript interfaces
│   │   ├── router.tsx         # Routing
│   │   └── App.tsx            # Root
│   └── vite.config.ts
│
├── fasthub_core/              # Uniwersalny pakiet
│   ├── __init__.py            # Glowne eksporty
│   ├── config.py              # Pydantic Settings
│   ├── contracts.py           # 7 abstrakcyjnych interfejsow
│   ├── contracts_impl.py      # Implementacje kontraktow
│   ├── auth/                  # JWT, bcrypt, blacklist, weryfikacja email
│   ├── users/                 # User, Organization, Member modele
│   ├── rbac/                  # Role, Permission, RBACService
│   ├── audit/                 # AuditLog, AuditService
│   ├── admin/                 # Super Admin dashboard
│   ├── billing/               # Subscription, Invoice
│   ├── notifications/         # In-app + email, preferencje
│   ├── realtime/              # WebSocket ConnectionManager
│   ├── middleware/             # Security headers, Request ID
│   └── db/                    # Async session, BaseModel
│
└── tests/                     # Testy fasthub_core
```

---

## 4. Modele bazy danych

### 4.1 User
```
Tabela: users
- id: UUID (PK)
- email: String (unique, indexed)
- hashed_password: String
- full_name: String
- is_active: Boolean (default: True)
- is_verified: Boolean (default: False)
- is_superuser: Boolean (default: False)
- is_email_verified: Boolean
- email_verified_at: DateTime
- magic_link_token: String (nullable, indexed)
- magic_link_expires: DateTime
- created_at, updated_at: DateTime
Relacje: memberships → Member[], api_tokens → APIToken[]
```

### 4.2 Organization
```
Tabela: organizations
- id: UUID (PK)
- name, slug: String (slug unique)
- type: String ("business" | "individual")
- email, nip, phone: String (nullable)
- billing_street, billing_city, billing_postal_code, billing_country
- is_complete: Boolean (onboarding)
- owner_id: UUID (FK → User)
- stripe_customer_id: String (unique)
- created_at, updated_at
Relacje: members → Member[], subscriptions → Subscription[], invoices → Invoice[]
```

### 4.3 Member
```
Tabela: members
- id: UUID (PK)
- user_id: UUID (FK → User)
- organization_id: UUID (FK → Organization)
- role: Enum (owner | admin | member)
- joined_at, invited_by
UniqueConstraint: (user_id, organization_id)
```

### 4.4 Subscription
```
Tabela: subscriptions
- id: UUID (PK)
- organization_id: UUID (FK → Organization)
- stripe_subscription_id: String (unique)
- stripe_price_id: String
- status: Enum (active | canceled | incomplete | past_due | trialing | unpaid)
- current_period_start, current_period_end: DateTime
- cancel_at_period_end: Boolean
- canceled_at: DateTime
```

### 4.5 Invoice
```
Tabela: invoices
- id: UUID (PK)
- organization_id: UUID (FK → Organization)
- invoice_number: String (unique)
- stripe_invoice_id, fakturownia_id: String (unique, nullable)
- status: Enum (draft | open | paid | void | uncollectible)
- amount: Numeric(10,2)
- currency: String (default: USD)
- pdf_url: Text
- due_date, paid_at: DateTime
```

### 4.6 AuditLog
```
Tabela: audit_logs
- id: UUID (PK)
- user_id: UUID (FK → User), user_email: String
- impersonated_by: UUID (nullable)
- organization_id: UUID (FK → Organization)
- action: String (indexed) — "create", "update", "delete", "login"
- resource_type: String (indexed), resource_id: String
- changes_before, changes_after: JSON
- summary: Text (auto-generated)
- ip_address, user_agent: String
- extra_data: JSON
- created_at: DateTime (indexed)
```

### 4.7 Notification
```
Tabela: notifications
- id: UUID (PK)
- user_id: UUID (FK → User, indexed)
- organization_id: UUID (FK → Organization, nullable)
- type: String (indexed) — "invitation", "role_change", "security_alert", "billing", "system", "impersonation"
- title: String(255), message: Text, link: String(500)
- is_read: Boolean (indexed), read_at: DateTime
- triggered_by: UUID (FK → User)
- created_at: DateTime
Indeksy: (user_id, is_read), (user_id, created_at)
```

### 4.8 NotificationPreference
```
Tabela: notification_preferences
- id: UUID (PK)
- user_id: UUID (FK → User)
- notification_type: String(50)
- channel_inapp: Boolean (default: True)
- channel_email: Boolean (default: True)
UniqueIndex: (user_id, notification_type)
```

### 4.9 RBAC — Permission, Role, RolePermission, UserRole
```
permissions: id, name (unique), category, description, is_system
roles: id, organization_id (nullable), name, description, is_system, is_default
role_permissions: id, role_id (FK), permission_id (FK)
user_roles: id, user_id (FK), role_id (FK), organization_id (FK), assigned_at, assigned_by
```

### 4.10 APIToken
```
Tabela: api_tokens
- id: UUID (PK)
- user_id: UUID (FK → User)
- token_hash: String (unique, indexed)
- name: String
- last_used_at, expires_at: DateTime
```

---

## 5. API Endpoints

### 5.1 Auth — `/api/v1/auth`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/register` | Rejestracja (email + haslo + nazwa) |
| POST | `/login` | Login → access_token + refresh_token |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Wylogowanie (blacklist token) |
| POST | `/magic-link` | Wyslij magic link na email |
| POST | `/verify-email` | Weryfikacja email tokenem |
| POST | `/resend-verification` | Ponowna wysylka weryfikacji |
| POST | `/password-reset` | Zadanie resetu hasla |
| POST | `/password-reset/confirm` | Potwierdzenie nowego hasla |
| POST | `/change-password` | Zmiana hasla (zalogowany) |

### 5.2 Users — `/api/v1/users`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/me` | Profil zalogowanego usera |
| PUT | `/me` | Aktualizacja profilu |
| GET | `/` | Lista userow (paginacja) |
| GET | `/{user_id}` | Szczegoly usera |
| DELETE | `/{user_id}` | Usun usera (admin) |

### 5.3 Organizations — `/api/v1/organizations`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/` | Utworz organizacje |
| GET | `/me` | Moja organizacja + statystyki |
| GET | `/{org_id}` | Szczegoly organizacji |
| PUT | `/{org_id}` | Aktualizuj organizacje |
| DELETE | `/{org_id}` | Usun organizacje (owner) |

### 5.4 Members — `/api/v1/organizations/{org_id}/members`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| POST | `/` | Zapros czlonka |
| GET | `/` | Lista czlonkow |
| PUT | `/{member_id}` | Zmien role |
| DELETE | `/{member_id}` | Usun czlonka |

### 5.5 Notifications — `/api/notifications`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `` | Lista powiadomien (paginacja, filtr unread) |
| GET | `/unread-count` | Liczba nieprzeczytanych (dla badge) |
| PATCH | `/{id}/read` | Oznacz jako przeczytane |
| POST | `/read-all` | Oznacz wszystkie jako przeczytane |
| DELETE | `/{id}` | Usun powiadomienie |
| GET | `/preferences` | Preferencje powiadomien |
| PUT | `/preferences` | Zmien preferencje |

### 5.6 RBAC — `/api/rbac`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/roles` | Lista rol w organizacji |
| POST | `/roles` | Utworz custom role |
| GET | `/permissions` | Lista uprawnien |
| POST | `/users/{id}/roles` | Przypisz role userowi |
| DELETE | `/users/{id}/roles/{role_id}` | Usun role |
| GET | `/users/{id}/permissions` | Uprawnienia usera |

### 5.7 Audit — `/api/audit`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/logs` | Lista audit logow (filtrowanie, paginacja) |
| GET | `/resource/{type}/{id}/history` | Historia zasobu |
| GET | `/users/{id}/activity` | Aktywnosc usera |
| GET | `/stats` | Statystyki audit |

### 5.8 Admin — `/api/admin`
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/stats` | Statystyki systemu |
| GET | `/organizations` | Lista organizacji (paginacja, szukanie) |
| GET | `/organizations/{id}` | Szczegoly org z czlonkami |
| GET | `/users` | Lista userow |
| POST | `/impersonate` | Impersonacja usera |
| POST | `/broadcast` | Broadcast wiadomosc |

### 5.9 WebSocket — `/ws`
| Typ | Sciezka | Opis |
|-----|---------|------|
| WS | `/ws/{org_id}?token=JWT` | WebSocket z organizacja |
| WS | `/ws?token=JWT` | WebSocket bez organizacji |
| GET | `/api/realtime/status` | Statystyki polaczen |
| GET | `/api/realtime/online-users` | Lista online userow |

### 5.10 Billing
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/api/v1/invoices` | Lista faktur |
| GET | `/api/v1/invoices/{id}` | Szczegoly faktury |
| GET | `/api/v1/invoices/{id}/pdf` | PDF faktury |
| GET | `/api/v1/subscription/status` | Status subskrypcji |

### 5.11 Health
| Metoda | Sciezka | Opis |
|--------|---------|------|
| GET | `/health` | Health check |
| GET | `/api/v1/ready` | Readiness (DB + Redis) |
| GET | `/api/v1/metrics` | Metryki (uptime, wersja) |

---

## 6. Kontrakty (fasthub_core/contracts.py)

Kontrakty to abstrakcyjne interfejsy — "obietnice" ktore FastHub gwarantuje kazdej aplikacji (AutoFlow, FastCRM itp.).

| Kontrakt | Metody | Implementacja |
|----------|--------|---------------|
| **AuthContract** | hash_password, verify_password, create_access_token, create_refresh_token, decode_token, blacklist_token, is_token_blacklisted | FastHubAuth — pelna |
| **UserContract** | get_current_user, get_user, list_organization_users, get_user_role | FastHubUser — pelna |
| **PermissionContract** | check_permission, get_user_permissions | FastHubPermission — RBAC |
| **BillingContract** | get_subscription, check_limit, record_usage | FastHubBilling — czesciowa (limity w v2.0) |
| **AuditContract** | log_action, get_audit_logs | FastHubAudit — pelna |
| **NotificationContract** | send_notification, send_email | FastHubNotification — pelna |
| **DatabaseContract** | get_db_session, get_engine | FastHubDatabase — pelna |

---

## 7. Kluczowe serwisy

### 7.1 AuthService (fasthub-backend)
- Rejestracja: tworzenie usera + organizacji + czlonkostwa (owner)
- Login: weryfikacja hasla → JWT (access 30min + refresh 7 dni)
- Token blacklist: Redis (produkcja) lub InMemory (dev)
- Email verification: 24h token
- Password reset: 1h token
- Magic link: jednorazowy link do logowania

### 7.2 RBACService (fasthub_core)
- Sprawdzanie uprawnien: check_permission(user_id, org_id, permission) → bool
- 3 systemowe role: Owner (*), Admin (14 uprawnien), Member (3 uprawnienia)
- 12 core permissions w 4 kategoriach: team, billing, settings, audit
- Custom role per organizacja
- Super Admin omija sprawdzanie

### 7.3 NotificationService (fasthub_core)
- 3 kanaly: in-app (DB), email (SMTP/Console), WebSocket (przyszlosc)
- 8 typow: invitation, role_change, security_alert, billing, system, impersonation, approval_request, approval_result
- FORCED_TYPES: security_alert, impersonation — nie mozna wylaczyc
- Preferencje per user per typ

### 7.4 AuditService (fasthub_core)
- Logowanie: kto, co, kiedy, skad, co sie zmienilo (before/after)
- Auto-summary: "Zmieniono plan: pro → enterprise"
- Filtrowanie pol wrazliwych (password, token, secret)
- Retention: cleanup logow starszych niz 90 dni

### 7.5 ConnectionManager (fasthub_core)
- In-memory WebSocket management
- Struktura: org_id → user_id → Set[WebSocket]
- send_to_user, broadcast_to_organization, broadcast_all
- Automatyczny cleanup martwych polaczen
- Singleton: get_connection_manager()

---

## 8. Middleware

Kolejnosc middleware (od zewnatrz do wewnatrz):
1. **CORS** — obsluga preflight OPTIONS
2. **TrustedHost** — blokada host header attacks (prod)
3. **RequestLoggingMiddleware** — logowanie requestow (metoda, sciezka, czas, IP)
4. **GZipMiddleware** — kompresja (min 1000 bytes)
5. **SecurityHeadersMiddleware** — X-Content-Type-Options, X-Frame-Options, XSS, CSP, Referrer, Permissions
6. **RequestIDMiddleware** — UUID per request → X-Request-ID header

### Rate Limiting
```
AUTH_LOGIN:          5/minute
AUTH_REGISTER:       3/hour
AUTH_PASSWORD_RESET: 3/hour
API_TOKEN_CREATE:    10/hour
PROTECTED_READ:      200/minute
PROTECTED_WRITE:     60/minute
ADMIN:               100/minute
```

---

## 9. Autentykacja — flow

```
1. POST /register
   → Utworz User + Organization + Member (owner)
   → Wyslij email weryfikacyjny
   → Zwroc access_token + refresh_token

2. POST /login
   → Zweryfikuj email + haslo
   → Sprawdz is_active
   → Zwroc access_token (30min) + refresh_token (7dni)

3. Request z tokenem
   → Authorization: Bearer {access_token}
   → decode_access_token() → user_id
   → Sprawdz blacklist
   → Pobierz User z bazy
   → Zwroc dane

4. POST /refresh
   → Dekoduj refresh_token → user_id
   → Wydaj nowy access_token

5. POST /logout
   → Dodaj token do blacklist (Redis TTL = czas wygasniecia)
```

---

## 10. RBAC — flow sprawdzania uprawnien

```
1. Request przychodzi z X-Organization-Id header
2. require_permission("team.invite_member") dependency
3. Pobierz user_id z JWT
4. Super Admin? → TAK → przepusc
5. RBACService.check_permission(user_id, org_id, "team.invite_member")
6. SELECT permissions
   FROM user_roles
   JOIN role_permissions ON role_permissions.role_id = user_roles.role_id
   JOIN permissions ON permissions.id = role_permissions.permission_id
   WHERE user_roles.user_id = ? AND user_roles.organization_id = ?
7. "team.invite_member" in permissions? → TAK/NIE
8. NIE → 403 Forbidden
```

---

## 11. Frontend — routing i strony

### Publiczne
```
/login              → LoginPage
/register           → RegisterPage
/forgot-password    → ForgotPasswordPage
/reset-password     → ResetPasswordPage
```

### Chronione (wymaga logowania)
```
/dashboard          → DashboardPage (statystyki, wykresy)
/team               → TeamPage (czlonkowie, zaproszenia, role)
/billing            → BillingPage (faktury, subskrypcje)
/settings           → SettingsPage (profil + organizacja)
/onboarding         → OnboardingPage (setup nowej org)
```

### Super Admin
```
/superadmin/organizations  → Zarzadzanie organizacjami
/superadmin/metrics        → Metryki systemowe
```

### State Management (Zustand)
- **authStore**: user, isAuthenticated, login(), logout(), fetchCurrentUser()
- **orgStore**: organization, fetchOrganization(), updateOrganization()

### API Client (Axios)
- Base URL: `VITE_API_URL` lub `http://localhost:8000/api/v1`
- Auto Bearer token w kazdym uquesi
- Auto refresh na 401
- Kolejkowanie requestow podczas refresh

---

## 12. Konfiguracja (zmienne srodowiskowe)

```env
# Aplikacja
APP_NAME=FastHub
DEBUG=false
ENVIRONMENT=production

# Baza danych
DATABASE_URL=postgresql://user:pass@host:5432/fasthub

# Bezpieczenstwo
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (SMTP — opcjonalne, bez tego dziala console mode)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=user@gmail.com
SMTP_PASSWORD=app-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=noreply@fasthub.app

# SendGrid (alternatywa)
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@fasthub.app

# Stripe
STRIPE_SECRET_KEY=sk_xxx
STRIPE_PUBLISHABLE_KEY=pk_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Sentry
SENTRY_DSN=https://xxx@sentry.io/yyy

# Frontend
FRONTEND_URL=https://app.fasthub.pl
VITE_API_URL=https://api.fasthub.pl/api/v1
```

---

## 13. Testy

### fasthub_core (tests/)
| Plik | Ilosc | Zakres |
|------|-------|--------|
| test_contracts.py | 17 | Kontrakty API |
| test_admin.py | ~10 | Super Admin |
| test_rbac.py | ~10 | Role i uprawnienia |
| test_audit_trail.py | ~10 | Audit logs |
| test_auth_improvements.py | ~10 | Auth (blacklist, validation, email) |
| test_notifications.py | 20 | Powiadomienia |
| test_realtime_security.py | 22 | WebSocket, middleware |

### fasthub-backend (tests/)
| Folder | Testy |
|--------|-------|
| unit/ | auth_service, org_service, admin_service, api_token, audit, cache, config |
| integration/ | auth_api, users_api, organizations_api, members_api, admin_api, edge_cases |

**Uruchamianie:**
```bash
# fasthub_core
python -m pytest tests/ -v

# fasthub-backend
cd fasthub-backend && python -m pytest tests/ -v
```

---

## 14. Uwagi techniczne

- **bcrypt 5.0 NIE dziala z passlib 1.7.4** — uzywac `bcrypt==4.1.2`
- **WebSocket auth** przez query string `?token=JWT` (nie mozna ustawic Authorization header w WS)
- **ConnectionManager jest in-memory** — dziala na jednym serwerze. Multi-server wymaga Redis pub/sub (v2.1+)
- **HSTS domyslnie wylaczony** — wlaczyc dopiero gdy SSL skonfigurowany
- **Migracje** uruchamiaja sie automatycznie na starcie aplikacji (alembic upgrade head)
- **fasthub_core nie jest importowany przez fasthub-backend** — to oddzielny pakiet do reuse
