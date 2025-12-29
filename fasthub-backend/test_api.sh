#!/bin/bash
# AutoFlow API Testing Script

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

echo "=== AutoFlow API Tests ==="
echo ""

# Test 1: Health Check
echo "1. Testing health endpoint..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# Test 2: Register
echo "2. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test'$(date +%s)'@autoflow.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "organization_name": "Test Org"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo ""

# Test 3: Login
echo "3. Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "founder@autoflow.io",
    "password": "Founder123!"
  }')
echo "$LOGIN_RESPONSE" | python3 -m json.tool
LOGIN_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo ""

# Test 4: Get current user
echo "4. Testing /me endpoint..."
curl -s "$API_URL/auth/me" \
  -H "Authorization: Bearer $LOGIN_TOKEN" | python3 -m json.tool
echo ""

# Test 5: Refresh token
echo "5. Testing token refresh..."
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh_token'])" 2>/dev/null)
curl -s -X POST "$API_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | python3 -m json.tool
echo ""

echo "=== Tests Complete ==="
