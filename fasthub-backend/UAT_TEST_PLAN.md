# UAT Test Plan - Production-Ready Features

**User Acceptance Testing Plan for AutoFlow Backend**

**Version:** 1.0  
**Date:** 2024-01-01  
**Status:** Ready for Testing

---

## 🎯 Overview

This document outlines the User Acceptance Testing (UAT) plan for all 6 Production-Ready Features implemented in the AutoFlow backend. The goal is to verify that each feature works correctly before deployment to production.

---

## 📋 Test Scope

### Features to Test

1. **Email Service** - 5 types of emails
2. **Rate Limiting** - Protection against abuse
3. **Monitoring** - Sentry integration + health checks
4. **Subscription Checks** - Revenue protection
5. **Token Blacklist** - Secure logout
6. **API Documentation** - Swagger + ReDoc

### Out of Scope

- Performance testing (load testing)
- Security penetration testing
- Frontend integration testing (no frontend yet)

---

## 🧪 Test Environment

### Prerequisites

```bash
# 1. Backend running
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Database available
DATABASE_URL=postgresql://user:pass@localhost:5432/autoflow

# 3. Redis running
REDIS_URL=redis://localhost:6379/0

# 4. SendGrid configured
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=test@example.com

# 5. Sentry configured (optional for testing)
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Test Data

```bash
# Test users
Admin User: admin@test.com / Admin123!
Regular User: user@test.com / User123!

# Test organization
Organization ID: <will be created during tests>

# Test subscription
Stripe Test Card: 4242 4242 4242 4242
```

---

## 📝 Test Cases

---

## 1. Email Service UAT

### Test Case 1.1: Verification Email

**Objective:** Verify that verification email is sent after registration

**Steps:**
1. POST `/api/v1/auth/register` with new user data
2. Check email inbox for verification email
3. Verify email contains:
   - Verification link
   - User's name
   - Correct sender (SENDGRID_FROM_EMAIL)
4. Click verification link
5. Verify user is marked as verified in database

**Expected Result:**
- ✅ Email received within 30 seconds
- ✅ Email contains valid verification link
- ✅ Link works and verifies user
- ✅ User can login after verification

**Test Data:**
```json
{
  "email": "test-verify@example.com",
  "password": "Test123!",
  "full_name": "Test User"
}
```

**Pass Criteria:**
- Email delivered successfully
- Verification link works
- User verified in database

---

### Test Case 1.2: Password Reset Email

**Objective:** Verify that password reset email is sent

**Steps:**
1. POST `/api/v1/auth/password-reset/request` with user email
2. Check email inbox for password reset email
3. Verify email contains:
   - Reset link with token
   - Expiration time (1 hour)
   - Security warning
4. Click reset link
5. POST `/api/v1/auth/password-reset/confirm` with new password
6. Verify password changed successfully

**Expected Result:**
- ✅ Email received within 30 seconds
- ✅ Reset link valid for 1 hour
- ✅ Password changed successfully
- ✅ Can login with new password

**Test Data:**
```json
{
  "email": "user@test.com"
}
```

**Pass Criteria:**
- Email delivered
- Reset link works
- Password changed
- Old password no longer works

---

### Test Case 1.3: Magic Link Email

**Objective:** Verify passwordless login via magic link

**Steps:**
1. POST `/api/v1/auth/magic-link/send` with user email
2. Check email inbox for magic link email
3. Verify email contains:
   - Magic link with token
   - Expiration time (15 minutes)
4. Click magic link
5. POST `/api/v1/auth/magic-link/verify` with token
6. Verify user logged in (receives access token)

**Expected Result:**
- ✅ Email received within 30 seconds
- ✅ Magic link valid for 15 minutes
- ✅ User logged in successfully
- ✅ Token works for API calls

**Test Data:**
```json
{
  "email": "user@test.com"
}
```

**Pass Criteria:**
- Email delivered
- Magic link works
- User logged in
- Access token valid

---

### Test Case 1.4: Invoice Email

**Objective:** Verify invoice email sent after payment

**Steps:**
1. Create subscription for user
2. Trigger successful payment (webhook or manual)
3. Check email inbox for invoice email
4. Verify email contains:
   - Invoice PDF attachment
   - Invoice number
   - Amount paid
   - Payment date
   - Download link
5. Download PDF and verify content

**Expected Result:**
- ✅ Email received within 1 minute
- ✅ PDF attached and downloadable
- ✅ Invoice details correct
- ✅ PDF formatted properly

**Test Data:**
```json
{
  "user_id": "<user_id>",
  "plan": "pro",
  "amount": 29.99
}
```

**Pass Criteria:**
- Email delivered
- PDF attached
- Invoice data correct
- PDF readable

---

### Test Case 1.5: Payment Failed Email

**Objective:** Verify payment failure notification

**Steps:**
1. Create subscription for user
2. Trigger failed payment (test card declined)
3. Check email inbox for payment failed email
4. Verify email contains:
   - Failure reason
   - Action required (update payment method)
   - Link to billing portal
   - Grace period information
5. Click billing portal link
6. Verify link works

**Expected Result:**
- ✅ Email received within 1 minute
- ✅ Failure reason clear
- ✅ Action steps provided
- ✅ Billing portal link works

**Test Data:**
```json
{
  "user_id": "<user_id>",
  "subscription_id": "<subscription_id>",
  "error": "card_declined"
}
```

**Pass Criteria:**
- Email delivered
- Clear instructions
- Billing portal link works
- User can update payment method

---

## 2. Rate Limiting UAT

### Test Case 2.1: Login Rate Limit

**Objective:** Verify login endpoint is rate limited (5/minute)

**Steps:**
1. Make 5 login attempts within 1 minute
2. Verify all 5 succeed (or fail with 401 if wrong password)
3. Make 6th login attempt
4. Verify 429 "Rate limit exceeded" response
5. Check response headers:
   - `X-RateLimit-Limit: 5`
   - `X-RateLimit-Remaining: 0`
   - `X-RateLimit-Reset: <timestamp>`
6. Wait 1 minute
7. Try login again
8. Verify it works

**Expected Result:**
- ✅ First 5 requests succeed
- ✅ 6th request returns 429
- ✅ Rate limit headers present
- ✅ Limit resets after 1 minute

**Test Script:**
```bash
for i in {1..6}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"user@test.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n" \
    -i | grep -E "(Status|X-RateLimit)"
  sleep 10
done
```

**Pass Criteria:**
- 5 requests allowed
- 6th request blocked (429)
- Headers correct
- Limit resets

---

### Test Case 2.2: Register Rate Limit

**Objective:** Verify register endpoint is rate limited (3/hour)

**Steps:**
1. Make 3 registration attempts within 1 hour
2. Verify all 3 succeed (or fail with 400 if email exists)
3. Make 4th registration attempt
4. Verify 429 "Rate limit exceeded" response
5. Check rate limit headers
6. Wait 1 hour
7. Try registration again
8. Verify it works

**Expected Result:**
- ✅ First 3 requests succeed
- ✅ 4th request returns 429
- ✅ Rate limit headers present
- ✅ Limit resets after 1 hour

**Test Script:**
```bash
for i in {1..4}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test$i@example.com\",\"password\":\"Test123!\",\"full_name\":\"Test $i\"}" \
    -w "\nStatus: %{http_code}\n" \
    -i | grep -E "(Status|X-RateLimit)"
  sleep 10
done
```

**Pass Criteria:**
- 3 requests allowed
- 4th request blocked (429)
- Headers correct
- Limit resets

---

### Test Case 2.3: Password Reset Rate Limit

**Objective:** Verify password reset is rate limited (3/hour)

**Steps:**
1. Make 3 password reset requests within 1 hour
2. Verify all 3 succeed
3. Make 4th request
4. Verify 429 response
5. Check rate limit headers

**Expected Result:**
- ✅ First 3 requests succeed
- ✅ 4th request returns 429
- ✅ Rate limit headers present

**Test Script:**
```bash
for i in {1..4}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/v1/auth/password-reset/request \
    -H "Content-Type: application/json" \
    -d '{"email":"user@test.com"}' \
    -w "\nStatus: %{http_code}\n" \
    -i | grep -E "(Status|X-RateLimit)"
  sleep 10
done
```

**Pass Criteria:**
- 3 requests allowed
- 4th request blocked (429)

---

### Test Case 2.4: API Token Creation Rate Limit

**Objective:** Verify API token creation is rate limited (10/hour)

**Steps:**
1. Login and get access token
2. Make 10 API token creation requests within 1 hour
3. Verify all 10 succeed
4. Make 11th request
5. Verify 429 response

**Expected Result:**
- ✅ First 10 requests succeed
- ✅ 11th request returns 429

**Test Script:**
```bash
TOKEN="<access_token>"
for i in {1..11}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/v1/api-tokens \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"Test Token $i\"}" \
    -w "\nStatus: %{http_code}\n"
  sleep 5
done
```

**Pass Criteria:**
- 10 requests allowed
- 11th request blocked (429)

---

## 3. Monitoring UAT

### Test Case 3.1: Health Check Endpoint

**Objective:** Verify basic health check works

**Steps:**
1. GET `/api/v1/health`
2. Verify response:
   - Status: 200
   - Body: `{"status": "healthy"}`
3. Test when database is down
4. Verify still returns 200 (basic check only)

**Expected Result:**
- ✅ Returns 200 OK
- ✅ JSON response with status
- ✅ Fast response (< 100ms)

**Test Script:**
```bash
curl -X GET http://localhost:8000/api/v1/health \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"
```

**Pass Criteria:**
- 200 status
- Correct JSON
- Fast response

---

### Test Case 3.2: Readiness Check Endpoint

**Objective:** Verify readiness check includes dependencies

**Steps:**
1. GET `/api/v1/ready`
2. Verify response includes:
   - `status: "ready"`
   - `database: true`
   - `redis: true` (if configured)
3. Stop database
4. GET `/api/v1/ready` again
5. Verify `database: false` and `status: "not_ready"`
6. Start database
7. Verify returns to ready

**Expected Result:**
- ✅ Returns 200 when all dependencies healthy
- ✅ Returns 503 when any dependency unhealthy
- ✅ Shows status of each dependency

**Test Script:**
```bash
# Test healthy
curl -X GET http://localhost:8000/api/v1/ready \
  -w "\nStatus: %{http_code}\n"

# Stop database
docker stop autoflow-db

# Test unhealthy
curl -X GET http://localhost:8000/api/v1/ready \
  -w "\nStatus: %{http_code}\n"

# Start database
docker start autoflow-db
```

**Pass Criteria:**
- Detects database status
- Detects Redis status
- Returns correct HTTP status

---

### Test Case 3.3: Metrics Endpoint

**Objective:** Verify metrics endpoint returns basic stats

**Steps:**
1. GET `/api/v1/metrics`
2. Verify response includes:
   - `uptime` (seconds)
   - `requests_total` (count)
   - `python_version`
   - `app_version`
3. Make several API calls
4. GET `/api/v1/metrics` again
5. Verify `requests_total` increased

**Expected Result:**
- ✅ Returns basic metrics
- ✅ Metrics update in real-time
- ✅ Uptime increases

**Test Script:**
```bash
# Get initial metrics
curl -X GET http://localhost:8000/api/v1/metrics

# Make some requests
for i in {1..10}; do
  curl -X GET http://localhost:8000/api/v1/health > /dev/null
done

# Get updated metrics
curl -X GET http://localhost:8000/api/v1/metrics
```

**Pass Criteria:**
- Metrics returned
- Request count increases
- Uptime increases

---

### Test Case 3.4: Sentry Error Tracking

**Objective:** Verify errors are sent to Sentry

**Steps:**
1. Configure SENTRY_DSN in environment
2. Restart application
3. Trigger an error (e.g., invalid endpoint)
4. Check Sentry dashboard
5. Verify error appears with:
   - Error message
   - Stack trace
   - Request context
   - User context (if authenticated)
6. Verify sensitive data filtered (Authorization header, passwords)

**Expected Result:**
- ✅ Errors appear in Sentry
- ✅ Stack trace included
- ✅ Context included
- ✅ Sensitive data filtered

**Test Script:**
```bash
# Trigger 404 error
curl -X GET http://localhost:8000/api/v1/nonexistent

# Trigger 500 error (if test endpoint exists)
curl -X GET http://localhost:8000/api/v1/test/error

# Check Sentry dashboard
open https://sentry.io/organizations/<org>/issues/
```

**Pass Criteria:**
- Errors logged to Sentry
- Context included
- No sensitive data leaked

---

## 4. Subscription Checks UAT

### Test Case 4.1: Active Subscription Access

**Objective:** Verify users with active subscription can access protected endpoints

**Steps:**
1. Create user with active subscription
2. Login and get access token
3. GET `/api/v1/users/me` (protected endpoint)
4. Verify 200 OK response
5. GET `/api/v1/subscription/status`
6. Verify `status: "active"` and `has_access: true`

**Expected Result:**
- ✅ User can access protected endpoints
- ✅ Subscription status shows active
- ✅ has_access is true

**Test Script:**
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"User123!"}' \
  | jq -r '.access_token')

# Access protected endpoint
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Check subscription status
curl -X GET http://localhost:8000/api/v1/subscription/status \
  -H "Authorization: Bearer $TOKEN"
```

**Pass Criteria:**
- Protected endpoint accessible
- Subscription status correct

---

### Test Case 4.2: Expired Subscription Blocked

**Objective:** Verify users with expired subscription cannot access protected endpoints

**Steps:**
1. Create user with expired subscription (status: canceled)
2. Login and get access token
3. GET `/api/v1/users/me`
4. Verify 402 "Payment Required" response
5. Verify error message includes:
   - Reason: "Subscription expired"
   - Action: "subscribe"
   - Link to subscription page
6. GET `/api/v1/subscription/status`
7. Verify `status: "canceled"` and `has_access: false`

**Expected Result:**
- ✅ User blocked from protected endpoints
- ✅ Clear error message
- ✅ Action steps provided
- ✅ Subscription status correct

**Test Script:**
```bash
# Update user subscription to canceled
# (manual database update or API call)

# Try to access protected endpoint
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nStatus: %{http_code}\n"

# Check subscription status
curl -X GET http://localhost:8000/api/v1/subscription/status \
  -H "Authorization: Bearer $TOKEN"
```

**Pass Criteria:**
- Access blocked (402)
- Error message clear
- Subscription status correct

---

### Test Case 4.3: Past Due Grace Period

**Objective:** Verify users with past_due subscription get 7-day grace period

**Steps:**
1. Create user with past_due subscription
2. Set subscription updated_at to 3 days ago
3. Login and get access token
4. GET `/api/v1/users/me`
5. Verify 200 OK (still within grace period)
6. GET `/api/v1/subscription/status`
7. Verify warning message about grace period
8. Update subscription updated_at to 8 days ago
9. GET `/api/v1/users/me` again
10. Verify 402 (grace period expired)

**Expected Result:**
- ✅ Access allowed within 7 days
- ✅ Warning message shown
- ✅ Access blocked after 7 days

**Test Script:**
```bash
# Set subscription to past_due (3 days ago)
# (manual database update)

# Access protected endpoint
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Check subscription status
curl -X GET http://localhost:8000/api/v1/subscription/status \
  -H "Authorization: Bearer $TOKEN"

# Set subscription to past_due (8 days ago)
# (manual database update)

# Try to access again
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nStatus: %{http_code}\n"
```

**Pass Criteria:**
- Grace period works (7 days)
- Warning shown
- Access blocked after grace period

---

### Test Case 4.4: Exempt Endpoints

**Objective:** Verify exempt endpoints don't require subscription

**Steps:**
1. Create user with no subscription
2. Login and get access token
3. GET `/api/v1/auth/me` (exempt)
4. Verify 200 OK
5. GET `/api/v1/subscriptions` (exempt - to view plans)
6. Verify 200 OK
7. GET `/api/v1/health` (exempt)
8. Verify 200 OK
9. GET `/api/v1/users/me` (not exempt)
10. Verify 402

**Expected Result:**
- ✅ Exempt endpoints accessible
- ✅ Non-exempt endpoints blocked

**Test Script:**
```bash
# Access exempt endpoints
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/subscriptions \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/health

# Try non-exempt endpoint
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nStatus: %{http_code}\n"
```

**Pass Criteria:**
- Exempt endpoints work
- Non-exempt blocked

---

## 5. Token Blacklist UAT

### Test Case 5.1: Logout Blacklists Token

**Objective:** Verify logout adds token to blacklist

**Steps:**
1. Login and get access token
2. GET `/api/v1/users/me` with token
3. Verify 200 OK
4. POST `/api/v1/auth/logout` with token
5. Verify 200 OK with message "Successfully logged out"
6. GET `/api/v1/users/me` with same token
7. Verify 401 "Token has been revoked"
8. Try to use token for any other endpoint
9. Verify all return 401

**Expected Result:**
- ✅ Logout succeeds
- ✅ Token blacklisted
- ✅ Token cannot be reused
- ✅ Clear error message

**Test Script:**
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"User123!"}' \
  | jq -r '.access_token')

# Use token
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Try to use token again
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nStatus: %{http_code}\n"
```

**Pass Criteria:**
- Logout works
- Token blacklisted
- Cannot reuse token

---

### Test Case 5.2: Blacklist Persists Across Restarts

**Objective:** Verify blacklist survives application restart

**Steps:**
1. Login and get access token
2. Logout (blacklist token)
3. Verify token doesn't work
4. Restart application
5. Try to use token again
6. Verify still returns 401 (blacklist persisted in Redis)

**Expected Result:**
- ✅ Blacklist persists in Redis
- ✅ Token still blocked after restart

**Test Script:**
```bash
# Login and logout
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"User123!"}' \
  | jq -r '.access_token')

curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Restart app
docker restart autoflow-app

# Wait for app to start
sleep 5

# Try to use token
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nStatus: %{http_code}\n"
```

**Pass Criteria:**
- Token still blocked after restart

---

### Test Case 5.3: Token Expires from Blacklist

**Objective:** Verify blacklisted tokens are removed after expiration

**Steps:**
1. Create short-lived token (1 minute expiration)
2. Logout (blacklist token)
3. Check Redis: `EXISTS blacklist:{token}`
4. Verify exists
5. Wait 2 minutes
6. Check Redis again
7. Verify token removed (TTL expired)

**Expected Result:**
- ✅ Token added to blacklist with TTL
- ✅ Token removed after expiration
- ✅ No memory leak

**Test Script:**
```bash
# Login with short expiration
# (modify JWT settings temporarily)

# Logout
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Check Redis
redis-cli EXISTS "blacklist:$TOKEN"

# Wait 2 minutes
sleep 120

# Check Redis again
redis-cli EXISTS "blacklist:$TOKEN"
```

**Pass Criteria:**
- Token removed after TTL
- No memory leak

---

### Test Case 5.4: Admin Token Revocation

**Objective:** Verify admin can manually revoke tokens

**Steps:**
1. Login as regular user, get token
2. Login as admin, get admin token
3. POST `/api/v1/admin/tokens/revoke-token` with user's token
4. Verify 200 OK
5. Try to use user's token
6. Verify 401 "Token has been revoked"
7. GET `/api/v1/admin/tokens/blacklist/stats`
8. Verify count increased

**Expected Result:**
- ✅ Admin can revoke tokens
- ✅ Revoked token doesn't work
- ✅ Stats updated

**Test Script:**
```bash
# Login as user
USER_TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"User123!"}' \
  | jq -r '.access_token')

# Login as admin
ADMIN_TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin123!"}' \
  | jq -r '.access_token')

# Revoke user token
curl -X POST http://localhost:8000/api/v1/admin/tokens/revoke-token \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$USER_TOKEN\"}"

# Try to use user token
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $USER_TOKEN" \
  -w "\nStatus: %{http_code}\n"

# Check stats
curl -X GET http://localhost:8000/api/v1/admin/tokens/blacklist/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Pass Criteria:**
- Admin can revoke
- Token blocked
- Stats correct

---

### Test Case 5.5: Blacklist Stats

**Objective:** Verify blacklist statistics endpoint

**Steps:**
1. GET `/api/v1/admin/tokens/blacklist/stats` (as admin)
2. Verify response includes:
   - `status: "active"`
   - `count: <number>`
   - `redis_connected: true`
3. Logout several users (blacklist tokens)
4. GET stats again
5. Verify count increased
6. Stop Redis
7. GET stats again
8. Verify `status: "unavailable"` and `redis_connected: false`

**Expected Result:**
- ✅ Stats accurate
- ✅ Count updates
- ✅ Detects Redis status

**Test Script:**
```bash
# Get initial stats
curl -X GET http://localhost:8000/api/v1/admin/tokens/blacklist/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Logout several users
# (multiple logout calls)

# Get updated stats
curl -X GET http://localhost:8000/api/v1/admin/tokens/blacklist/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Stop Redis
docker stop autoflow-redis

# Get stats again
curl -X GET http://localhost:8000/api/v1/admin/tokens/blacklist/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Pass Criteria:**
- Stats accurate
- Detects Redis status

---

## 6. API Documentation UAT

### Test Case 6.1: Swagger UI Accessible

**Objective:** Verify Swagger UI is accessible and functional

**Steps:**
1. Open browser to http://localhost:8000/api/v1/docs
2. Verify Swagger UI loads
3. Verify all endpoints visible
4. Verify grouped by tags (Auth, Users, etc.)
5. Expand an endpoint (e.g., POST /auth/login)
6. Verify shows:
   - Request body schema
   - Response schemas
   - Example values
7. Click "Try it out"
8. Fill in test data
9. Click "Execute"
10. Verify request sent and response shown

**Expected Result:**
- ✅ Swagger UI loads
- ✅ All endpoints visible
- ✅ Schemas shown
- ✅ "Try it out" works

**Manual Test:**
- Open http://localhost:8000/api/v1/docs
- Test login endpoint
- Verify response

**Pass Criteria:**
- UI loads
- Endpoints work
- Schemas correct

---

### Test Case 6.2: ReDoc Accessible

**Objective:** Verify ReDoc is accessible

**Steps:**
1. Open browser to http://localhost:8000/api/v1/redoc
2. Verify ReDoc loads
3. Verify all endpoints visible
4. Verify search works
5. Search for "login"
6. Verify finds POST /auth/login
7. Click endpoint
8. Verify shows documentation

**Expected Result:**
- ✅ ReDoc loads
- ✅ All endpoints visible
- ✅ Search works
- ✅ Documentation clear

**Manual Test:**
- Open http://localhost:8000/api/v1/redoc
- Search for endpoints
- Verify documentation

**Pass Criteria:**
- UI loads
- Search works
- Docs readable

---

### Test Case 6.3: OpenAPI Schema Valid

**Objective:** Verify OpenAPI schema is valid

**Steps:**
1. GET `/api/v1/openapi.json`
2. Verify JSON response
3. Verify contains:
   - `openapi: "3.0.0"` (or higher)
   - `info` with title, version, description
   - `paths` with all endpoints
   - `components.schemas` with all models
4. Validate schema using online validator
5. Verify no errors

**Expected Result:**
- ✅ Valid OpenAPI 3.0 schema
- ✅ All endpoints included
- ✅ All schemas included

**Test Script:**
```bash
# Get OpenAPI schema
curl -X GET http://localhost:8000/api/v1/openapi.json > openapi.json

# Validate schema
# Use https://editor.swagger.io/ or
npx @apidevtools/swagger-cli validate openapi.json
```

**Pass Criteria:**
- Schema valid
- No errors
- All endpoints included

---

### Test Case 6.4: Authentication in Swagger

**Objective:** Verify authentication works in Swagger UI

**Steps:**
1. Open Swagger UI
2. Click "Authorize" button
3. Enter Bearer token: `Bearer <token>`
4. Click "Authorize"
5. Try protected endpoint (e.g., GET /users/me)
6. Verify request includes Authorization header
7. Verify response successful
8. Click "Logout"
9. Try protected endpoint again
10. Verify 401 error

**Expected Result:**
- ✅ Authorization button works
- ✅ Token included in requests
- ✅ Protected endpoints accessible
- ✅ Logout works

**Manual Test:**
- Open Swagger UI
- Authorize with token
- Test protected endpoint
- Logout and test again

**Pass Criteria:**
- Authorization works
- Token included
- Logout works

---

## 📊 Test Results Summary

### Test Execution Checklist

| # | Test Case | Status | Pass/Fail | Notes |
|---|-----------|--------|-----------|-------|
| 1.1 | Verification Email | ⏳ Pending | | |
| 1.2 | Password Reset Email | ⏳ Pending | | |
| 1.3 | Magic Link Email | ⏳ Pending | | |
| 1.4 | Invoice Email | ⏳ Pending | | |
| 1.5 | Payment Failed Email | ⏳ Pending | | |
| 2.1 | Login Rate Limit | ⏳ Pending | | |
| 2.2 | Register Rate Limit | ⏳ Pending | | |
| 2.3 | Password Reset Rate Limit | ⏳ Pending | | |
| 2.4 | API Token Rate Limit | ⏳ Pending | | |
| 3.1 | Health Check | ⏳ Pending | | |
| 3.2 | Readiness Check | ⏳ Pending | | |
| 3.3 | Metrics Endpoint | ⏳ Pending | | |
| 3.4 | Sentry Error Tracking | ⏳ Pending | | |
| 4.1 | Active Subscription Access | ⏳ Pending | | |
| 4.2 | Expired Subscription Blocked | ⏳ Pending | | |
| 4.3 | Past Due Grace Period | ⏳ Pending | | |
| 4.4 | Exempt Endpoints | ⏳ Pending | | |
| 5.1 | Logout Blacklists Token | ⏳ Pending | | |
| 5.2 | Blacklist Persists | ⏳ Pending | | |
| 5.3 | Token Expires | ⏳ Pending | | |
| 5.4 | Admin Token Revocation | ⏳ Pending | | |
| 5.5 | Blacklist Stats | ⏳ Pending | | |
| 6.1 | Swagger UI | ⏳ Pending | | |
| 6.2 | ReDoc | ⏳ Pending | | |
| 6.3 | OpenAPI Schema | ⏳ Pending | | |
| 6.4 | Authentication in Swagger | ⏳ Pending | | |

**Total Test Cases:** 26  
**Passed:** 0  
**Failed:** 0  
**Pending:** 26

---

## 🐛 Issues Found

### Critical Issues
*None yet*

### Major Issues
*None yet*

### Minor Issues
*None yet*

---

## ✅ Sign-Off

### Test Execution

- **Tested By:** _______________
- **Date:** _______________
- **Environment:** _______________
- **Version:** _______________

### Approval

- **Product Owner:** _______________
- **Date:** _______________

- **Technical Lead:** _______________
- **Date:** _______________

---

## 📝 Notes

- All tests should be executed in a clean test environment
- Test data should be cleaned up after testing
- Failed tests should be documented with screenshots/logs
- Retests should be performed after fixes

---

**Last Updated:** 2024-01-01  
**Version:** 1.0  
**Status:** Ready for Execution
