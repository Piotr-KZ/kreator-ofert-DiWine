# Token Blacklist Implementation Problem

## 🎯 OBJECTIVE
Implement JWT token blacklist using Redis so that logged-out tokens cannot be used to access protected endpoints.

---

## 📋 CURRENT IMPLEMENTATION

### 1. Token Blacklist Service (`app/core/token_blacklist.py`)

```python
class TokenBlacklist:
    @classmethod
    async def get_redis(cls) -> Optional[Redis]:
        """Get Redis client"""
        try:
            redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await redis_client.ping()
            return redis_client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None

    @classmethod
    async def add_token(cls, token: str, expires_at: datetime) -> bool:
        """Add token to blacklist"""
        redis_client = await cls.get_redis()
        if not redis_client:
            return False

        try:
            key = f"blacklist:{token}"
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await redis_client.setex(key, ttl, "1")
                logger.info(f"Token added to blacklist: {key[:50]}... TTL: {ttl}s")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add token to blacklist: {e}")
            return False

    @classmethod
    async def is_blacklisted(cls, token: str) -> bool:
        """Check if token is blacklisted"""
        redis_client = await cls.get_redis()
        if not redis_client:
            return False  # Fail open

        try:
            key = f"blacklist:{token}"
            exists = await redis_client.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False  # Fail open
```

### 2. Logout Endpoint (`app/api/v1/endpoints/auth.py`)

```python
@router.post("/logout", response_model=dict)
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    """Logout user - invalidates access token by adding to blacklist"""
    import logging
    from datetime import datetime
    from app.core.security import decode_access_token
    from app.core.token_blacklist import TokenBlacklist

    logger = logging.getLogger(__name__)

    try:
        # Get token from request
        auth_header = request.headers.get("Authorization")
        logger.info(f"Logout: auth_header present: {bool(auth_header)}")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            logger.info(f"Logout: token extracted, length: {len(token)}")

            # Decode token to get expiration
            payload = decode_access_token(token)
            logger.info(f"Logout: payload: {bool(payload)}, exp: {payload.get('exp') if payload else None}")
            
            if payload and payload.get("exp"):
                expires_at = datetime.fromtimestamp(payload["exp"])
                logger.info(f"Logout: calling add_token with expires_at={expires_at}")
                
                # Add token to blacklist
                result = await TokenBlacklist.add_token(token, expires_at)
                logger.info(f"Logout: add_token result: {result}")
            else:
                logger.warning("Logout: payload or exp missing")
                
    except Exception as e:
        logger.error(f"Logout error: {type(e).__name__}: {str(e)}", exc_info=True)
        # Don't fail logout even if blacklist fails

    return {"message": "Successfully logged out"}
```

### 3. Blacklist Check in Auth Dependency (`app/core/dependencies.py`)

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    from app.core.token_blacklist import TokenBlacklist
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Check if token is blacklisted
        if await TokenBlacklist.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode token
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = await get_user_by_id(db, UUID(user_id))
    if user is None:
        raise credentials_exception

    return user
```

---

## ❌ PROBLEM SYMPTOMS

### 1. Logout Returns Internal Server Error
```bash
$ curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <token>"

Internal Server Error
```

### 2. No Logs Appear
Despite extensive logging in logout endpoint:
```python
logger.info(f"Logout: auth_header present: {bool(auth_header)}")
logger.info(f"Logout: token extracted, length: {len(token)}")
# etc...
```

**NO logs appear in `/tmp/backend_final.log`**

### 3. Redis Keys Not Created
```bash
$ redis-cli KEYS "blacklist:*"
(empty array)
```

Even though `add_token()` should create `blacklist:<token>` key.

### 4. Token Still Works After Logout
```bash
# After logout
$ curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"

{"email":"test@example.com",...}  # ❌ Should be blocked!
```

---

## 🔍 DEBUGGING ATTEMPTS

### 1. Added Extensive Logging
- Added `logger.info()` at every step in logout endpoint
- Added `logger.error()` in try/except blocks
- **Result:** NO logs appear

### 2. Checked Redis Connection
```bash
$ redis-cli PING
PONG  # ✅ Redis works

$ redis-cli KEYS "*"
LIMITS:LIMITER/...  # ✅ Rate limiting uses Redis successfully
```

### 3. Verified Code Changes
```bash
$ grep -n "Logout:" app/api/v1/endpoints/auth.py
214:        logger.info(f"Logout: auth_header present: {bool(auth_header)}")
217:        logger.info(f"Logout: token extracted, length: {len(token)}")
# ✅ Code is in file
```

### 4. Cleared Python Cache
```bash
$ find . -type d -name "__pycache__" -exec rm -rf {} +
$ find . -name "*.pyc" -delete
```

### 5. Restarted Backend Multiple Times
```bash
$ pkill -9 -f uvicorn
$ python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Result:** Still no logs, still Internal Server Error

---

## 🤔 SUSPECTED ROOT CAUSES

### Theory 1: Auto-Reload Not Working
- Code changes don't take effect
- Backend uses cached/old version
- Evidence: Added deliberate syntax error, backend still ran

### Theory 2: Exception Before Logging
- Error occurs before first `logger.info()` is reached
- But try/except should catch it
- No error logs appear either

### Theory 3: Async Redis Issue
- `redis-py` async client may not work properly
- `await redis_client.setex()` may fail silently
- But rate limiting (slowapi) uses Redis successfully

### Theory 4: Import Issue
- `from app.core.token_blacklist import TokenBlacklist` fails
- But no ImportError in logs
- Other imports work fine

### Theory 5: Middleware Intercepts Before Endpoint
- Some middleware catches exception before endpoint runs
- But other endpoints work fine
- Only logout has this issue

---

## 📊 WORKING VS NOT WORKING

### ✅ WORKING
- Health checks
- Registration
- Login
- `/auth/me` endpoint
- Rate limiting (uses Redis)
- Database queries
- All other endpoints

### ❌ NOT WORKING
- Logout endpoint (Internal Server Error)
- Token blacklist (tokens not added to Redis)
- Blacklist check (tokens not blocked after logout)

---

## 🎯 QUESTIONS FOR CLAUDE

1. **Why do NO logs appear from logout endpoint?**
   - Even the first `logger.info()` doesn't show up
   - Try/except should catch any errors
   - Other endpoints log successfully

2. **Why does logout return Internal Server Error?**
   - Traceback shows "Exception in ASGI application"
   - But doesn't show the actual error
   - Try/except should prevent 500 error

3. **Why is Redis key not created?**
   - `add_token()` should create `blacklist:<token>` key
   - Redis connection works (rate limiting uses it)
   - No error logs about Redis failures

4. **Is there a better way to implement token blacklist?**
   - Current approach: Redis with async client
   - Alternative: Database table?
   - Alternative: Synchronous Redis client?

5. **How to properly debug this?**
   - Logs don't appear
   - Auto-reload doesn't work
   - Cache clearing doesn't help

---

## 🛠️ ENVIRONMENT

- **Python:** 3.11
- **FastAPI:** Latest
- **Redis:** redis-py (async)
- **Database:** PostgreSQL
- **OS:** Ubuntu 22.04

---

## 📁 RELEVANT FILES

1. `/home/ubuntu/autoflow-backend/app/core/token_blacklist.py` - TokenBlacklist class
2. `/home/ubuntu/autoflow-backend/app/api/v1/endpoints/auth.py` - Logout endpoint (line 196-234)
3. `/home/ubuntu/autoflow-backend/app/core/dependencies.py` - get_current_user with blacklist check (line 38-46)
4. `/home/ubuntu/autoflow-backend/app/main.py` - FastAPI app with middlewares

---

## 🎯 DESIRED OUTCOME

1. Logout endpoint returns `{"message": "Successfully logged out"}` (200 OK)
2. Token is added to Redis: `blacklist:<token>` key with TTL
3. Subsequent requests with that token get 401 Unauthorized
4. Logs appear showing the flow

---

## ❓ SPECIFIC HELP NEEDED

**Please suggest:**
1. Why logs don't appear (most critical - can't debug without logs)
2. How to fix the Internal Server Error in logout
3. Whether async Redis approach is correct
4. Alternative implementation strategies
5. Debugging techniques when logs don't work

Thank you! 🙏
