"""Compliance validation tool"""
from langchain.tools import tool
from typing import Dict, Any, List
from datetime import datetime


@tool
def validate_compliance(action: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate if an action complies with banking regulations.
    
    Args:
        action: Action to validate (e.g., "dispute_transaction", "close_account")
        customer_data: Customer and account information
    
    Returns:
        Dictionary with compliance validation results
    """
    compliance_rules = {
        "dispute_transaction": {
            "required_fields": ["transaction_id", "reason", "account_id"],
            "max_disputes_per_month": 5,
            "time_limit_days": 60
        },
        "close_account": {
            "required_fields": ["account_id", "reason"],
            "requires_balance_zero": True,
            "requires_human_approval": True
        },
        "transfer_funds": {
            "required_fields": ["from_account", "to_account", "amount"],
            "max_amount": 10000,
            "requires_verification": True
        }
    }
    
    rule = compliance_rules.get(action, {})
    
    if not rule:
        return {
            "action": action,
            "compliant": False,
            "reason": "Unknown action",
            "violations": ["Action not recognized"]
        }
    
    violations = []
    
    # Check required fields
    required_fields = rule.get("required_fields", [])
    for field in required_fields:
        if field not in customer_data:
            violations.append(f"Missing required field: {field}")
    
    # Check business rules
    if action == "dispute_transaction":
        dispute_count = customer_data.get("dispute_count_this_month", 0)
        if dispute_count >= rule.get("max_disputes_per_month", 5):
            violations.append("Maximum disputes per month exceeded")
    
    if action == "transfer_funds":
        amount = customer_data.get("amount", 0)
        if amount > rule.get("max_amount", 10000):
            violations.append(f"Transfer amount exceeds maximum: ${rule.get('max_amount')}")
    
    compliant = len(violations) == 0
    
    return {
        "action": action,
        "compliant": compliant,
        "violations": violations,
        "requires_human_review": rule.get("requires_human_approval", False) or not compliant,
        "timestamp": datetime.now().isoformat()
    }


@tool
def check_regulatory_requirements(operation: str, jurisdiction: str = "US") -> Dict[str, Any]:
    """
    Check regulatory requirements for an operation.
    
    Args:
        operation: Operation type
        jurisdiction: Jurisdiction (US, EU, etc.)
    
    Returns:
        Dictionary with regulatory requirements
    """
    regulations = {
        "US": {
            "dispute_transaction": ["Regulation E", "FCRA"],
            "fraud_detection": ["BSA", "AML"],
            "data_access": ["GLBA", "CCPA"]
        },
        "EU": {
            "dispute_transaction": ["PSD2"],
            "fraud_detection": ["GDPR", "AML"],
            "data_access": ["GDPR"]
        }
    }
    
    jurisdiction_regs = regulations.get(jurisdiction, {})
    applicable_regs = jurisdiction_regs.get(operation, [])
    
    return {
        "operation": operation,
        "jurisdiction": jurisdiction,
        "applicable_regulations": applicable_regs,
        "compliance_required": len(applicable_regs) > 0
    }

