# Testing Guide for Amex Enterprise Platform

## Issues Fixed

### 1. Configuration Issues
- ✅ Made `OPENAI_API_KEY` optional in config (will raise error when needed)
- ✅ Added default SECRET_KEY with proper length
- ✅ All settings have sensible defaults

### 2. Import Issues
- ✅ Fixed lazy initialization for vector store manager
- ✅ Added error handling for missing vector store
- ✅ Improved import paths

### 3. Agent Initialization
- ✅ Added API key validation in all agents
- ✅ Added fallback handling in support agent
- ✅ Better error messages

### 4. Vector Store
- ✅ Added dummy retriever fallback when no documents loaded
- ✅ Graceful handling of missing embeddings
- ✅ Better error messages

## Testing Steps

### 1. Basic Configuration Test

```python
# Test config loading
from app.config import settings
print(f"API Title: {settings.API_TITLE}")
print(f"Model: {settings.OPENAI_MODEL}")
```

### 2. Test Without API Key (Should Fail Gracefully)

```python
# This should raise a clear error
from agents.support_agent import SupportAgent
try:
    agent = SupportAgent()
except ValueError as e:
    print(f"Expected error: {e}")
```

### 3. Test With API Key

```bash
# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Or create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

### 4. Test FastAPI Application

```bash
# Start the server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","cache":"disabled","version":"1.0.0"}
```

### 5. Test Authentication

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "password123"}'

# Should return JWT token
```

### 6. Test Query Endpoint (Requires API Key)

```bash
# Get token first
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "password123"}' | jq -r '.access_token')

# Query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What is my balance?",
    "customer_id": "CUST001"
  }'
```

## Common Issues and Solutions

### Issue: "OPENAI_API_KEY not set"
**Solution:** Set the environment variable or add to .env file

### Issue: "Vector store not initialized"
**Solution:** This is expected if no documents are loaded. The system will use a dummy retriever.

### Issue: "Redis connection failed"
**Solution:** This is expected if Redis is not running. Caching will be disabled automatically.

### Issue: Import errors
**Solution:** Make sure you're running from the project root directory:
```bash
cd labs/AmexEnterprisePlatform
python -m app.main
```

## Running Tests

### Manual Testing Script

Create a test file `test_basic.py`:

```python
"""Basic tests"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading"""
    from app.config import settings
    assert settings.API_TITLE == "Amex Customer Intelligence Platform"
    print("✓ Config test passed")

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        from app.auth import authenticate_user
        from app.cache import cache_service
        print("✓ Import test passed")
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        raise

def test_health_endpoint():
    """Test health endpoint"""
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health endpoint test passed")

if __name__ == "__main__":
    print("Running basic tests...")
    test_config()
    test_imports()
    test_health_endpoint()
    print("\nAll basic tests passed!")
```

Run it:
```bash
python test_basic.py
```

## Next Steps

1. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access API docs:**
   - Open http://localhost:8000/docs
   - Test endpoints interactively

## Notes

- The system is designed to work even without Redis (caching disabled)
- The system will work without documents loaded (uses dummy retriever)
- API key is required for actual agent execution
- All errors are logged and handled gracefully

