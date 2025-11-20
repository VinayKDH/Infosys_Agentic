"""Compliance agent"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from state.amex_state import AmexState
from app.config import settings
from tools.compliance_validator import validate_compliance, check_regulatory_requirements
import json


class ComplianceAgent:
    """Ensures regulatory compliance"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
    
    def process(self, state: AmexState) -> AmexState:
        """Process compliance validation"""
        query = state.get("original_query", "")
        customer_id = state.get("customer_id", "")
        
        try:
            # Determine action type
            action = "support_query"
            if "dispute" in query.lower():
                action = "dispute_transaction"
            elif "close" in query.lower() and "account" in query.lower():
                action = "close_account"
            elif "transfer" in query.lower():
                action = "transfer_funds"
            
            # Validate compliance
            customer_data = {
                "customer_id": customer_id,
                "account_id": customer_id,
                "dispute_count_this_month": 2  # Mock
            }
            
            validation = validate_compliance.invoke({
                "action": action,
                "customer_data": customer_data
            })
            
            # Check regulatory requirements
            regulations = check_regulatory_requirements.invoke({
                "operation": action,
                "jurisdiction": "US"
            })
            
            compliance_result = {
                "action": action,
                "compliant": validation.get("compliant", False),
                "violations": validation.get("violations", []),
                "requires_human_review": validation.get("requires_human_review", False),
                "regulations": regulations.get("applicable_regulations", []),
                "timestamp": validation.get("timestamp")
            }
            
            # Update state
            if not validation.get("compliant", False):
                state["compliance_status"] = "failed"
                state["requires_human_review"] = True
            elif validation.get("requires_human_review", False):
                state["compliance_status"] = "requires_review"
                state["requires_human_review"] = True
            else:
                state["compliance_status"] = "passed"
            
            state["compliance_result"] = compliance_result
            state["compliance_checks"] = state.get("compliance_checks", []) + [compliance_result]
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Compliance: {'PASSED' if compliance_result['compliant'] else 'FAILED'}")
            ]
        
        except Exception as e:
            error_msg = f"Compliance agent error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["compliance_result"] = {"error": error_msg}
            state["compliance_status"] = "failed"
        
        return state

