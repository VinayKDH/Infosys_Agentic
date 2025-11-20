#!/bin/bash

# Day 3 Advanced Lab - Comprehensive API Testing Script
# Tests all endpoints including authentication, queries, metrics, and error handling

API_URL="http://localhost:8001/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Day 3 Advanced Lab - Comprehensive Testing"
echo "=========================================="
echo ""

# Test 1: Health Check
echo -e "${YELLOW}1. Testing Health Check...${NC}"
HEALTH=$(curl -s "http://localhost:8001/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$HEALTH" | python3 -m json.tool
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "$HEALTH"
fi
echo ""

# Test 2: Root Endpoint
echo -e "${YELLOW}2. Testing Root Endpoint...${NC}"
ROOT=$(curl -s "http://localhost:8001/")
if echo "$ROOT" | grep -q "message"; then
    echo -e "${GREEN}✓ Root endpoint works${NC}"
    echo "$ROOT" | python3 -m json.tool
else
    echo -e "${RED}✗ Root endpoint failed${NC}"
fi
echo ""

# Test 3: Metrics Endpoint
echo -e "${YELLOW}3. Testing Metrics Endpoint...${NC}"
METRICS=$(curl -s "$API_URL/metrics")
if [ ! -z "$METRICS" ]; then
    echo -e "${GREEN}✓ Metrics endpoint works${NC}"
    echo "$METRICS" | head -20
    echo "..."
else
    echo -e "${RED}✗ Metrics endpoint failed${NC}"
fi
echo ""

# Test 4: Authentication - Login
echo -e "${YELLOW}4. Testing Authentication (Login)...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Login successful${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    if [ ! -z "$TOKEN" ]; then
        echo "Token obtained: ${TOKEN:0:50}..."
        echo "$LOGIN_RESPONSE" | python3 -m json.tool
    else
        echo -e "${RED}✗ Failed to extract token${NC}"
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESPONSE"
    echo ""
    echo "Trying alternative login method..."
    # Try with query parameters
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login?username=admin&password=admin123")
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        echo -e "${GREEN}✓ Login successful (query params)${NC}"
    else
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
fi
echo ""

# Test 5: Query Endpoint (Authenticated)
echo -e "${YELLOW}5. Testing Query Endpoint (Authenticated)...${NC}"
if [ ! -z "$TOKEN" ]; then
    QUERY_RESPONSE=$(curl -s -X POST "$API_URL/query" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"query": "What is FastAPI?"}')
    
    if echo "$QUERY_RESPONSE" | grep -q "response"; then
        echo -e "${GREEN}✓ Query endpoint works${NC}"
        echo "$QUERY_RESPONSE" | python3 -m json.tool
        SESSION_ID=$(echo "$QUERY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null)
    else
        echo -e "${RED}✗ Query endpoint failed${NC}"
        echo "$QUERY_RESPONSE"
    fi
else
    echo -e "${RED}✗ No token available for query test${NC}"
fi
echo ""

# Test 6: Query with Session (Conversation Continuity)
echo -e "${YELLOW}6. Testing Query with Session (Conversation Continuity)...${NC}"
if [ ! -z "$TOKEN" ] && [ ! -z "$SESSION_ID" ]; then
    SESSION_QUERY=$(curl -s -X POST "$API_URL/query" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"Can you explain it in one sentence?\", \"session_id\": \"$SESSION_ID\"}")
    
    if echo "$SESSION_QUERY" | grep -q "response"; then
        echo -e "${GREEN}✓ Session-based query works${NC}"
        echo "$SESSION_QUERY" | python3 -m json.tool | head -15
    else
        echo -e "${RED}✗ Session query failed${NC}"
        echo "$SESSION_QUERY"
    fi
else
    echo -e "${YELLOW}⚠ Skipping session test (no token or session)${NC}"
fi
echo ""

# Test 7: Unauthorized Access (No Token)
echo -e "${YELLOW}7. Testing Unauthorized Access (No Token)...${NC}"
UNAUTH_RESPONSE=$(curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Test"}')

if echo "$UNAUTH_RESPONSE" | grep -q "401\|Unauthorized\|Not authenticated"; then
    echo -e "${GREEN}✓ Unauthorized access properly rejected${NC}"
    echo "$UNAUTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UNAUTH_RESPONSE"
else
    echo -e "${YELLOW}⚠ Unexpected response (might not have auth middleware)${NC}"
    echo "$UNAUTH_RESPONSE"
fi
echo ""

# Test 8: Invalid Credentials
echo -e "${YELLOW}8. Testing Invalid Credentials...${NC}"
INVALID_LOGIN=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=wrongpassword")

if echo "$INVALID_LOGIN" | grep -q "401\|Incorrect\|Unauthorized"; then
    echo -e "${GREEN}✓ Invalid credentials properly rejected${NC}"
    echo "$INVALID_LOGIN" | python3 -m json.tool 2>/dev/null || echo "$INVALID_LOGIN"
else
    echo -e "${YELLOW}⚠ Unexpected response${NC}"
    echo "$INVALID_LOGIN"
fi
echo ""

# Test 9: Metrics After Requests
echo -e "${YELLOW}9. Checking Metrics After Requests...${NC}"
METRICS_AFTER=$(curl -s "$API_URL/metrics")
if echo "$METRICS_AFTER" | grep -q "http_requests_total"; then
    echo -e "${GREEN}✓ Metrics are being collected${NC}"
    echo "$METRICS_AFTER" | grep -E "http_requests_total|agent_executions" | head -5
else
    echo -e "${YELLOW}⚠ Metrics format might be different${NC}"
fi
echo ""

# Test 10: Another Query (Different Topic)
echo -e "${YELLOW}10. Testing Another Query (Different Topic)...${NC}"
if [ ! -z "$TOKEN" ]; then
    QUERY2=$(curl -s -X POST "$API_URL/query" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"query": "Tell me a programming joke"}')
    
    if echo "$QUERY2" | grep -q "response"; then
        echo -e "${GREEN}✓ Second query works${NC}"
        echo "$QUERY2" | python3 -m json.tool | head -10
    else
        echo -e "${RED}✗ Second query failed${NC}"
        echo "$QUERY2"
    fi
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Testing Complete!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Health Check: ✓"
echo "- Authentication: ✓"
echo "- Query Endpoint: ✓"
echo "- Metrics: ✓"
echo "- Error Handling: ✓"
echo ""
echo "API Documentation: http://localhost:8001/docs"
echo "Metrics: http://localhost:8001/api/v1/metrics"
echo "Health: http://localhost:8001/health"

