# FastHub - Complete System Documentation

**Last Updated:** 2026-01-02  
**Version:** 1.0  
**Status:** Production-Ready on Render.com

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Features & Modules](#features--modules)
4. [API Endpoints](#api-endpoints)
5. [Database Schema](#database-schema)
6. [Authentication & Authorization](#authentication--authorization)
7. [Deployment](#deployment)
8. [Testing](#testing)
9. [Known Issues & Limitations](#known-issues--limitations)

---

## 1. System Overview

**FastHub** is a production-ready SaaS boilerplate for multi-tenant applications with:
- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** React 18 + Ant Design
- **Database:** PostgreSQL (TiDB Cloud)
- **Deployment:** Render.com
- **Authentication:** JWT-based with email/password

### Live URLs
- **Frontend:** https://fasthub-lz4x.onrender.com
- **Backend API:** https://fasthub-backend.onrender.com
- **API Docs:** https://fasthub-backend.onrender.com/docs

---

## 2. Architecture

### Tech Stack

**Backend:**
- FastAPI 0.115.6
- SQLAlchemy 2.0 (async ORM)
- Pydantic V2 (validation)
- Alembic (migrations)
- PostgreSQL 15+
- JWT authentication

**Frontend:**
- React 18
- Ant Design 5.x
- Axios (HTTP client)
- React Router
- Zustand (state management)

### Project Structure

```
fasthub-repo/
├── fasthub-backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # API routes
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── users.py          # User management
│   │   │   ├── organizations.py  # Organization CRUD
│   │   │   ├── members.py        # Team management
│   │   │   └── subscriptions.py  # Billing (mock)
│   │   ├── core/
│   │   │   ├── config.py         # Settings
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   └── dependencies.py   # Dependency injection
│   │   ├── db/
│   │   │   ├── base.py           # SQLAlchemy base
│   │   │   └── session.py        # Database session
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── member.py
│   │   │   ├── subscription.py
│   │   │   └── audit_log.py
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── main.py               # FastAPI app
│   ├── alembic/                  # Database migrations
│   ├── tests/                    # Automated tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── fasthub-frontend/
│   ├── src/
│   │   ├── pages/                # Page components
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── TeamPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── UsersPage.tsx (SuperAdmin only)
│   │   ├── components/           # Reusable components
│   │   │   ├── AppLayout.tsx     # Main layout
│   │   │   ├── OnboardingModal.tsx
│   │   │   └── PasswordRequirements.tsx
│   │   ├── store/                # Zustand stores
│   │   │   ├── authStore.ts
│   │   │   └── orgStore.ts
│   │   ├── api/                  # API client
│   │   │   ├── client.ts         # Axios instance
│   │   │   ├── auth.ts
│   │   │   ├── organizations.ts
│   │   │   └── users.ts
│   │   └── App.tsx               # Root component
│   ├── Dockerfile
│   └── package.json
│
├── render.yaml                   # Render deployment config
└── docker-compose.yml            # Local development
```

---

## 3. Features & Modules

### 3.1 Authentication & Authorization

**Features:**
- ✅ Email/password registration
- ✅ Login with JWT tokens (access + refresh)
- ✅ Password change
- ✅ Logout
- ✅ Role-based access control (SuperAdmin, Admin, Viewer)

**Roles:**
- **SuperAdmin:** Full system access, can view all users/organizations
- **Admin:** Organization owner, can manage team and settings
- **Viewer:** Read-only access to organization data

**Implementation:**
- Backend: `app/api/v1/endpoints/auth.py`
- Frontend: `src/pages/LoginPage.tsx`, `src/pages/RegisterPage.tsx`
- Store: `src/store/authStore.ts`

### 3.2 User Management

**Features:**
- ✅ User CRUD (SuperAdmin only)
- ✅ Profile viewing
- ✅ User search and filtering
- ✅ Delete protection (cannot delete self)
- ✅ Audit logging for SuperAdmin actions

**Implementation:**
- Backend: `app/api/v1/endpoints/users.py`
- Frontend: `src/pages/UsersPage.tsx` (SuperAdmin only)
- Model: `app/models/user.py`

### 3.3 Organization Management

**Features:**
- ✅ Organization CRUD
- ✅ Multi-organization support per user
- ✅ Organization onboarding modal (first login)
- ✅ Settings page with validation
- ✅ Billing address management
- ✅ Organization deletion (with confirmation)

**Validation Rules:**
- **NIP (Tax ID):** 10 digits only
- **Postal Code:** XX-XXX format (e.g., 30-001)
- **Phone:** International format with optional +
- **Country:** Dropdown selector (18 countries)

**Implementation:**
- Backend: `app/api/v1/endpoints/organizations.py`
- Frontend: `src/pages/SettingsPage.tsx`, `src/components/OnboardingModal.tsx`
- Model: `app/models/organization.py`

### 3.4 Team Management (Members)

**Features:**
- ✅ View team members
- ✅ Invite new members (existing users only)
- ✅ Change member roles (Admin/Viewer)
- ✅ Remove members
- ✅ Owner visibility (virtual member injection)
- ✅ Role badges (Owner, Admin, Viewer)

**Implementation:**
- Backend: `app/api/v1/endpoints/members.py`
- Frontend: `src/pages/TeamPage.tsx`
- Model: `app/models/member.py`

### 3.5 Billing & Subscriptions (Mock)

**Features:**
- ✅ View subscription plans (Free, Pro, Enterprise)
- ✅ Mock plan changes (no Stripe integration)
- ✅ Billing page UI
- ⚠️ **Note:** Stripe integration not active (mock only)

**Implementation:**
- Backend: `app/api/v1/endpoints/subscriptions.py`
- Frontend: `src/pages/BillingPage.tsx`
- Model: `app/models/subscription.py`

### 3.6 Dashboard & Analytics

**Features:**
- ✅ Organization statistics (members, users)
- ✅ Empty state for orphan users (no organization)
- ✅ "Create Organization" CTA
- ✅ Multi-organization support

**Implementation:**
- Frontend: `src/pages/DashboardPage.tsx`

### 3.7 Audit Logging

**Features:**
- ✅ Log SuperAdmin actions (create, update, delete users)
- ✅ Store actor, action, target, metadata
- ✅ Timestamp tracking

**Implementation:**
- Model: `app/models/audit_log.py`
- Service: `app/services/audit_service.py`

---

## 4. API Endpoints

### 4.1 Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login with email/password | No |
| POST | `/refresh` | Refresh access token | Yes (refresh token) |
| POST | `/logout` | Logout (invalidate tokens) | Yes |
| GET | `/me` | Get current user | Yes |
| POST | `/change-password` | Change password | Yes |

### 4.2 Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/` | List all users | Yes | SuperAdmin |
| GET | `/{user_id}` | Get user by ID | Yes | SuperAdmin |
| DELETE | `/{user_id}` | Delete user | Yes | SuperAdmin |

### 4.3 Organizations (`/api/v1/organizations`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/me` | Get current user's organizations | Yes |
| POST | `/` | Create organization | Yes |
| GET | `/{org_id}` | Get organization by ID | Yes |
| PATCH | `/{org_id}` | Update organization | Yes (Admin) |
| DELETE | `/{org_id}` | Delete organization | Yes (Admin) |
| POST | `/{org_id}/complete` | Complete onboarding | Yes |

### 4.4 Members (`/api/v1/organizations/{org_id}/members`)

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/` | List members | Yes | All |
| POST | `/` | Invite member | Yes | Admin |
| PATCH | `/{member_id}` | Update member role | Yes | Admin |
| DELETE | `/{member_id}` | Remove member | Yes | Admin |

### 4.5 Subscriptions (`/api/v1/subscriptions`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/plans` | List available plans | Yes |
| POST | `/subscribe` | Subscribe to plan (mock) | Yes |
| POST | `/cancel` | Cancel subscription (mock) | Yes |

---

## 5. Database Schema

### 5.1 Tables

**users**
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE)
- `full_name` (VARCHAR)
- `hashed_password` (VARCHAR)
- `is_active` (BOOLEAN)
- `is_verified` (BOOLEAN)
- `is_superuser` (BOOLEAN)
- `role` (ENUM: admin, user)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**organizations**
- `id` (UUID, PK)
- `name` (VARCHAR)
- `email` (VARCHAR)
- `phone` (VARCHAR, nullable)
- `nip` (VARCHAR, nullable)
- `billing_street` (VARCHAR)
- `billing_city` (VARCHAR)
- `billing_postal_code` (VARCHAR)
- `billing_country` (VARCHAR)
- `owner_id` (UUID, FK → users.id)
- `onboarding_completed` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**members**
- `id` (UUID, PK)
- `organization_id` (UUID, FK → organizations.id)
- `user_id` (UUID, FK → users.id)
- `role` (ENUM: ADMIN, VIEWER)
- `joined_at` (TIMESTAMP)

**subscriptions** (mock)
- `id` (UUID, PK)
- `organization_id` (UUID, FK → organizations.id)
- `plan` (VARCHAR: free, pro, enterprise)
- `status` (VARCHAR: active, canceled)
- `created_at` (TIMESTAMP)

**audit_logs**
- `id` (UUID, PK)
- `actor_id` (UUID, FK → users.id)
- `action` (VARCHAR: create_user, delete_user, etc.)
- `target_type` (VARCHAR: user, organization)
- `target_id` (UUID)
- `metadata` (JSONB)
- `created_at` (TIMESTAMP)

### 5.2 Relationships

- `users.id` ← `organizations.owner_id` (one-to-many)
- `users.id` ← `members.user_id` (many-to-many via members)
- `organizations.id` ← `members.organization_id` (many-to-many via members)
- `organizations.id` ← `subscriptions.organization_id` (one-to-one)

---

## 6. Authentication & Authorization

### 6.1 JWT Tokens

**Access Token:**
- Expiration: 30 minutes
- Payload: `sub` (user_id), `org` (organization_id), `exp`, `iat`, `type`

**Refresh Token:**
- Expiration: 7 days
- Payload: `sub` (user_id), `exp`, `iat`, `type`

### 6.2 Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character

### 6.3 Role-Based Access Control

**SuperAdmin:**
- View all users (`/api/v1/users`)
- Delete any user (except self)
- Access Users page in frontend

**Admin (Organization Owner):**
- Manage organization settings
- Invite/remove members
- Change member roles
- Delete organization

**Viewer:**
- Read-only access to organization data
- Cannot modify settings or members

---

## 7. Deployment

### 7.1 Render.com Setup

**Services:**
1. **fasthub-backend** (Web Service)
   - Build: `cd fasthub-backend && pip install -r requirements.txt`
   - Start: `cd fasthub-backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - URL: https://fasthub-backend.onrender.com

2. **fasthub-lz4x** (Static Site)
   - Build: `cd fasthub-frontend && npm install && npm run build`
   - Publish: `fasthub-frontend/dist`
   - URL: https://fasthub-lz4x.onrender.com

**Environment Variables (Backend):**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing secret
- `BACKEND_CORS_ORIGINS` - Allowed origins (JSON array)
- `ENVIRONMENT` - production
- `DEBUG` - false

**Environment Variables (Frontend):**
- `VITE_API_URL` - Backend API URL

### 7.2 Database (TiDB Cloud)

- **Provider:** TiDB Cloud (MySQL-compatible)
- **Connection:** PostgreSQL driver (psycopg2)
- **Migrations:** Alembic

### 7.3 Deployment Workflow

1. Push to GitHub `main` branch
2. Render auto-detects changes
3. Backend builds (~2-3 minutes)
4. Frontend builds (~2-3 minutes)
5. Services restart automatically

---

## 8. Testing

### 8.1 Test Coverage

- **Total Tests:** 44
- **Passing:** 40 (91%)
- **Failing:** 4 (Stripe mocking required)
- **Coverage:** 46%

### 8.2 Test Categories

**Unit Tests:** (10/10 passing)
- Password hashing
- JWT token generation
- Validation logic

**Auth API Tests:** (14/14 passing)
- Registration
- Login
- Token refresh
- Password change

**Users API Tests:** (7/7 passing)
- List users (SuperAdmin)
- Get user by ID
- Delete user
- Delete protection

**Members API Tests:** (6/6 passing)
- List members
- Invite member
- Update role
- Remove member

**Subscriptions API Tests:** (3/7 passing)
- ⚠️ 4 tests require Stripe mocking

### 8.3 Running Tests

```bash
# With Docker
docker-compose exec backend pytest

# Coverage report
docker-compose exec backend pytest --cov=app --cov-report=html
```

---

## 9. Known Issues & Limitations

### 9.1 Current Limitations

1. **Stripe Integration:** Mock only (no real payments)
2. **Email Service:** Not implemented (no verification emails)
3. **Invite System:** Can only invite existing users (no email invites)
4. **Rate Limiting:** Not implemented
5. **File Uploads:** Not supported
6. **2FA:** Not implemented

### 9.2 Known Bugs

1. **Invite Member Dropdown:** User dropdown empty (frontend validation issue)
2. **Settings Form:** Validation and read-only view implemented (latest commit)

### 9.3 Security Considerations

**Implemented:**
- ✅ Password hashing (bcrypt)
- ✅ JWT token expiration
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ Input validation (Pydantic)
- ✅ Delete protection (cannot delete self)

**Missing:**
- ⚠️ Rate limiting
- ⚠️ Token blacklist (logout doesn't invalidate tokens)
- ⚠️ HTTPS enforcement (Render handles this)
- ⚠️ Email verification
- ⚠️ Password reset via email

---

## 10. Demo Data

**SuperAdmin:**
- Email: `piotr.k@training-effect.pl`
- Password: `DemoPass123`

**Test Users:** (32 users total)
- Jack Anderson (orphan user): `jack.anderson@dataflow.systems` / `DemoPass123`
- Frank Miller (empty org): `frank.miller@cloudstart.io` / `DemoPass123`
- Bob Smith (owner): `bob.smith@techcorp.com` / `DemoPass123`

**Organizations:** 10 demo organizations with members

---

## 11. Future Roadmap

### Phase 1: Core Improvements
- [ ] Implement real Stripe integration
- [ ] Add email service (SendGrid/AWS SES)
- [ ] Fix invite member dropdown
- [ ] Add rate limiting

### Phase 2: Features
- [ ] File upload support
- [ ] 2FA authentication
- [ ] Email invites for new users
- [ ] Password reset via email

### Phase 3: Scale
- [ ] Redis caching
- [ ] Background job queue (Celery)
- [ ] Monitoring (Sentry, DataDog)
- [ ] CI/CD pipeline (GitHub Actions)

---

**End of Documentation**
