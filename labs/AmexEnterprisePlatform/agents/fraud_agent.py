"""Fraud detection agent"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from state.amex_state import AmexState
from app.config import settings
from tools.transaction_analyzer import analyze_transaction, get_transaction_history
from tools.risk_scorer import calculate_risk_score, analyze_account_patterns
import json


class FraudAgent:
    """Detects and analyzes potential fraud"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
    
    def process(self, state: AmexState) -> AmexState:
        """Process fraud detection request"""
        query = state.get("original_query", "")
        customer_id = state.get("customer_id", "")
        
        try:
            # Extract transaction ID if mentioned
            transaction_id = None
            if "transaction" in query.lower():
                # Try to extract transaction ID (simplified)
                words = query.split()
                for i, word in enumerate(words):
                    if "txn" in word.lower() or "transaction" in word.lower():
                        if i + 1 < len(words):
                            transaction_id = words[i + 1]
                            break
            
            fraud_result = {
                "analysis": "",
                "risk_score": 0,
                "flags": [],
                "recommendations": []
            }
            
            # Get transaction history
            history = get_transaction_history.invoke({"account_id": customer_id, "days": 30})
            
            # Analyze patterns
            patterns = analyze_account_patterns.invoke({
                "account_id": customer_id,
                "transactions": history.get("transactions", [])
            })
            
            # If specific transaction mentioned, analyze it
            if transaction_id:
                transaction = analyze_transaction.invoke({
                    "transaction_id": transaction_id,
                    "account_id": customer_id
                })
                
                risk_analysis = calculate_risk_score.invoke({
                    "transaction": transaction,
                    "account_history": history
                })
                
                fraud_result["transaction_analysis"] = transaction
                fraud_result["risk_score"] = risk_analysis.get("risk_score", 0)
                fraud_result["risk_level"] = risk_analysis.get("risk_level", "low")
                fraud_result["flags"] = risk_analysis.get("flags", [])
                fraud_result["recommended_action"] = risk_analysis.get("recommended_action", "approve")
            
            # Generate analysis summary
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a fraud detection specialist. Analyze the fraud detection results and provide:
                1. Summary of findings
                2. Risk assessment
                3. Recommended actions
                4. Customer communication points"""),
                ("human", """Query: {query}
                
                Risk Score: {risk_score}
                Flags: {flags}
                Patterns: {patterns}
                
                Provide a comprehensive fraud analysis.""")
            ])
            
            chain = analysis_prompt | self.llm
            analysis = chain.invoke({
                "query": query,
                "risk_score": fraud_result.get("risk_score", 0),
                "flags": ", ".join(fraud_result.get("flags", [])),
                "patterns": json.dumps(patterns.get("anomalies", []))
            })
            
            fraud_result["analysis"] = analysis.content
            fraud_result["patterns"] = patterns
            
            # Determine if human review needed
            if fraud_result.get("risk_score", 0) >= 70:
                state["requires_human_review"] = True
                fraud_result["recommendations"].append("Requires immediate human review")
            
            state["fraud_result"] = fraud_result
            state["risk_scores"] = state.get("risk_scores", []) + [fraud_result.get("risk_score", 0)]
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Fraud Agent: {analysis.content}")
            ]
        
        except Exception as e:
            error_msg = f"Fraud agent error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["fraud_result"] = {"error": error_msg}
        
        return state

