"""Account calculation tools"""
from langchain.tools import tool
from typing import Dict, Any
import math


@tool
def calculate_rewards(points: int, category: str) -> Dict[str, Any]:
    """
    Calculate rewards value based on points and category.
    
    Args:
        points: Number of reward points
        category: Category (travel, dining, retail, etc.)
    
    Returns:
        Dictionary with rewards calculation
    """
    # Reward multipliers by category
    multipliers = {
        "travel": 1.5,
        "dining": 1.25,
        "retail": 1.0,
        "gas": 1.0,
        "groceries": 1.0,
        "other": 0.5
    }
    
    multiplier = multipliers.get(category.lower(), 1.0)
    value = points * multiplier / 100  # 100 points = $1 base
    
    return {
        "points": points,
        "category": category,
        "multiplier": multiplier,
        "cash_value": round(value, 2),
        "redemption_options": {
            "statement_credit": round(value, 2),
            "travel": round(value * 1.5, 2),
            "gift_cards": round(value * 0.9, 2)
        }
    }


@tool
def calculate_interest(balance: float, apr: float, days: int) -> Dict[str, Any]:
    """
    Calculate interest charges on a balance.
    
    Args:
        balance: Account balance
        apr: Annual Percentage Rate (as decimal, e.g., 0.18 for 18%)
        days: Number of days
    
    Returns:
        Dictionary with interest calculation
    """
    daily_rate = apr / 365
    interest = balance * daily_rate * days
    
    return {
        "balance": balance,
        "apr": apr,
        "apr_percentage": apr * 100,
        "days": days,
        "daily_rate": round(daily_rate * 100, 4),
        "interest_charge": round(interest, 2),
        "total_balance": round(balance + interest, 2)
    }


@tool
def calculate_minimum_payment(balance: float, apr: float = 0.18) -> Dict[str, Any]:
    """
    Calculate minimum payment required.
    
    Args:
        balance: Current balance
        apr: Annual Percentage Rate (default: 18%)
    
    Returns:
        Dictionary with minimum payment calculation
    """
    # Minimum payment is typically 1% of balance + interest
    interest_charge = balance * (apr / 12)  # Monthly interest
    minimum_percentage = 0.01
    minimum_payment = max(
        balance * minimum_percentage + interest_charge,
        25.0  # Minimum $25
    )
    
    return {
        "balance": balance,
        "apr": apr,
        "monthly_interest": round(interest_charge, 2),
        "minimum_payment": round(minimum_payment, 2),
        "percentage_of_balance": round((minimum_payment / balance) * 100, 2) if balance > 0 else 0
    }

