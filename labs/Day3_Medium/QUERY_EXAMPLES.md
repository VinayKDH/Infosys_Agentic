# Day 3 Medium Lab - Query Examples from Terminal

## Server Status
The API server should be running on: `http://localhost:8000`

Check if it's running:
```bash
curl http://localhost:8000/health
```

## Basic Query Examples

### 1. Simple Query (No Session)
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "stream": false
  }'
```

**Pretty Print Response:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "stream": false
  }' | python3 -m json.tool
```

### 2. Query with Session (Conversation Continuity)
First, get a session ID from a previous query, then use it:

```bash
# First query - save the session_id from response
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "My name is John"}')

SESSION_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

# Second query using the same session
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What is my name?\",
    \"session_id\": \"$SESSION_ID\"
  }" | python3 -m json.tool
```

### 3. Streaming Query (Server-Sent Events)
```bash
curl -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain machine learning in simple terms"
  }'
```

**To see streaming chunks:**
```bash
curl -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me a story about AI"
  }' | while IFS= read -r line; do
    if [[ $line == data:* ]]; then
      echo "$line" | sed 's/data: //' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['chunk'], end='', flush=True)" 2>/dev/null
    fi
  done
echo ""
```

### 4. List All Sessions
```bash
curl http://localhost:8000/api/v1/sessions | python3 -m json.tool
```

### 5. Get Session Information
```bash
# Replace SESSION_ID with actual session ID
curl http://localhost:8000/api/v1/session/SESSION_ID | python3 -m json.tool
```

### 6. Delete a Session
```bash
# Replace SESSION_ID with actual session ID
curl -X DELETE http://localhost:8000/api/v1/session/SESSION_ID | python3 -m json.tool
```

## Using the Test Script

Run the comprehensive test script:
```bash
cd labs/Day3_Medium
./test_api.sh
```

## Interactive Testing with Python

Create a file `test_interactive.py`:

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1"

def query_agent(query, session_id=None):
    """Send a query to the agent"""
    response = requests.post(
        f"{API_URL}/query",
        json={
            "query": query,
            "session_id": session_id,
            "stream": False
        }
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # First query
    result1 = query_agent("What is Python?")
    print(json.dumps(result1, indent=2))
    
    session_id = result1["session_id"]
    
    # Follow-up query with session
    result2 = query_agent("Can you give me an example?", session_id)
    print(json.dumps(result2, indent=2))
```

Run it:
```bash
python3 test_interactive.py
```

## Common Query Examples

### Technical Questions
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the difference between AI and ML?"}' | python3 -m json.tool
```

### Creative Requests
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a haiku about programming"}' | python3 -m json.tool
```

### Code Explanation
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain async/await in Python"}' | python3 -m json.tool
```

### General Questions
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the benefits of using FastAPI?"}' | python3 -m json.tool
```

## Tips

1. **Pretty Print JSON:** Always pipe to `python3 -m json.tool` for readable output
2. **Save Session ID:** Extract session_id from first response for conversation continuity
3. **Check Health:** Use `/health` endpoint to verify server is running
4. **View API Docs:** Open `http://localhost:8000/docs` in browser for interactive testing
5. **Error Handling:** Check HTTP status codes (200 = success, 400 = bad request, 500 = server error)

## Troubleshooting

**Server not responding:**
```bash
# Check if server is running
ps aux | grep uvicorn

# Restart server
cd labs/Day3_Medium
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Key Error:**
- Make sure `.env` file exists with `OPENAI_API_KEY=your_key_here`

**Connection Refused:**
- Verify server is running on port 8000
- Check firewall settings

