"""Reviewer agent for quality assurance"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from state.amex_state import AmexState
from app.config import settings


class ReviewerAgent:
    """Reviews agent outputs and determines if human review is needed"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
    
    def process(self, state: AmexState) -> AmexState:
        """Review all agent results"""
        support_result = state.get("support_result")
        fraud_result = state.get("fraud_result")
        account_intel_result = state.get("account_intel_result")
        compliance_result = state.get("compliance_result")
        compliance_status = state.get("compliance_status", "passed")
        
        try:
            # Review prompt
            review_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a quality reviewer. Review all agent outputs and determine:
                1. If responses are accurate and complete
                2. If human review is needed
                3. If any corrections are needed
                4. Final response quality
                
                Respond with JSON: {"needs_human_review": bool, "quality_score": 0-100, "review_notes": str}"""),
                ("human", """Review the following agent outputs:
                
                Support: {support}
                Fraud: {fraud}
                Account Intel: {account}
                Compliance: {compliance}
                Compliance Status: {compliance_status}
                
                Provide review assessment.""")
            ])
            
            chain = review_prompt | self.llm
            review = chain.invoke({
                "support": support_result or "N/A",
                "fraud": str(fraud_result) if fraud_result else "N/A",
                "account": str(account_intel_result) if account_intel_result else "N/A",
                "compliance": str(compliance_result) if compliance_result else "N/A",
                "compliance_status": compliance_status
            })
            
            # Determine if human review needed
            needs_human = (
                state.get("requires_human_review", False) or
                compliance_status == "failed" or
                (fraud_result and fraud_result.get("risk_score", 0) >= 70) or
                "high" in state.get("priority", "").lower() or
                "critical" in state.get("priority", "").lower()
            )
            
            state["requires_human_review"] = needs_human
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Reviewer: {'Human review required' if needs_human else 'Approved for auto-response'}")
            ]
        
        except Exception as e:
            error_msg = f"Reviewer agent error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            # Default to requiring human review on error
            state["requires_human_review"] = True
        
        return state

