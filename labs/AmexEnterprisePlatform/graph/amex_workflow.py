"""Main LangGraph workflow for Amex platform"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state.amex_state import AmexState
from agents.planner import PlannerAgent
from agents.support_agent import SupportAgent
from agents.fraud_agent import FraudAgent
from agents.account_intel_agent import AccountIntelAgent
from agents.compliance_agent import ComplianceAgent
from agents.reviewer_agent import ReviewerAgent
from langchain_core.messages import HumanMessage, AIMessage
from typing import Literal


class AmexWorkflow:
    """Main workflow orchestrating all agents"""
    
    def __init__(self):
        # Lazy initialization - agents will be created when needed
        self.planner = None
        self.support = None
        self.fraud = None
        self.account_intel = None
        self.compliance = None
        self.reviewer = None
        self.memory = MemorySaver()
        self.graph = None
        self._initialize_agents()
        self.graph = self._build_graph()
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            self.planner = PlannerAgent()
            self.support = SupportAgent()
            self.fraud = FraudAgent()
            self.account_intel = AccountIntelAgent()
            self.compliance = ComplianceAgent()
            self.reviewer = ReviewerAgent()
        except ValueError as e:
            # If API key is missing, agents will be None
            # This allows the workflow to be created but will fail when used
            print(f"Warning: Could not initialize agents: {e}")
            print("Agents will need to be initialized before use.")
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AmexState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("support", self._support_node)
        workflow.add_node("fraud", self._fraud_node)
        workflow.add_node("account_intel", self._account_intel_node)
        workflow.add_node("compliance", self._compliance_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("human_review", self._human_review_node)
        workflow.add_node("synthesize", self._synthesize_node)
        
        # Entry point
        workflow.add_edge(START, "planner")
        
        # Conditional routing from planner
        workflow.add_conditional_edges(
            "planner",
            self._route_after_planning,
            {
                "support": "support",
                "fraud": "fraud",
                "account_intel": "account_intel",
                "multi_agent": "support"  # Start with support for multi-agent
            }
        )
        
        # All agents route to compliance check
        workflow.add_edge("support", "compliance")
        workflow.add_edge("fraud", "compliance")
        workflow.add_edge("account_intel", "compliance")
        
        # Compliance routes to reviewer
        workflow.add_edge("compliance", "reviewer")
        
        # Reviewer routes conditionally
        workflow.add_conditional_edges(
            "reviewer",
            self._route_after_review,
            {
                "human_review": "human_review",
                "synthesize": "synthesize"
            }
        )
        
        # Human review routes back or to synthesize
        workflow.add_conditional_edges(
            "human_review",
            self._route_after_human_review,
            {
                "synthesize": "synthesize",
                "reviewer": "reviewer"
            }
        )
        
        # Synthesize to end
        workflow.add_edge("synthesize", END)
        
        # Compile with checkpoints
        return workflow.compile(checkpointer=self.memory)
    
    def _planner_node(self, state: AmexState) -> AmexState:
        """Planner node"""
        if self.planner is None:
            raise ValueError("Planner agent not initialized. Set OPENAI_API_KEY.")
        return self.planner.plan(state)
    
    def _support_node(self, state: AmexState) -> AmexState:
        """Support agent node"""
        if self.support is None:
            raise ValueError("Support agent not initialized. Set OPENAI_API_KEY.")
        return self.support.process(state)
    
    def _fraud_node(self, state: AmexState) -> AmexState:
        """Fraud agent node"""
        if self.fraud is None:
            raise ValueError("Fraud agent not initialized. Set OPENAI_API_KEY.")
        return self.fraud.process(state)
    
    def _account_intel_node(self, state: AmexState) -> AmexState:
        """Account intelligence agent node"""
        if self.account_intel is None:
            raise ValueError("Account intel agent not initialized. Set OPENAI_API_KEY.")
        return self.account_intel.process(state)
    
    def _compliance_node(self, state: AmexState) -> AmexState:
        """Compliance agent node"""
        if self.compliance is None:
            raise ValueError("Compliance agent not initialized. Set OPENAI_API_KEY.")
        return self.compliance.process(state)
    
    def _reviewer_node(self, state: AmexState) -> AmexState:
        """Reviewer agent node"""
        if self.reviewer is None:
            raise ValueError("Reviewer agent not initialized. Set OPENAI_API_KEY.")
        return self.reviewer.process(state)
    
    def _human_review_node(self, state: AmexState) -> AmexState:
        """Human review node (mock - in production, would pause for human input)"""
        # In production, this would use LangGraph interrupts
        state["human_approved"] = True  # Mock approval
        state["human_notes"] = "Approved by automated review system"
        state["messages"] = state.get("messages", []) + [
            AIMessage(content="Human review: Approved")
        ]
        return state
    
    def _synthesize_node(self, state: AmexState) -> AmexState:
        """Synthesize final response"""
        support_result = state.get("support_result", "")
        fraud_result = state.get("fraud_result")
        account_intel_result = state.get("account_intel_result")
        recommendations = state.get("recommendations", [])
        
        # Build final response
        response_parts = []
        
        if support_result:
            response_parts.append(f"Support Response: {support_result}")
        
        if fraud_result and isinstance(fraud_result, dict):
            analysis = fraud_result.get("analysis", "")
            if analysis:
                response_parts.append(f"Fraud Analysis: {analysis}")
        
        if account_intel_result and isinstance(account_intel_result, dict):
            insights = account_intel_result.get("insights", "")
            if insights:
                response_parts.append(f"Account Insights: {insights}")
        
        if recommendations:
            response_parts.append(f"Recommendations: {'; '.join(recommendations)}")
        
        final_response = "\n\n".join(response_parts) if response_parts else "Thank you for your inquiry. We're processing your request."
        
        state["final_response"] = final_response
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Final Response: {final_response}")
        ]
        
        return state
    
    def _route_after_planning(self, state: AmexState) -> Literal["support", "fraud", "account_intel", "multi_agent"]:
        """Route after planning"""
        request_type = state.get("request_type", "support")
        required_agents = state.get("required_agents", [])
        
        if len(required_agents) > 1:
            return "multi_agent"
        elif request_type == "fraud":
            return "fraud"
        elif request_type == "account":
            return "account_intel"
        else:
            return "support"
    
    def _route_after_review(self, state: AmexState) -> Literal["human_review", "synthesize"]:
        """Route after review"""
        if state.get("requires_human_review", False):
            return "human_review"
        return "synthesize"
    
    def _route_after_human_review(self, state: AmexState) -> Literal["synthesize", "reviewer"]:
        """Route after human review"""
        if state.get("human_approved", False):
            return "synthesize"
        return "reviewer"
    
    def invoke(self, state: AmexState, config: dict = None):
        """Invoke the workflow"""
        if config is None:
            config = {"configurable": {"thread_id": state.get("session_id", "default")}}
        return self.graph.invoke(state, config)
    
    def stream(self, state: AmexState, config: dict = None):
        """Stream workflow execution"""
        if config is None:
            config = {"configurable": {"thread_id": state.get("session_id", "default")}}
        return self.graph.stream(state, config)

