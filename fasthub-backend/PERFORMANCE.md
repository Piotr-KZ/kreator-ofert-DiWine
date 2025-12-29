# Performance Optimization Guide

## Overview

This boilerplate implements performance best practices for production-ready SaaS applications.

---

## Implemented Optimizations

### 1. Database Indexes ✅

**Single Column Indexes:**
```sql
-- Users
idx_users_email (email)
idx_users_organization_id (organization_id)
idx_users_role (role)
idx_users_created_at (created_at)

-- Organizations
idx_organizations_owner_id (owner_id)
idx_organizations_created_at (created_at)

-- Subscriptions
idx_subscriptions_organization_id (organization_id)
idx_subscriptions_status (status)
idx_subscriptions_stripe_subscription_id (stripe_subscription_id) UNIQUE
idx_subscriptions_current_period_end (current_period_end)

-- Invoices
idx_invoices_organization_id (organization_id)
idx_invoices_subscription_id (subscription_id)
idx_invoices_status (status)
idx_invoices_stripe_invoice_id (stripe_invoice_id) UNIQUE
idx_invoices_created_at (created_at)

-- API Tokens
idx_api_tokens_user_id (user_id)
idx_api_tokens_token_hash (token_hash) UNIQUE
idx_api_tokens_expires_at (expires_at)
```

**Composite Indexes (for common queries):**
```sql
idx_users_org_role (organization_id, role)
idx_subscriptions_org_status (organization_id, status)
idx_invoices_org_status (organization_id, status)
```

**Impact:**
- 10-100x faster queries on indexed columns
- Efficient filtering and sorting
- Faster JOIN operations

---

### 2. Connection Pooling ✅

**SQLAlchemy Configuration:**
```python
# app/db/session.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Max connections in pool
    max_overflow=10,       # Extra connections if pool full
    pool_pre_ping=True,    # Test connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=False             # Disable SQL logging in production
)
```

**Benefits:**
- Reuse database connections
- Reduce connection overhead
- Handle concurrent requests efficiently

---

### 3. Redis Caching ✅

**Cache Service:**
```python
from app.core.cache import cache

# Get from cache
value = await cache.get("user:123:profile")

# Set in cache (5 min expiry)
await cache.set("user:123:profile", user_data, expire=300)

# Delete from cache
await cache.delete("user:123:profile")

# Delete pattern
await cache.delete_pattern("user:123:*")
```

**Common Caching Patterns:**

1. **User Profile:**
```python
# Cache user profile for 5 minutes
key = cache.cache_key("user", user_id, "profile")
cached = await cache.get(key)
if cached:
    return cached

user = await db.get(User, user_id)
await cache.set(key, user.dict(), expire=300)
return user
```

2. **Organization Data:**
```python
# Cache organization for 10 minutes
key = cache.cache_key("org", org_id)
cached = await cache.get(key)
if cached:
    return cached

org = await db.get(Organization, org_id)
await cache.set(key, org.dict(), expire=600)
return org
```

3. **Subscription Status:**
```python
# Cache subscription status for 1 minute
key = cache.cache_key("subscription", org_id, "status")
cached = await cache.get(key)
if cached:
    return cached

subscription = await get_active_subscription(org_id)
await cache.set(key, subscription.dict(), expire=60)
return subscription
```

**Cache Invalidation:**
```python
# After user update
await cache.delete_pattern(f"user:{user_id}:*")

# After organization update
await cache.delete_pattern(f"org:{org_id}:*")
```

---

### 4. Query Optimization ✅

**Best Practices:**

1. **Use `select()` instead of `query()`:**
```python
# ✅ Good (SQLAlchemy 2.0 style)
stmt = select(User).where(User.email == email)
result = await db.execute(stmt)
user = result.scalar_one_or_none()

# ❌ Bad (SQLAlchemy 1.x style)
user = await db.query(User).filter(User.email == email).first()
```

2. **Eager Loading (avoid N+1 queries):**
```python
# ✅ Good (load organization with user)
stmt = select(User).options(selectinload(User.organization)).where(User.id == user_id)
result = await db.execute(stmt)
user = result.scalar_one()

# ❌ Bad (N+1 query problem)
user = await db.get(User, user_id)
org = await db.get(Organization, user.organization_id)  # Extra query!
```

3. **Pagination:**
```python
# ✅ Good (limit results)
stmt = select(User).limit(20).offset(page * 20)
result = await db.execute(stmt)
users = result.scalars().all()

# ❌ Bad (load all records)
users = await db.execute(select(User))
```

4. **Selective Loading:**
```python
# ✅ Good (load only needed columns)
stmt = select(User.id, User.email, User.full_name)
result = await db.execute(stmt)
users = result.all()

# ❌ Bad (load all columns)
users = await db.execute(select(User))
```

---

### 5. Response Compression ✅

**GZip Middleware:**
```python
# Automatically compresses responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Nginx Compression:**
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json;
```

**Impact:**
- 60-80% reduction in response size
- Faster page loads
- Reduced bandwidth costs

---

### 6. Async Operations ✅

**All I/O operations are async:**
- Database queries (SQLAlchemy async)
- HTTP requests (httpx)
- Redis operations (aioredis)
- Email sending (async SendGrid)

**Benefits:**
- Non-blocking I/O
- Handle more concurrent requests
- Better resource utilization

---

### 7. Rate Limiting ✅

**Prevents abuse and ensures fair usage:**

- Application level (slowapi)
- Nginx level (nginx.conf)

**Impact:**
- Prevents DoS attacks
- Ensures service availability
- Fair resource distribution

---

## Performance Monitoring

### 1. Response Time Tracking

**Middleware logs response time:**
```
INFO: POST /api/v1/auth/login - 200 - 0.123s
```

**Headers:**
```
X-Process-Time: 0.123
```

### 2. Database Query Monitoring

**Enable SQL logging (development only):**
```python
# app/db/session.py
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # Log all SQL queries
)
```

### 3. Redis Monitoring

**Check Redis stats:**
```bash
redis-cli info stats
redis-cli slowlog get 10
```

---

## Performance Benchmarks

### Expected Performance (with optimizations)

**API Endpoints:**
- Auth (login): < 200ms
- User profile: < 50ms (cached), < 150ms (uncached)
- List users: < 100ms (20 items)
- Create subscription: < 300ms

**Database Queries:**
- Indexed lookups: < 10ms
- Joins with indexes: < 50ms
- Full table scans: Avoid!

**Cache Hit Rates:**
- Target: > 80% hit rate
- User profiles: > 90%
- Organization data: > 85%

---

## Optimization Checklist

### Database

- [x] Indexes on foreign keys
- [x] Indexes on frequently queried columns
- [x] Composite indexes for common queries
- [x] Connection pooling configured
- [ ] Query performance monitoring
- [ ] Slow query logging enabled
- [ ] Regular EXPLAIN ANALYZE reviews

### Caching

- [x] Redis cache service
- [x] Cache helper methods
- [ ] Cache hit rate monitoring
- [ ] Cache invalidation strategy
- [ ] Cache warming for critical data

### API

- [x] Response compression (GZip)
- [x] Rate limiting
- [x] Async operations
- [ ] CDN for static assets
- [ ] API response pagination
- [ ] Conditional requests (ETags)

### Frontend

- [ ] Code splitting
- [ ] Lazy loading
- [ ] Image optimization
- [ ] Browser caching headers
- [ ] Minification

---

## Load Testing

### Using Apache Bench

```bash
# Test login endpoint
ab -n 1000 -c 10 -p login.json -T application/json \
  http://localhost:8000/api/v1/auth/login

# Test user list (with auth)
ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/users/
```

### Using Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
    
    @task
    def get_profile(self):
        self.client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task
    def list_users(self):
        self.client.get("/api/v1/users/", headers={
            "Authorization": f"Bearer {self.token}"
        })
```

Run:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Scaling Strategies

### Horizontal Scaling

**Application:**
- Deploy multiple API instances
- Use load balancer (Nginx, AWS ALB)
- Docker Compose scaling: `docker-compose up --scale api=3`

**Database:**
- Read replicas for read-heavy workloads
- Sharding for write-heavy workloads
- Managed database services (AWS RDS, Google Cloud SQL)

**Cache:**
- Redis Cluster for high availability
- Redis Sentinel for automatic failover

### Vertical Scaling

**Increase resources:**
- More CPU cores
- More RAM
- Faster disks (SSD)

**Optimize configuration:**
- Increase connection pool size
- Increase worker processes
- Tune OS parameters

---

## Common Performance Issues

### 1. N+1 Query Problem

**Symptom:** Many database queries for related data

**Solution:** Use eager loading
```python
stmt = select(User).options(selectinload(User.organization))
```

### 2. Missing Indexes

**Symptom:** Slow queries on filtered columns

**Solution:** Add indexes
```bash
alembic revision -m "Add index"
# Edit migration file
alembic upgrade head
```

### 3. Cache Misses

**Symptom:** High database load, slow responses

**Solution:** Implement caching strategy
```python
await cache.set(key, data, expire=300)
```

### 4. Large Payloads

**Symptom:** Slow API responses, high bandwidth

**Solution:** 
- Pagination
- Selective field loading
- Response compression

### 5. Blocking Operations

**Symptom:** Low concurrency, timeouts

**Solution:** Use async operations
```python
async def get_data():
    return await db.execute(stmt)
```

---

## Monitoring Tools

**Recommended:**
- **Application:** New Relic, Datadog, Sentry
- **Database:** pg_stat_statements, MySQL slow query log
- **Cache:** Redis INFO, RedisInsight
- **Infrastructure:** Prometheus + Grafana

---

## Further Optimization

**Advanced techniques:**
- Database query caching
- Full-text search (Elasticsearch)
- Message queues (Celery + Redis)
- CDN for static assets
- HTTP/2 and HTTP/3
- Database partitioning
- Materialized views

---

## References

- [SQLAlchemy Performance](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [FastAPI Performance](https://fastapi.tiangolo.com/async/)
- [Redis Best Practices](https://redis.io/topics/optimization)
- [MySQL Optimization](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
