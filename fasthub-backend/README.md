# AutoFlow - Universal SaaS Boilerplate

**FastAPI + PostgreSQL + Stripe + Multi-Tenant Architecture**

## 🎯 Overview

AutoFlow is a production-ready SaaS boilerplate built with FastAPI and PostgreSQL, featuring:

### Core Features
- **Multi-tenant architecture** with organization-based data isolation
- **Authentication & Authorization** with JWT tokens and role-based access control
- **Stripe integration** for subscriptions and billing
- **Invoice management** with PDF generation
- **Email service** with 5 types of emails (verification, password reset, magic link, invoice, payment failed)
- **API Tokens** for long-lived API access

### Production-Ready Features
- **Rate Limiting** - Protection against abuse and DDoS attacks
- **Monitoring** - Sentry integration with health checks
- **Subscription Checks** - Automatic revenue protection with grace periods
- **Token Blacklist** - Secure logout and token revocation
- **API Documentation** - Comprehensive Swagger UI + ReDoc

## 🏗️ Architecture

```
app/
├── api/v1/endpoints/     # API endpoints (controllers)
├── core/                 # Core configuration and security
├── db/                   # Database session management
├── models/               # SQLAlchemy models (entities)
├── schemas/              # Pydantic schemas (DTOs)
├── services/             # Business logic services
├── use_cases/            # Use cases (application layer)
└── main.py               # FastAPI application entry point

alembic/                  # Database migrations
tests/                    # Test suite
```

### Architecture Layers

1. **API Layer** (`api/v1/endpoints/`) - HTTP endpoints, request/response handling
2. **Use Cases Layer** (`use_cases/`) - Application logic, orchestration
3. **Services Layer** (`services/`) - Business logic, domain rules
4. **Models Layer** (`models/`) - Database entities, ORM models
5. **Schemas Layer** (`schemas/`) - Data validation, DTOs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (for Celery)

### Installation

1. **Clone and setup**
```bash
cd autoflow-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Setup database**
```bash
# Create PostgreSQL database
createdb autoflow

# Run migrations
alembic upgrade head
```

4. **Run development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access API documentation**
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 📦 Modules

### 1. Auth Module
- User registration and login
- JWT token management (access + refresh tokens)
- Password reset flow
- Email verification
- Multi-factor authentication (planned)

### 2. Users Module
- User profile management
- Role-based access control (Admin, User, Viewer)
- Organization membership
- User preferences

### 3. Subscriptions Module
- Stripe integration
- Subscription plans management
- Billing portal
- Webhook handling
- Usage tracking

### 4. Invoices Module
- Invoice generation
- PDF export
- Fakturownia integration
- Payment tracking
- Email delivery

### 5. Organizations Module
- Multi-tenant support
- Organization settings
- Member management
- Data isolation

## 🔐 Security

- **Password hashing** with bcrypt
- **JWT tokens** with expiration
- **CORS** configuration
- **SQL injection** protection (SQLAlchemy ORM)
- **Input validation** with Pydantic
- **Row-level security** with PostgreSQL policies

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_auth_api.py -v
```

### Test Results

```
✅ Unit Tests: 10/10 (100%)
✅ Auth API Tests: 14/14 (100%)
✅ Users API Tests: 7/7 (100%)
✅ Admin API Tests: 6/6 (100%)
⚠️ Subscriptions API Tests: 3/7 (43% - Stripe mocking needed)

TOTAL: 40/44 passing (91%)
```

## 📝 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history
```

## 🔧 Development

### Code Style

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Project Structure Guidelines

- **Models** - Database entities only, no business logic
- **Schemas** - Pydantic models for validation and serialization
- **Services** - Business logic, reusable across use cases
- **Use Cases** - Application logic, orchestrate services
- **Endpoints** - HTTP layer, minimal logic

## 🌐 External Integrations

### Stripe
- Subscription management
- Payment processing
- Webhook handling

### Fakturownia
- Invoice generation
- Polish tax compliance

### Google APIs
- Gmail integration
- Google Drive storage
- Google Sheets export

### SendGrid
- Transactional emails
- Email templates

### Outlook IMAP
- Email reading
- Invoice parsing

## 📊 Multi-Tenancy

AutoFlow uses **organization-based multi-tenancy**:

- Each user belongs to one organization
- Data is isolated by `organization_id`
- Queries automatically filter by organization
- Row-level security in PostgreSQL

## 🚀 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` in environment
- [ ] Configure production database (PostgreSQL/MySQL)
- [ ] Setup Redis for rate limiting and token blacklist
- [ ] Configure CORS origins
- [ ] Setup SSL/TLS certificates
- [ ] Configure Stripe webhooks
- [ ] Configure SendGrid API key
- [ ] Configure Sentry DSN for error tracking
- [ ] Setup monitoring and alerts
- [ ] Configure backups
- [ ] Setup CI/CD pipeline
- [ ] Test health checks (`/api/v1/health`, `/api/v1/ready`)
- [ ] Verify rate limiting is working
- [ ] Test subscription checks
- [ ] Test token blacklist (logout)

### Docker Deployment

```bash
# Build image
docker build -t autoflow-backend .

# Run container
docker run -p 8000:8000 --env-file .env autoflow-backend
```

## 📚 API Documentation

Full API documentation is available at:
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### Additional Documentation
- **[PRODUCTION_READY.md](PRODUCTION_READY.md)** - Complete production features documentation
- **[TOKEN_BLACKLIST.md](TOKEN_BLACKLIST.md)** - Token blacklist implementation details
- **[EMAIL_SETUP.md](EMAIL_SETUP.md)** - Email configuration guide
- **[TODO.md](TODO.md)** - Feature status and roadmap

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'

# Use token
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Credits

Based on the architecture from Akademia SaaS boilerplate (Firebase/TypeScript), migrated to FastAPI/PostgreSQL.

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using FastAPI, PostgreSQL, and modern Python practices**
