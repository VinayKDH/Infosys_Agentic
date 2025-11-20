# Day 3 Advanced Lab - Query Examples from Terminal

## Server Status
The API server is running on: `http://localhost:8001`

**Note:** Day 3 Advanced requires authentication (JWT tokens) for most endpoints.

## Features
- ✅ JWT Authentication
- ✅ Redis Caching (if Redis is running)
- ✅ Prometheus Metrics
- ✅ Health Checks
- ✅ Structured Logging

---

## Step 1: Authentication

### Login to Get JWT Token

```bash
# Login as admin
curl -X POST "http://localhost:8001/api/v1/auth/login?username=admin&password=admin123" | python3 -m json.tool
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**Save the token:**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login?username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token: $TOKEN"
```

**Available Users:**
- Username: `admin`, Password: `admin123`
- Username: `user`, Password: `user123`

---

## Step 2: Send Queries (Requires Authentication)

### Simple Query

```bash
# First, get token
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login?username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Then send query with token
curl -X POST "http://localhost:8001/api/v1/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "stream": false
  }' | python3 -m json.tool
```

### Query with Session (Conversation Continuity)

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login?username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# First query - save session_id
RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "My name is Alice"}')

SESSION_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

# Follow-up query using session
curl -X POST "http://localhost:8001/api/v1/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What is my name?\",
    \"session_id\": \"$SESSION_ID\"
  }" | python3 -m json.tool
```

---

## Step 3: Check Metrics

### View Prometheus Metrics

```bash
curl http://localhost:8001/api/v1/metrics | head -50
```

This shows:
- HTTP request counts
- Request durations
- Agent executions
- Cache hits/misses
- Active sessions

---

## Step 4: Health Check

### Check Service Health

```bash
curl http://localhost:8001/health | python3 -m json.tool
```

**Response:**
```json
{
    "status": "healthy",
    "cache": "connected"  // or "disabled" if Redis not running
}
```

---

## Complete Example Script

```bash
#!/bin/bash

API_URL="http://localhost:8001/api/v1"

echo "=== Day 3 Advanced Lab - API Testing ==="
echo ""

# Step 1: Login
echo "1. Logging in..."
TOKEN=$(curl -s -X POST "$API_URL/auth/login?username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token obtained: ${TOKEN:0:50}..."
echo ""

# Step 2: Health Check
echo "2. Health Check..."
curl -s "$API_URL/../health" | python3 -m json.tool
echo ""

# Step 3: Send Query
echo "3. Sending Query..."
curl -s -X POST "$API_URL/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is FastAPI?"}' | python3 -m json.tool
echo ""

# Step 4: Check Metrics
echo "4. Checking Metrics..."
curl -s "$API_URL/metrics" | head -30
echo ""

echo "=== Testing Complete ==="
```

---

## Quick Reference

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/api/v1/auth/login` | POST | No | Get JWT token |
| `/api/v1/query` | POST | Yes | Process query |
| `/api/v1/metrics` | GET | No | Prometheus metrics |
| `/docs` | GET | No | Interactive API docs |

### Authentication

All authenticated endpoints require:
```
Authorization: Bearer <token>
```

### Error Responses

**401 Unauthorized:**
```json
{
    "detail": "Incorrect username or password"
}
```

**401 Unauthorized (Invalid Token):**
```json
{
    "detail": "Could not validate credentials"
}
```

---

## Testing with Python

```python
import requests

API_URL = "http://localhost:8001/api/v1"

# Login
response = requests.post(
    f"{API_URL}/auth/login",
    params={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Query
response = requests.post(
    f"{API_URL}/query",
    headers=headers,
    json={"query": "What is AI?"}
)
print(response.json())
```

---

## Notes

1. **Redis Caching:** If Redis is not running, caching will be automatically disabled
2. **Token Expiry:** Tokens expire after 30 minutes (configurable)
3. **Metrics:** Prometheus metrics are available at `/api/v1/metrics`
4. **Logging:** All requests are logged with structured logging
5. **Rate Limiting:** Rate limiting is configured but may require Redis

---

## Troubleshooting

**Authentication fails:**
- Check username/password (admin/admin123 or user/user123)
- Verify token is included in Authorization header

**Cache shows "disabled":**
- Redis is not running (this is OK, caching will be disabled)
- To enable: `docker run -d -p 6379:6379 redis:7-alpine`

**Port conflict:**
- Day 3 Advanced runs on port 8001 (Day 3 Medium runs on 8000)
- Change port in `.env` or command line if needed

