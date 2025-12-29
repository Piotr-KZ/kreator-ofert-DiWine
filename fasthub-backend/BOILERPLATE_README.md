# 🚀 AutoFlow FastAPI SaaS Boilerplate

**Production-ready FastAPI boilerplate for building SaaS applications with authentication, multi-tenancy, and Stripe integration.**

---

## ✨ Features

### 🔐 Authentication & Authorization
- ✅ JWT-based authentication (access + refresh tokens)
- ✅ Password hashing with bcrypt
- ✅ Email verification flow (optional)
- ✅ Password reset flow
- ✅ Role-based access control (RBAC): admin, user, viewer

### 🏢 Multi-Tenancy
- ✅ Organization-based multi-tenancy
- ✅ User-organization relationships
- ✅ Organization ownership & transfer
- ✅ Team member management

### 👥 User Management
- ✅ User CRUD operations
- ✅ User profile management
- ✅ Role management
- ✅ User activation/deactivation

### 💳 Payments (Stripe Integration)
- ✅ Subscription management
- ✅ Multiple subscription plans
- ✅ Stripe webhooks
- ✅ Invoice generation

### 🛠️ Technical Stack
- **Framework:** FastAPI 0.109+
- **Database:** MySQL/TiDB (async with aiomysql)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Authentication:** python-jose, passlib, bcrypt
- **Payments:** Stripe

---

## 📁 Project Structure

```
autoflow-backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/          # API endpoints
│   │   │   ├── auth.py         # Authentication routes
│   │   │   ├── users.py        # User management routes
│   │   │   └── organizations.py # Organization routes
│   │   └── api.py              # API router aggregator
│   ├── core/
│   │   ├── config.py           # Configuration (Pydantic Settings)
│   │   ├── security.py         # JWT & password utilities
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── db/
│   │   └── session.py          # Database session management
│   ├── models/                 # SQLAlchemy models
│   │   ├── base.py            # Base model with timestamps
│   │   ├── user.py            # User model
│   │   ├── organization.py    # Organization model
│   │   ├── subscription.py    # Subscription model
│   │   └── invoice.py         # Invoice model
│   ├── schemas/               # Pydantic schemas (DTOs)
│   │   ├── auth.py           # Auth DTOs
│   │   ├── user.py           # User DTOs
│   │   └── organization.py   # Organization DTOs
│   ├── services/             # Business logic layer
│   │   ├── auth_service.py           # Auth business logic
│   │   ├── user_service.py           # User management logic
│   │   ├── organization_service.py   # Organization logic
│   │   ├── user_repository.py        # User data access
│   │   └── organization_repository.py # Org data access
│   └── main.py               # FastAPI application entry point
├── alembic/                  # Database migrations
│   ├── versions/            # Migration files
│   └── env.py              # Alembic configuration
├── docs/                    # Documentation
├── tests/                   # Test files
├── .env                     # Environment variables (DO NOT COMMIT)
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
└── README.md              # This file
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
# Clone repository
git clone <your-repo-url>
cd autoflow-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required environment variables:**
```env
# Database
DATABASE_URL=mysql://user:password@host:port/database?ssl=true

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe (optional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (optional)
SENDGRID_API_KEY=SG...
FROM_EMAIL=noreply@yourdomain.com
```

### 3. Setup Database

```bash
# Run migrations
alembic upgrade head
```

### 4. Run Development Server

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:**
- API: http://localhost:8000
- Docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📚 API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "organization_name": "Acme Inc"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### User Management Endpoints

#### List Users (in organization)
```http
GET /api/v1/users/?skip=0&limit=100
Authorization: Bearer {access_token}
```

#### Get User
```http
GET /api/v1/users/{user_id}
Authorization: Bearer {access_token}
```

#### Update User
```http
PATCH /api/v1/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "role": "admin"
}
```

#### Delete User (admin only)
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer {access_token}
```

### Organization Endpoints

#### Get Current Organization
```http
GET /api/v1/organizations/me
Authorization: Bearer {access_token}
```

#### Update Organization (owner only)
```http
PATCH /api/v1/organizations/{org_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New Company Name",
  "slug": "new-company-slug"
}
```

#### Transfer Ownership (owner only)
```http
POST /api/v1/organizations/{org_id}/transfer-ownership
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "new_owner_id": 123
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

---

## 🔧 Configuration

### Email Verification

By default, email verification is **disabled** for easier development. To enable:

1. Set `is_verified=False` in `app/services/auth_service.py` (line 69)
2. Configure SendGrid API key in `.env`
3. Implement email sending in `app/services/email_service.py`

### Stripe Integration

1. Get API keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Add keys to `.env`
3. Configure webhook endpoint: `https://yourdomain.com/api/v1/webhooks/stripe`
4. Test with Stripe CLI: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe`

---

## 🚢 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables (Production)

```env
DATABASE_URL=mysql://user:password@prod-host:port/database?ssl=true
JWT_SECRET_KEY=<generate-strong-secret>
ENVIRONMENT=production
DEBUG=false
```

### Run Migrations

```bash
alembic upgrade head
```

### Start Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📝 Development Guidelines

### Adding New Endpoints

1. Create schema in `app/schemas/`
2. Create model in `app/models/` (if needed)
3. Create repository in `app/services/`
4. Create service in `app/services/`
5. Create endpoint in `app/api/v1/endpoints/`
6. Register router in `app/api/v1/api.py`
7. Run migration: `alembic revision --autogenerate -m "description"`
8. Apply migration: `alembic upgrade head`

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Use async/await for database operations

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - feel free to use this boilerplate for your projects!

---

## 🙏 Credits

Built with ❤️ using FastAPI, SQLAlchemy, and modern Python best practices.

**Key Technologies:**
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Stripe](https://stripe.com/)

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Create Issue](https://github.com/your-repo/issues)
- Documentation: [Read Docs](https://docs.yourdomain.com)
- Email: support@yourdomain.com
