"""Basic tests for Amex Enterprise Platform"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_config():
    """Test configuration loading"""
    from app.config import settings
    assert settings.API_TITLE == "Amex Customer Intelligence Platform"
    print("✓ Config test passed")
    return True


def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        from app.auth import authenticate_user
        from app.cache import cache_service
        from app.monitoring import get_metrics
        from state.amex_state import AmexState
        print("✓ Import test passed")
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_endpoint():
    """Test health endpoint"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth_endpoint():
    """Test authentication endpoint"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.post(
            "/api/v1/login",
            json={"username": "customer1", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("✓ Auth endpoint test passed")
        return True
    except Exception as e:
        print(f"✗ Auth endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools():
    """Test that tools can be imported and used"""
    try:
        from tools.transaction_analyzer import analyze_transaction
        from tools.account_calculator import calculate_rewards
        
        # Test transaction analyzer
        result = analyze_transaction.invoke({
            "transaction_id": "TXN123",
            "account_id": "CUST001"
        })
        assert "transaction_id" in result
        print("✓ Tools test passed")
        return True
    except Exception as e:
        print(f"✗ Tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_state():
    """Test state definition"""
    try:
        from state.amex_state import AmexState
        from langchain_core.messages import HumanMessage
        
        # Create a sample state
        state: AmexState = {
            "customer_id": "CUST001",
            "request_id": "REQ001",
            "request_type": "support",
            "original_query": "Test query",
            "session_id": "SESSION001",
            "execution_plan": None,
            "required_agents": [],
            "priority": "medium",
            "support_result": None,
            "fraud_result": None,
            "account_intel_result": None,
            "compliance_result": None,
            "transactions": [],
            "risk_scores": [],
            "compliance_checks": [],
            "compliance_status": None,
            "requires_human_review": False,
            "human_approved": None,
            "human_notes": None,
            "final_response": None,
            "recommendations": [],
            "messages": [HumanMessage(content="Test")],
            "errors": []
        }
        assert state["customer_id"] == "CUST001"
        print("✓ State test passed")
        return True
    except Exception as e:
        print(f"✗ State test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Running basic tests for Amex Enterprise Platform")
    print("=" * 60)
    print()
    
    results = []
    
    print("1. Testing configuration...")
    results.append(test_config())
    print()
    
    print("2. Testing imports...")
    results.append(test_imports())
    print()
    
    print("3. Testing health endpoint...")
    results.append(test_health_endpoint())
    print()
    
    print("4. Testing auth endpoint...")
    results.append(test_auth_endpoint())
    print()
    
    print("5. Testing tools...")
    results.append(test_tools())
    print()
    
    print("6. Testing state...")
    results.append(test_state())
    print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

