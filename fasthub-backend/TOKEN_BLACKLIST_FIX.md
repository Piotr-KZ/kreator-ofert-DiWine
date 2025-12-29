# Token Blacklist Fix - Complete Solution

## Problem Summary

The token blacklist feature was failing with HTTP 500 errors during logout. After extensive debugging, **two critical issues** were identified:

### Issue 1: Async/Await Mismatch
**Root Cause:** Using `redis.Redis` (sync) with `await` (async)

**Symptom:** Internal Server Error 500 on logout, no logs appearing

**Solution:** Changed to sync Redis client and removed all `async`/`await` from token blacklist code

### Issue 2: Timezone Handling Bug  
**Root Cause:** Using `datetime.utcnow()` and `datetime.fromtimestamp()` without timezone awareness

**Symptom:** TTL calculated as `-16200` seconds (token "expired" 4.5 hours ago) instead of `+1800` seconds (30 minutes)

**Explanation:**
- Sandbox runs in EST timezone (UTC-5)
- JWT tokens store `exp` as UTC timestamp
- `datetime.fromtimestamp(exp)` converts to **local time** (EST), not UTC
- `datetime.utcnow()` returns **local time** labeled as UTC (also EST)
- Result: 5-hour difference (18000 seconds) causes negative TTL

**Solution:** Use timezone-aware datetime operations:
```python
# WRONG (uses local timezone)
expires_at = datetime.fromtimestamp(payload["exp"])
now = datetime.utcnow()

# CORRECT (uses UTC)
expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
now = datetime.now(timezone.utc).replace(tzinfo=None)
```

---

## Files Modified

### 1. `/home/ubuntu/autoflow-backend/app/core/token_blacklist.py`

**Changes:**
- Removed `async`/`await` - made all methods synchronous
- Changed `from redis.asyncio import Redis` → `from redis import Redis`
- Fixed timezone handling in `add_token()`:
  ```python
  from datetime import datetime, timezone
  
  # Old (WRONG)
  ttl = int((expires_at - datetime.utcnow()).total_seconds())
  
  # New (CORRECT)
  now = datetime.now(timezone.utc).replace(tzinfo=None)
  ttl = int((expires_at - now).total_seconds())
  ```

### 2. `/home/ubuntu/autoflow-backend/app/api/v1/endpoints/auth.py`

**Changes:**
- Changed `async def logout()` → `def logout()` (sync)
- Removed `await` from `TokenBlacklist.add_token()`
- Fixed timezone handling when parsing JWT exp:
  ```python
  from datetime import datetime, timezone
  
  # Old (WRONG)
  expires_at = datetime.fromtimestamp(payload["exp"])
  
  # New (CORRECT)
  expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
  ```

### 3. `/home/ubuntu/autoflow-backend/app/core/dependencies.py`

**Changes:**
- Removed `await` from `TokenBlacklist.is_blacklisted()` call:
  ```python
  # Old (WRONG)
  if await TokenBlacklist.is_blacklisted(token):
  
  # New (CORRECT)
  if TokenBlacklist.is_blacklisted(token):
  ```

### 4. `/home/ubuntu/autoflow-backend/app/core/config.py`

**Changes:**
- Added missing Redis configuration fields:
  ```python
  REDIS_HOST: str = "localhost"
  REDIS_PORT: int = 6379
  REDIS_DB: int = 0
  ```

### 5. `/home/ubuntu/autoflow-backend/start_backend.sh` (NEW FILE)

**Purpose:** Unset Manus system environment variables to use local `.env` instead

**Content:**
```bash
#!/bin/bash
# Unset Manus environment variables that conflict with local .env
unset DATABASE_URL
unset REDIS_URL
unset REDIS_HOST
unset REDIS_PORT

# Start backend
cd /home/ubuntu/autoflow-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Why needed:** Manus injects `DATABASE_URL` (TiDB/MySQL) as system env var, which overrides local `.env` (PostgreSQL)

---

## Testing Results

### UAT Test Suite: **100% PASS** (8/8)

```
=== SUMMARY ===
PASSED: 8
FAILED: 0
SUCCESS RATE: 100%
```

**Tests Passed:**
1. ✅ Health Check
2. ✅ Readiness Check (Database + Redis)
3. ✅ Metrics Endpoint
4. ✅ Swagger UI
5. ✅ ReDoc
6. ✅ OpenAPI Schema (39 endpoints)
7. ✅ **Token Blacklist - Logout** (FIXED!)
8. ✅ Rate Limiting

### Manual Verification

```bash
# 1. Login
$ curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test12345"}'
# Returns: access_token

# 2. Logout
$ curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
# Returns: {"message": "Successfully logged out"}

# 3. Check Redis
$ redis-cli KEYS "blacklist:*"
# Returns: 2 blacklisted tokens

# 4. Try to use token
$ curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
# Returns: {"detail": "Token has been revoked"} (401 Unauthorized)
```

**✅ Token blacklist working correctly!**

---

## Key Learnings

### 1. Timezone Pitfalls in Python

**Never use `datetime.utcnow()` or `datetime.fromtimestamp()` without timezone!**

```python
# ❌ BAD - Uses local timezone
now = datetime.utcnow()  # Returns local time, not UTC!
exp = datetime.fromtimestamp(timestamp)  # Converts to local time!

# ✅ GOOD - Explicit UTC
now = datetime.now(timezone.utc).replace(tzinfo=None)
exp = datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)
```

### 2. Async/Sync Mismatch Detection

**Symptoms:**
- No logs appearing (exception before log statements)
- HTTP 500 with no traceback
- `TypeError: object X can't be used in 'await' expression`

**Solution:**
- Check if library is actually async (`redis.asyncio` vs `redis`)
- Match function signatures (`async def` requires `await` on all async calls)
- For simple operations (< 1ms), sync is often better than async

### 3. Environment Variable Priority

**Pydantic Settings priority (highest to lowest):**
1. System environment variables
2. `.env` file
3. Default values

**Solution for Manus conflict:**
- Create startup script that `unset`s conflicting env vars
- Or use different variable names in code

---

## Production Deployment Notes

### 1. Start Backend

```bash
# Use startup script to avoid env var conflicts
/home/ubuntu/autoflow-backend/start_backend.sh
```

### 2. Required Services

- **PostgreSQL:** localhost:5432 (database: autoflow)
- **Redis:** localhost:6379 (for rate limiting + token blacklist)

### 3. Environment Variables

All configured in `.env`:
- `DATABASE_URL=postgresql://autoflow:autoflow123@localhost:5432/autoflow`
- `REDIS_HOST=localhost`
- `REDIS_PORT=6379`
- `REDIS_DB=0`

### 4. Monitoring

Token blacklist logs:
```
✅ Redis connected (sync)
✅ Token blacklisted: blacklist:eyJ... (TTL=1800s)
✅ User test@example.com logged out successfully
⛔ Token is blacklisted: blacklist:eyJ...
```

---

## Conclusion

**Token blacklist is now fully functional!**

The fix involved:
1. Converting Redis client from async to sync
2. Fixing timezone handling in datetime operations
3. Adding missing Redis config fields
4. Creating startup script to handle Manus env vars

All 8 UAT tests pass (100% success rate).

**Status: PRODUCTION READY ✅**
