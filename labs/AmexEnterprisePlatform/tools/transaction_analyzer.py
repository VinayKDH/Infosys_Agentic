"""Transaction analysis tool"""
from typing import Dict, Any, Optional
from langchain.tools import tool
import random
from datetime import datetime, timedelta


@tool
def analyze_transaction(transaction_id: str, account_id: str) -> Dict[str, Any]:
    """
    Analyze a specific transaction by ID.
    
    Args:
        transaction_id: The unique transaction identifier
        account_id: The account ID associated with the transaction
    
    Returns:
        Dictionary containing transaction details including:
        - merchant: Merchant name
        - amount: Transaction amount
        - date: Transaction date
        - category: Transaction category
        - risk_score: Risk score (0-100)
        - location: Transaction location
    """
    # Mock implementation - in production, this would query the banking database
    merchants = ["Best Buy", "Amazon", "Starbucks", "Shell Gas", "Walmart", "Target"]
    categories = ["Electronics", "Retail", "Food & Dining", "Gas", "Groceries"]
    
    return {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "merchant": random.choice(merchants),
        "amount": round(random.uniform(10, 500), 2),
        "date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        "category": random.choice(categories),
        "risk_score": random.randint(0, 100),
        "location": f"{random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston'])}, USA",
        "status": "completed"
    }


@tool
def get_transaction_history(account_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Get transaction history for an account.
    
    Args:
        account_id: The account ID
        days: Number of days to retrieve (default: 30)
    
    Returns:
        Dictionary containing transaction history
    """
    # Mock implementation
    transactions = []
    for i in range(random.randint(5, 20)):
        transactions.append({
            "transaction_id": f"TXN{random.randint(100000, 999999)}",
            "merchant": random.choice(["Amazon", "Starbucks", "Shell", "Walmart"]),
            "amount": round(random.uniform(5, 200), 2),
            "date": (datetime.now() - timedelta(days=random.randint(0, days))).isoformat(),
            "category": random.choice(["Retail", "Food", "Gas", "Groceries"])
        })
    
    return {
        "account_id": account_id,
        "period_days": days,
        "total_transactions": len(transactions),
        "transactions": sorted(transactions, key=lambda x: x["date"], reverse=True)
    }

