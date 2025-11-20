"""Risk scoring tool for fraud detection"""
from langchain.tools import tool
from typing import Dict, Any, List
import random


@tool
def calculate_risk_score(transaction: Dict[str, Any], account_history: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate fraud risk score for a transaction.
    
    Args:
        transaction: Transaction details (amount, merchant, location, etc.)
        account_history: Account transaction history
    
    Returns:
        Dictionary with risk score and flags
    """
    risk_score = 0
    flags = []
    
    amount = transaction.get("amount", 0)
    merchant = transaction.get("merchant", "")
    location = transaction.get("location", "")
    
    # Amount-based risk
    if amount > 1000:
        risk_score += 30
        flags.append("high_amount")
    elif amount > 500:
        risk_score += 15
        flags.append("medium_amount")
    
    # Merchant-based risk (mock - in production, use ML model)
    high_risk_merchants = ["Unknown Merchant", "International Merchant"]
    if any(rm in merchant for rm in high_risk_merchants):
        risk_score += 25
        flags.append("suspicious_merchant")
    
    # Location-based risk
    if "International" in location or location == "":
        risk_score += 20
        flags.append("unusual_location")
    
    # Velocity check (mock)
    recent_transactions = account_history.get("recent_transactions", [])
    if len(recent_transactions) > 10:
        risk_score += 15
        flags.append("high_velocity")
    
    # Normalize to 0-100
    risk_score = min(risk_score, 100)
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "high"
        action = "block_and_review"
    elif risk_score >= 40:
        risk_level = "medium"
        action = "flag_for_review"
    else:
        risk_level = "low"
        action = "approve"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "flags": flags,
        "recommended_action": action,
        "confidence": round(100 - risk_score, 2)
    }


@tool
def analyze_account_patterns(account_id: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze spending patterns for an account.
    
    Args:
        account_id: Account ID
        transactions: List of transactions
    
    Returns:
        Dictionary with pattern analysis
    """
    if not transactions:
        return {
            "account_id": account_id,
            "patterns": {},
            "anomalies": []
        }
    
    # Calculate spending by category
    category_spending = {}
    total_spending = 0
    
    for txn in transactions:
        category = txn.get("category", "other")
        amount = txn.get("amount", 0)
        category_spending[category] = category_spending.get(category, 0) + amount
        total_spending += amount
    
    # Detect anomalies (mock - in production, use statistical analysis)
    anomalies = []
    avg_amount = total_spending / len(transactions) if transactions else 0
    
    for txn in transactions:
        if txn.get("amount", 0) > avg_amount * 3:
            anomalies.append({
                "transaction_id": txn.get("transaction_id"),
                "reason": "unusually_high_amount",
                "amount": txn.get("amount"),
                "average": round(avg_amount, 2)
            })
    
    return {
        "account_id": account_id,
        "total_transactions": len(transactions),
        "total_spending": round(total_spending, 2),
        "average_transaction": round(avg_amount, 2),
        "category_breakdown": {k: round(v, 2) for k, v in category_spending.items()},
        "anomalies": anomalies,
        "pattern_summary": f"Account shows {len(anomalies)} anomalies in {len(transactions)} transactions"
    }

