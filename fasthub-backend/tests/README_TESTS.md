# FastHub - Automated Tests

## 📋 Test Files

### **Core Tests:**
1. `test_auth.py` - Authentication (register, login, logout)
2. `test_auth_advanced.py` - Advanced auth (refresh token, password reset)
3. `test_organizations.py` - Organization management + onboarding

### **Configuration:**
- `conftest.py` - Test fixtures and configuration
- `pytest.ini` - Pytest configuration

---

## 🚀 Running Tests

### **With Docker (RECOMMENDED):**

```bash
# All tests
docker-compose exec backend pytest

# Specific file
docker-compose exec backend pytest tests/test_auth.py

# Specific test
docker-compose exec backend pytest tests/test_auth.py::test_register_user

# With coverage report
docker-compose exec backend pytest --cov=app --cov-report=html

# Fail fast (stop on first failure)
docker-compose exec backend pytest -x

# Verbose output
docker-compose exec backend pytest -vv
```

### **Without Docker:**

```bash
cd fasthub-backend

# Activate venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

---

## 📊 Test Coverage

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

---

## ✅ Test Checklist

### **Authentication Tests:**
- [x] User registration (3 fields)
- [x] Duplicate email validation
- [x] Login success
- [x] Login with wrong password
- [x] Token refresh
- [x] Logout (token blacklist)
- [x] Password reset request
- [x] Password change

### **Organization Tests:**
- [x] Get current organization
- [x] Complete organization onboarding
- [x] Validate NIP (10 digits)
- [x] Validate postal code (XX-XXX)
- [x] Update organization

---

## 🔧 Adding New Tests

### **1. Create test file:**

```python
# tests/test_feature.py
"""Feature tests"""

def test_feature_works(client, auth_headers):
    """Test feature functionality"""
    response = client.get("/api/v1/feature", headers=auth_headers)
    assert response.status_code == 200
```

### **2. Run tests:**

```bash
docker-compose exec backend pytest tests/test_feature.py
```

---

## 📝 Test Fixtures

Available in `conftest.py`:

- `client` - FastAPI test client
- `db` - Test database session
- `test_user_data` - Sample user data
- `auth_headers` - Authenticated headers (Bearer token)

---

## 🐛 Debugging Failed Tests

```bash
# Show full traceback
docker-compose exec backend pytest -vv --tb=long

# Run only failed tests
docker-compose exec backend pytest --lf

# Drop into debugger on failure
docker-compose exec backend pytest --pdb
```

---

## ✅ CI/CD Integration

Tests run automatically in Docker:

```yaml
# docker-compose.yml
backend:
  command: >
    sh -c "
      alembic upgrade head &&
      pytest &&
      uvicorn app.main:app --reload
    "
```

---

## 📊 Expected Results

All tests should pass:

```
tests/test_auth.py .................... [ 40%]
tests/test_auth_advanced.py ........... [ 60%]
tests/test_organizations.py ........... [100%]

======================== 15 passed in 2.34s ========================
```

---

## 🎯 Next Steps

1. ✅ Run tests: `docker-compose exec backend pytest`
2. ✅ Check coverage: `pytest --cov=app`
3. ✅ Add new tests for new features
4. ✅ Keep coverage above 80%

---

**Happy Testing!** 🚀
