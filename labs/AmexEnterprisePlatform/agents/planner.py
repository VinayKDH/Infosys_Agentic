"""Planner agent for routing requests"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from state.amex_state import AmexState
from app.config import settings
from typing import List


class PlannerAgent:
    """Plans execution strategy for incoming requests"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
    
    def plan(self, state: AmexState) -> AmexState:
        """Analyze request and create execution plan"""
        query = state.get("original_query", "")
        request_type = state.get("request_type", "support")
        
        # Classification prompt
        classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a planning agent for a banking customer support system.
            Analyze the customer query and determine:
            1. Request type: support, fraud, account, compliance, or multi
            2. Required agents: support, fraud, account_intel, compliance
            3. Priority: low, medium, high, or critical
            4. Execution plan: step-by-step plan
            
            Respond in JSON format with keys: request_type, required_agents (list), priority, execution_plan."""),
            ("human", "Query: {query}")
        ])
        
        chain = classification_prompt | self.llm
        response = chain.invoke({"query": query})
        
        # Parse response (simplified - in production, use structured output)
        content = response.content
        
        # Extract information (simplified parsing)
        if "fraud" in content.lower() or "unauthorized" in content.lower() or "stolen" in content.lower():
            request_type = "fraud"
            required_agents = ["fraud", "compliance"]
            priority = "high"
        elif "spending" in content.lower() or "rewards" in content.lower() or "insights" in content.lower():
            request_type = "account"
            required_agents = ["account_intel", "compliance"]
            priority = "medium"
        elif "dispute" in content.lower() or "charge" in content.lower():
            request_type = "multi"
            required_agents = ["support", "fraud", "compliance"]
            priority = "high"
        else:
            request_type = "support"
            required_agents = ["support", "compliance"]
            priority = "medium"
        
        execution_plan = f"""
        1. Classify request as: {request_type}
        2. Route to agents: {', '.join(required_agents)}
        3. Execute agent workflows
        4. Run compliance check
        5. Review results
        6. Generate final response
        """
        
        state["request_type"] = request_type
        state["required_agents"] = required_agents
        state["priority"] = priority
        state["execution_plan"] = execution_plan
        
        # Add message
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Planned execution: {execution_plan}")
        ]
        
        return state

