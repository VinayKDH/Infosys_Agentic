"""State definition for Amex multi-agent system"""
from typing import TypedDict, Literal, Optional, List, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
import operator


class AmexState(TypedDict):
    """State for Amex Customer Intelligence Platform"""
    
    # Request Information
    customer_id: str
    request_id: str
    request_type: Literal["support", "fraud", "account", "compliance", "multi"]
    original_query: str
    session_id: str
    
    # Planning
    execution_plan: Optional[str]
    required_agents: Annotated[List[str], operator.add]
    priority: Literal["low", "medium", "high", "critical"]
    
    # Agent Results
    support_result: Optional[str]
    fraud_result: Optional[Dict[str, Any]]
    account_intel_result: Optional[Dict[str, Any]]
    compliance_result: Optional[Dict[str, Any]]
    
    # Transaction Data
    transactions: Annotated[List[Dict[str, Any]], operator.add]
    risk_scores: Annotated[List[float], operator.add]
    
    # Compliance
    compliance_checks: Annotated[List[Dict[str, Any]], operator.add]
    compliance_status: Optional[Literal["passed", "failed", "requires_review"]]
    
    # Review
    requires_human_review: bool
    human_approved: Optional[bool]
    human_notes: Optional[str]
    
    # Response
    final_response: Optional[str]
    recommendations: Annotated[List[str], operator.add]
    
    # Messages
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Errors
    errors: Annotated[List[str], operator.add]

