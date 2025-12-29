# AutoFlow Backend - Project Structure

## 📁 Directory Structure

```
autoflow-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/          # API endpoints (controllers)
│   │       │   ├── auth.py         # Authentication endpoints
│   │       │   ├── users.py        # User management endpoints
│   │       │   ├── subscriptions.py # Subscription endpoints
│   │       │   └── invoices.py     # Invoice endpoints
│   │       └── api.py              # API router aggregator
│   │
│   ├── core/
│   │   ├── config.py               # Application configuration
│   │   └── security.py             # Security utilities (JWT, hashing)
│   │
│   ├── db/
│   │   └── session.py              # Database session management
│   │
│   ├── models/                     # SQLAlchemy models (entities)
│   │   ├── base.py                 # Base model with common fields
│   │   ├── user.py                 # User model
│   │   ├── organization.py         # Organization model
│   │   ├── subscription.py         # Subscription model
│   │   └── invoice.py              # Invoice model
│   │
│   ├── schemas/                    # Pydantic schemas (DTOs)
│   │   ├── auth.py                 # Auth request/response schemas
│   │   ├── user.py                 # User schemas
│   │   ├── subscription.py         # Subscription schemas
│   │   └── invoice.py              # Invoice schemas
│   │
│   ├── services/                   # Business logic services
│   │   ├── auth_service.py         # Authentication service
│   │   ├── user_service.py         # User service
│   │   ├── stripe_service.py       # Stripe integration
│   │   ├── email_service.py        # Email sending
│   │   └── pdf_service.py          # PDF generation
│   │
│   ├── use_cases/                  # Use cases (application layer)
│   │   ├── auth/
│   │   │   ├── register.py         # Register use case
│   │   │   ├── login.py            # Login use case
│   │   │   └── reset_password.py   # Password reset use case
│   │   ├── users/
│   │   │   ├── get_profile.py      # Get user profile
│   │   │   └── update_profile.py   # Update user profile
│   │   ├── subscriptions/
│   │   │   ├── create_subscription.py
│   │   │   └── cancel_subscription.py
│   │   └── invoices/
│   │       ├── generate_invoice.py
│   │       └── send_invoice.py
│   │
│   └── main.py                     # FastAPI application entry point
│
├── alembic/                        # Database migrations
│   ├── versions/                   # Migration files
│   ├── env.py                      # Alembic environment
│   └── script.py.mako              # Migration template
│
├── tests/                          # Test suite
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_subscriptions.py
│   └── test_invoices.py
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── alembic.ini                     # Alembic configuration
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── STRUCTURE.md                    # This file
└── TODO.md                         # Implementation checklist
```

## 🏗️ Architecture Layers

### 1. API Layer (`app/api/v1/endpoints/`)
**Responsibility:** HTTP request/response handling, input validation, authentication

**Example:**
```python
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    use_case = RegisterUseCase(db)
    user = await use_case.execute(user_data)
    return user
```

### 2. Use Cases Layer (`app/use_cases/`)
**Responsibility:** Application logic, orchestration, business workflows

**Example:**
```python
class RegisterUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
        self.email_service = EmailService()
    
    async def execute(self, user_data: UserCreate) -> User:
        # 1. Validate user doesn't exist
        # 2. Create user
        # 3. Send verification email
        # 4. Return user
```

### 3. Services Layer (`app/services/`)
**Responsibility:** Business logic, domain rules, external integrations

**Example:**
```python
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        # Hash password
        # Create user in database
        # Return user
```

### 4. Models Layer (`app/models/`)
**Responsibility:** Database entities, ORM models

**Example:**
```python
class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(320), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
```

### 5. Schemas Layer (`app/schemas/`)
**Responsibility:** Data validation, serialization, DTOs

**Example:**
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime
```

## 🔄 Request Flow

```
HTTP Request
    ↓
API Endpoint (endpoints/auth.py)
    ↓
Use Case (use_cases/auth/register.py)
    ↓
Service (services/user_service.py)
    ↓
Model (models/user.py)
    ↓
Database (PostgreSQL)
    ↓
Response (schemas/user.py)
    ↓
HTTP Response
```

## 📦 Module Dependencies

```
API Layer
    ↓ depends on
Use Cases Layer
    ↓ depends on
Services Layer
    ↓ depends on
Models Layer + Schemas Layer
```

**Rules:**
- API can only call Use Cases
- Use Cases can call Services
- Services can call Models
- No circular dependencies
- Each layer is independent and testable

## 🎯 Design Patterns

### Repository Pattern
Used in Services layer for database operations:
```python
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

### Use Case Pattern
Encapsulates business workflows:
```python
class LoginUseCase:
    async def execute(self, credentials: LoginRequest) -> TokenResponse:
        # 1. Validate credentials
        # 2. Generate tokens
        # 3. Update last login
        # 4. Return tokens
```

### Dependency Injection
Used throughout the application:
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Decode token and get user
```

## 🔐 Multi-Tenancy

**Organization-based isolation:**
- Each user belongs to one organization
- All queries filter by `organization_id`
- Row-level security in PostgreSQL

**Implementation:**
```python
async def get_current_organization(
    current_user: User = Depends(get_current_user)
) -> Organization:
    return current_user.organization

# In endpoints:
@router.get("/invoices")
async def list_invoices(
    org: Organization = Depends(get_current_organization)
):
    # Automatically filtered by organization
    return await invoice_service.list_by_organization(org.id)
```

## 📝 Naming Conventions

### Files
- `snake_case.py` for all Python files
- `test_*.py` for test files

### Classes
- `PascalCase` for classes
- `*Service` for services
- `*UseCase` for use cases
- `*Repository` for repositories

### Functions
- `snake_case` for functions
- `async def` for async functions
- Prefix with `get_`, `create_`, `update_`, `delete_` for CRUD

### Variables
- `snake_case` for variables
- `UPPER_CASE` for constants

## 🧪 Testing Structure

```
tests/
├── unit/                   # Unit tests (isolated)
│   ├── test_services.py
│   └── test_use_cases.py
├── integration/            # Integration tests (with DB)
│   ├── test_repositories.py
│   └── test_api.py
└── e2e/                    # End-to-end tests
    └── test_workflows.py
```

## 📚 Additional Documentation

- See `README.md` for setup and usage
- See `TODO.md` for implementation checklist
- See API docs at `/api/v1/docs` when running

---

**This structure follows Domain-Driven Design (DDD) principles and Clean Architecture patterns.**
