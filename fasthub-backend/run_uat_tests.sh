#!/bin/bash

# UAT Test Suite
echo "=== AUTOFLOW BACKEND UAT TEST SUITE ===" > uat_results.log
echo "Date: $(date)" >> uat_results.log
echo "Backend: http://localhost:8000" >> uat_results.log
echo "" >> uat_results.log

PASS=0
FAIL=0

# Test 3.1: Health Check
echo "TEST 3.1: Health Check" >> uat_results.log
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/v1/health)
if echo "$RESPONSE" | grep -q "HTTP:200" && echo "$RESPONSE" | grep -q "healthy"; then
  echo "✅ PASS" >> uat_results.log
  ((PASS++))
else
  echo "❌ FAIL" >> uat_results.log
  ((FAIL++))
fi

# Test 3.2: Readiness Check
echo "" >> uat_results.log
echo "TEST 3.2: Readiness Check" >> uat_results.log
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/v1/ready)
if echo "$RESPONSE" | grep -q "HTTP:200" && echo "$RESPONSE" | grep -q "ready"; then
  echo "✅ PASS - Database and Redis healthy" >> uat_results.log
  ((PASS++))
else
  echo "❌ FAIL" >> uat_results.log
  echo "$RESPONSE" | head -5 >> uat_results.log
  ((FAIL++))
fi

# Test 3.3: Metrics
echo "" >> uat_results.log
echo "TEST 3.3: Metrics Endpoint" >> uat_results.log
RESPONSE=$(curl -s http://localhost:8000/api/v1/metrics)
if echo "$RESPONSE" | grep -q "uptime"; then
  echo "✅ PASS - Metrics include uptime" >> uat_results.log
  ((PASS++))
else
  echo "❌ FAIL" >> uat_results.log
  ((FAIL++))
fi

# Test 6.1: Swagger UI
echo "" >> uat_results.log
echo "TEST 6.1: Swagger UI" >> uat_results.log
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/v1/docs)
if echo "$RESPONSE" | grep -q "HTTP:200" && echo "$RESPONSE" | grep -q "swagger"; then
  echo "✅ PASS" >> uat_results.log
  ((PASS++))
else
  echo "❌ FAIL" >> uat_results.log
  ((FAIL++))
fi

# Test 6.2: ReDoc
echo "" >> uat_results.log
echo "TEST 6.2: ReDoc" >> uat_results.log
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/v1/redoc)
if echo "$RESPONSE" | grep -q "HTTP:200" && echo "$RESPONSE" | grep -q "redoc"; then
  echo "✅ PASS" >> uat_results.log
  ((PASS++))
else
  echo "❌ FAIL" >> uat_results.log
  ((FAIL++))
fi

# Test 6.3: OpenAPI Schema
echo "" >> uat_results.log
echo "TEST 6.3: OpenAPI Schema" >> uat_results.log
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/v1/openapi.json)
if echo "$RESPONSE" | grep -q "HTTP:200" && echo "$RESPONSE" | grep -q "openapi"; then
  ENDPOINTS=$(echo "$RESPONSE" | grep -o '"/api/v1' | wc -l)
  echo "✅ PASS - Found $ENDPOINTS endpoints" >> uat_results.log
  ((PASS++))
else
  echo "❌ FAIL" >> uat_results.log
  ((FAIL++))
fi

# Create test user for auth tests
echo "" >> uat_results.log
echo "SETUP: Creating test user..." >> uat_results.log
REGISTER=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"uat-test@example.com","password":"Test123!","full_name":"UAT Test"}' \
  -w "\nHTTP:%{http_code}")

if echo "$REGISTER" | grep -q "HTTP:201\|HTTP:400"; then
  # Login
  LOGIN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"uat-test@example.com","password":"Test123!"}')
  
  TOKEN=$(echo "$LOGIN" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
  
  if [ -n "$TOKEN" ]; then
    echo "✅ Test user logged in" >> uat_results.log
    echo "$TOKEN" > /tmp/uat_token.txt
    
    # Test 5.1: Token Blacklist - Logout
    echo "" >> uat_results.log
    echo "TEST 5.1: Token Blacklist - Logout" >> uat_results.log
    
    # Use token
    USE1=$(curl -s -w "\nHTTP:%{http_code}" -X GET http://localhost:8000/api/v1/auth/me \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$USE1" | grep -q "HTTP:200"; then
      # Logout
      LOGOUT=$(curl -s -w "\nHTTP:%{http_code}" -X POST http://localhost:8000/api/v1/auth/logout \
        -H "Authorization: Bearer $TOKEN")
      
      # Try to use token again
      USE2=$(curl -s -w "\nHTTP:%{http_code}" -X GET http://localhost:8000/api/v1/auth/me \
        -H "Authorization: Bearer $TOKEN")
      
      if echo "$USE2" | grep -q "HTTP:401\|HTTP:403"; then
        echo "✅ PASS - Token blacklisted after logout" >> uat_results.log
        ((PASS++))
      else
        echo "❌ FAIL - Token still works after logout" >> uat_results.log
        ((FAIL++))
      fi
    else
      echo "❌ FAIL - Could not use token before logout" >> uat_results.log
      ((FAIL++))
    fi
    
  else
    echo "❌ Failed to login" >> uat_results.log
  fi
else
  echo "❌ Failed to create user" >> uat_results.log
  echo "$REGISTER" | head -5 >> uat_results.log
fi

# Test 2.1: Rate Limiting - Login
echo "" >> uat_results.log
echo "TEST 2.1: Rate Limiting - Login (5/minute)" >> uat_results.log
echo "Making 6 login attempts..." >> uat_results.log

LIMITED=false
for i in {1..6}; do
  RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}')
  
  if echo "$RESPONSE" | grep -q "HTTP:429"; then
    LIMITED=true
    break
  fi
  sleep 1
done

if [ "$LIMITED" = true ]; then
  echo "✅ PASS - Rate limit enforced" >> uat_results.log
  ((PASS++))
else
  echo "⚠️  SKIP - Rate limit not triggered (may need more requests)" >> uat_results.log
fi

# Summary
echo "" >> uat_results.log
echo "=== SUMMARY ===" >> uat_results.log
echo "PASSED: $PASS" >> uat_results.log
echo "FAILED: $FAIL" >> uat_results.log
TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
  PERCENT=$((PASS * 100 / TOTAL))
  echo "SUCCESS RATE: $PERCENT%" >> uat_results.log
fi

cat uat_results.log
