# Token Blacklist Documentation

This document describes the token blacklist implementation for secure logout and token revocation.

---

## 🎯 Overview

The token blacklist provides server-side token invalidation using Redis. When a user logs out or an admin revokes a token, it's added to the blacklist and cannot be used again.

---

## 🏗️ Architecture

### Components

1. **TokenBlacklist Service** (`app/core/token_blacklist.py`)
   - Redis-based token storage
   - Automatic TTL management
   - Fail-open design (if Redis unavailable, tokens are accepted)

2. **Authentication Middleware** (`app/core/dependencies.py`)
   - Checks blacklist before validating JWT
   - Returns 401 if token is blacklisted

3. **Logout Endpoint** (`/api/v1/auth/logout`)
   - Adds current token to blacklist
   - Extracts expiration from JWT for TTL

4. **Admin Endpoints** (`/api/v1/admin/tokens/*`)
   - Manual token revocation
   - Blacklist statistics
   - Clear blacklist (testing)

---

## 🔧 How It Works

### 1. User Logout

```
User → POST /api/v1/auth/logout
      ↓
Extract token from Authorization header
      ↓
Decode JWT to get expiration time
      ↓
Add to Redis: blacklist:{token} = "1" (TTL = time until expiration)
      ↓
Return success message
```

### 2. Token Validation

```
User → Request with Bearer token
      ↓
Check Redis: EXISTS blacklist:{token}
      ↓
If exists → 401 "Token has been revoked"
      ↓
If not exists → Continue with normal JWT validation
```

### 3. Automatic Cleanup

Redis automatically removes blacklisted tokens when they expire (TTL), preventing memory bloat.

---

## 📝 API Endpoints

### User Endpoints

#### POST `/api/v1/auth/logout`

Logout and blacklist current token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

### Admin Endpoints

#### GET `/api/v1/admin/tokens/blacklist/stats`

Get blacklist statistics.

**Requires:** Admin role

**Response:**
```json
{
  "status": "active",
  "count": 42,
  "redis_connected": true
}
```

#### POST `/api/v1/admin/tokens/revoke-token`

Manually revoke a specific token.

**Requires:** Admin role

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "message": "Token revoked successfully",
  "revoked": true
}
```

#### POST `/api/v1/admin/tokens/blacklist/clear`

Clear all blacklisted tokens (testing only).

**Requires:** Admin role

**Response:**
```json
{
  "message": "Token blacklist cleared successfully",
  "cleared": true
}
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Redis URL for token blacklist
REDIS_URL=redis://localhost:6379/0

# For production with authentication
REDIS_URL=redis://:password@host:6379/0

# For Redis Cluster
REDIS_URL=redis://host1:6379,host2:6379,host3:6379/0
```

### Redis Requirements

- **Version:** Redis 5.0+
- **Memory:** ~100 bytes per blacklisted token
- **Persistence:** Not required (tokens expire anyway)
- **Replication:** Recommended for high availability

---

## 🔒 Security Considerations

### Fail-Open Design

If Redis is unavailable, the system **fails open** (accepts tokens) to maintain availability. This is a trade-off:

**Pros:**
- Service remains available during Redis outages
- No user-facing errors

**Cons:**
- Blacklisted tokens work during Redis outage
- Logout doesn't fully invalidate tokens

**Mitigation:**
- Monitor Redis health closely
- Use Redis replication for high availability
- Keep JWT expiration short (30 minutes)
- Use refresh tokens for long sessions

### Token Expiration

Blacklisted tokens are stored with TTL matching their expiration:

```python
# Token expires in 30 minutes
ttl = (expires_at - now).total_seconds()  # 1800 seconds

# Redis automatically removes after 30 minutes
redis.setex(f"blacklist:{token}", ttl, "1")
```

This prevents memory bloat and ensures blacklist doesn't grow indefinitely.

### Race Conditions

**Scenario:** User logs out, but token is still used in parallel requests.

**Solution:** Blacklist check happens before JWT validation, so parallel requests will fail after logout completes.

```
Request 1: POST /logout → Add to blacklist → Return
Request 2: GET /data (parallel) → Check blacklist → 401
```

---

## 📊 Performance

### Redis Operations

- **Add token:** O(1) - `SETEX`
- **Check token:** O(1) - `EXISTS`
- **Get stats:** O(N) - `SCAN` (N = number of blacklisted tokens)

### Memory Usage

```
Per token: ~100 bytes (key + value + metadata)
1,000 tokens: ~100 KB
10,000 tokens: ~1 MB
100,000 tokens: ~10 MB
```

### Latency

- **Local Redis:** < 1ms
- **Remote Redis:** 5-10ms
- **Redis Cluster:** 10-20ms

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response: {"access_token": "eyJ..."}

# 2. Use token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJ..."

# Response: {"id": "...", "email": "user@example.com"}

# 3. Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer eyJ..."

# Response: {"message": "Successfully logged out"}

# 4. Try to use token again
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJ..."

# Response: 401 {"detail": "Token has been revoked"}
```

### Admin Testing

```bash
# Get blacklist stats
curl http://localhost:8000/api/v1/admin/tokens/blacklist/stats \
  -H "Authorization: Bearer <admin_token>"

# Response: {"status": "active", "count": 1, "redis_connected": true}

# Manually revoke token
curl -X POST http://localhost:8000/api/v1/admin/tokens/revoke-token \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJ..."}'

# Response: {"message": "Token revoked successfully", "revoked": true}
```

### Automated Testing

```python
import pytest
from app.core.token_blacklist import TokenBlacklist

@pytest.mark.asyncio
async def test_token_blacklist():
    token = "test_token_123"
    
    # Check token not blacklisted
    assert not await TokenBlacklist.is_blacklisted(token)
    
    # Add to blacklist
    await TokenBlacklist.add_token(token)
    
    # Check token is blacklisted
    assert await TokenBlacklist.is_blacklisted(token)
    
    # Remove from blacklist
    await TokenBlacklist.remove_token(token)
    
    # Check token not blacklisted
    assert not await TokenBlacklist.is_blacklisted(token)
```

---

## 🚀 Production Deployment

### Redis Setup

**Option 1: Single Redis Instance**

```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
```

**Option 2: Redis Sentinel (High Availability)**

```yaml
# docker-compose.yml
redis-master:
  image: redis:7-alpine
  command: redis-server --appendonly yes

redis-sentinel:
  image: redis:7-alpine
  command: redis-sentinel /etc/redis/sentinel.conf
  depends_on:
    - redis-master
```

**Option 3: Redis Cluster (Scalability)**

Use managed Redis service:
- AWS ElastiCache
- Google Cloud Memorystore
- Azure Cache for Redis
- Redis Cloud

### Environment Configuration

```bash
# Production
REDIS_URL=redis://:password@redis-prod.example.com:6379/0

# Staging
REDIS_URL=redis://:password@redis-staging.example.com:6379/0

# Development
REDIS_URL=redis://localhost:6379/0
```

### Monitoring

**Key Metrics:**
- Redis connection status
- Blacklist size (number of tokens)
- Redis memory usage
- Blacklist hit rate (how often tokens are checked)

**Alerts:**
- Redis connection failures
- Blacklist size > 100,000 tokens
- Redis memory > 80%

---

## 🐛 Troubleshooting

### Problem: Tokens not being blacklisted

**Symptoms:** Users can still use tokens after logout

**Solutions:**
1. Check Redis connection: `redis-cli ping`
2. Verify REDIS_URL in environment
3. Check logs for blacklist errors
4. Test manually: `redis-cli GET blacklist:your_token`

### Problem: Redis connection failures

**Symptoms:** "Token blacklist Redis connection failed" in logs

**Solutions:**
1. Verify Redis is running: `docker ps | grep redis`
2. Check Redis port: `netstat -an | grep 6379`
3. Test connection: `redis-cli -h host -p port ping`
4. Check firewall rules

### Problem: Memory usage growing

**Symptoms:** Redis memory usage increasing over time

**Solutions:**
1. Check TTL on blacklisted tokens: `redis-cli TTL blacklist:token`
2. Verify tokens have expiration
3. Monitor blacklist size: `GET /api/v1/admin/tokens/blacklist/stats`
4. Consider shorter JWT expiration times

### Problem: Blacklist not working after Redis restart

**Symptoms:** Previously blacklisted tokens work after Redis restart

**Explanation:** This is expected behavior. Blacklist is in-memory only.

**Solutions:**
1. Use Redis persistence (AOF or RDB)
2. Accept that tokens may work briefly after restart
3. Keep JWT expiration short (30 minutes)

---

## 🔄 Alternatives

### 1. Short-Lived Tokens Only

**Pros:**
- No blacklist needed
- Simpler architecture

**Cons:**
- Poor UX (frequent re-login)
- Doesn't solve logout problem

### 2. Database-Based Blacklist

**Pros:**
- Persistent across restarts
- No Redis dependency

**Cons:**
- Slower (database query on every request)
- Database load

### 3. Stateful Sessions

**Pros:**
- Complete control
- Easy revocation

**Cons:**
- Doesn't scale horizontally
- Session storage required
- Not RESTful

### 4. JWT Versioning

**Pros:**
- No blacklist needed
- Revoke all user tokens at once

**Cons:**
- Requires database lookup
- Can't revoke individual tokens

---

## 📚 Best Practices

1. **Keep JWT expiration short** (30 minutes)
   - Limits window of vulnerability
   - Reduces blacklist size

2. **Use refresh tokens** for long sessions
   - Short-lived access tokens
   - Long-lived refresh tokens
   - Refresh tokens can be revoked in database

3. **Monitor Redis health**
   - Set up alerts for connection failures
   - Use Redis replication for HA

4. **Log blacklist operations**
   - Track who revoked what token
   - Audit trail for security

5. **Test logout flow**
   - Verify tokens are actually blacklisted
   - Test parallel requests

6. **Consider token rotation**
   - Issue new token on each request
   - Automatically invalidate old tokens

---

## 📖 References

- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Token Handling](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

---

**Last Updated:** 2024-01-01
**Version:** 1.0.0
