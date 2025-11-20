"""Account intelligence agent"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from state.amex_state import AmexState
from app.config import settings
from tools.transaction_analyzer import get_transaction_history
from tools.account_calculator import calculate_rewards
from tools.risk_scorer import analyze_account_patterns
import json


class AccountIntelAgent:
    """Provides financial insights and recommendations"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
    
    def process(self, state: AmexState) -> AmexState:
        """Process account intelligence request"""
        query = state.get("original_query", "")
        customer_id = state.get("customer_id", "")
        
        try:
            # Get transaction history
            history = get_transaction_history.invoke({"account_id": customer_id, "days": 90})
            
            # Analyze patterns
            patterns = analyze_account_patterns.invoke({
                "account_id": customer_id,
                "transactions": history.get("transactions", [])
            })
            
            # Calculate rewards if mentioned
            rewards_info = None
            if "rewards" in query.lower() or "points" in query.lower():
                # Mock points (in production, get from account)
                points = 50000
                rewards_info = calculate_rewards.invoke({
                    "points": points,
                    "category": "travel"
                })
            
            # Generate insights
            insights_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a financial insights specialist. Analyze account data and provide:
                1. Spending patterns and trends
                2. Category breakdown
                3. Personalized recommendations
                4. Rewards optimization suggestions
                5. Budgeting tips
                
                Be specific, actionable, and helpful."""),
                ("human", """Query: {query}
                
                Transaction History: {history}
                Patterns: {patterns}
                Rewards: {rewards}
                
                Provide comprehensive account insights and recommendations.""")
            ])
            
            chain = insights_prompt | self.llm
            insights = chain.invoke({
                "query": query,
                "history": json.dumps(history, indent=2),
                "patterns": json.dumps(patterns, indent=2),
                "rewards": json.dumps(rewards_info, indent=2) if rewards_info else "N/A"
            })
            
            account_intel_result = {
                "insights": insights.content,
                "transaction_summary": {
                    "total_transactions": history.get("total_transactions", 0),
                    "total_spending": sum(t.get("amount", 0) for t in history.get("transactions", [])),
                    "category_breakdown": patterns.get("category_breakdown", {})
                },
                "patterns": patterns,
                "rewards": rewards_info,
                "recommendations": []
            }
            
            # Extract recommendations
            if "travel" in query.lower():
                account_intel_result["recommendations"].append("Consider using points for travel to maximize value (1.5x multiplier)")
            if patterns.get("anomalies"):
                account_intel_result["recommendations"].append("Review unusual transactions for accuracy")
            
            state["account_intel_result"] = account_intel_result
            state["recommendations"] = state.get("recommendations", []) + account_intel_result["recommendations"]
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=f"Account Intelligence: {insights.content}")
            ]
        
        except Exception as e:
            error_msg = f"Account intel agent error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["account_intel_result"] = {"error": error_msg}
        
        return state

