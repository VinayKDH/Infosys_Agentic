"""Example usage of the Amex Enterprise Platform"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def login(username: str, password: str) -> str:
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/login",
        json={"username": username, "password": password}
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    print(f"✓ Logged in as {username}")
    return token


def query_support(token: str, query: str, customer_id: str = "CUST001"):
    """Query customer support"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/query",
        headers=headers,
        json={
            "query": query,
            "customer_id": customer_id,
            "stream": False
        }
    )
    response.raise_for_status()
    result = response.json()
    print(f"\n📝 Query: {query}")
    print(f"✅ Response: {result['response']}")
    print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
    return result


def main():
    """Example usage"""
    print("=" * 60)
    print("Amex Enterprise Platform - Example Usage")
    print("=" * 60)
    
    # Login
    try:
        token = login("customer1", "password123")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Example 1: Fraud Detection Query
    print("\n" + "=" * 60)
    print("Example 1: Fraud Detection")
    print("=" * 60)
    query_support(
        token,
        "I see a charge for $500 at Best Buy yesterday, but I didn't make that purchase."
    )
    
    time.sleep(2)
    
    # Example 2: Account Intelligence
    print("\n" + "=" * 60)
    print("Example 2: Account Intelligence")
    print("=" * 60)
    query_support(
        token,
        "How can I maximize my rewards this month? Show me my spending patterns."
    )
    
    time.sleep(2)
    
    # Example 3: General Support
    print("\n" + "=" * 60)
    print("Example 3: General Support")
    print("=" * 60)
    query_support(
        token,
        "What is my current balance and when is my next payment due?"
    )
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

