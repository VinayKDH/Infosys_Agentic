#!/bin/bash

# Day 3 Medium Lab - API Testing Script
# This script demonstrates how to send queries to the API from terminal

API_URL="http://localhost:8000/api/v1"

echo "=========================================="
echo "Day 3 Medium Lab - API Testing"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$API_URL/../health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Root Endpoint
echo "2. Testing Root Endpoint..."
curl -s "$API_URL/.." | python3 -m json.tool
echo ""
echo ""

# Test 3: Simple Query
echo "3. Testing Simple Query..."
echo "Query: 'What is artificial intelligence?'"
echo ""
RESPONSE=$(curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "stream": false
  }')

echo "$RESPONSE" | python3 -m json.tool
SESSION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo ""
echo "Session ID: $SESSION_ID"
echo ""

# Test 4: Query with Session (Conversation Continuity)
echo "4. Testing Query with Session (Conversation Continuity)..."
echo "Query: 'Can you explain it in simpler terms?'"
echo ""
curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"Can you explain it in simpler terms?\",
    \"session_id\": \"$SESSION_ID\",
    \"stream\": false
  }" | python3 -m json.tool
echo ""
echo ""

# Test 5: List All Sessions
echo "5. Listing All Sessions..."
curl -s "$API_URL/sessions" | python3 -m json.tool
echo ""
echo ""

# Test 6: Get Session Info
echo "6. Getting Session Info..."
curl -s "$API_URL/session/$SESSION_ID" | python3 -m json.tool
echo ""
echo ""

# Test 7: Another Query (Different Topic)
echo "7. Testing Another Query (Different Topic)..."
echo "Query: 'Tell me a joke'"
echo ""
curl -s -X POST "$API_URL/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me a joke",
    "stream": false
  }' | python3 -m json.tool
echo ""
echo ""

# Test 8: Streaming Query (SSE)
echo "8. Testing Streaming Query (Server-Sent Events)..."
echo "Query: 'Explain machine learning in 3 sentences'"
echo ""
echo "Streaming response:"
curl -s -X POST "$API_URL/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain machine learning in 3 sentences"
  }' | while IFS= read -r line; do
    if [[ $line == data:* ]]; then
      echo "$line" | sed 's/data: //' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['chunk'], end='', flush=True); exit(0 if not data.get('done') else 1)" 2>/dev/null
    fi
  done
echo ""
echo ""

# Test 9: List Sessions Again
echo "9. Listing All Sessions (After Multiple Queries)..."
curl -s "$API_URL/sessions" | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo "To test manually, use these curl commands:"
echo ""
echo "# Simple Query:"
echo "curl -X POST \"$API_URL/query\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"Your question here\"}'"
echo ""
echo "# Query with Session:"
echo "curl -X POST \"$API_URL/query\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"Your question\", \"session_id\": \"SESSION_ID\"}'"
echo ""
echo "# Stream Query:"
echo "curl -X POST \"$API_URL/query/stream\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"Your question\"}'"
echo ""

