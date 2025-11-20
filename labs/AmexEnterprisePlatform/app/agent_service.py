"""Agent service for orchestrating workflows"""
from graph.amex_workflow import AmexWorkflow
from state.amex_state import AmexState
from langchain_core.messages import HumanMessage
from typing import Dict, Any, AsyncIterator
import time
import uuid
from datetime import datetime
from app.monitoring import agent_executions, agent_duration


class AgentService:
    """Service for executing agent workflows"""
    
    def __init__(self):
        self.workflow = AmexWorkflow()
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    async def process_query(
        self,
        query: str,
        customer_id: str,
        session_id: str = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """Process a user query through the agent system"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize or retrieve session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "message_count": 0,
                "customer_id": customer_id
            }
        
        # Prepare initial state
        initial_state: AmexState = {
            "customer_id": customer_id,
            "request_id": request_id,
            "request_type": "support",
            "original_query": query,
            "session_id": session_id,
            "execution_plan": None,
            "required_agents": [],
            "priority": "medium",
            "support_result": None,
            "fraud_result": None,
            "account_intel_result": None,
            "compliance_result": None,
            "transactions": [],
            "risk_scores": [],
            "compliance_checks": [],
            "compliance_status": None,
            "requires_human_review": False,
            "human_approved": None,
            "human_notes": None,
            "final_response": None,
            "recommendations": [],
            "messages": [HumanMessage(content=query)],
            "errors": []
        }
        
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            # Track agent execution
            with agent_duration.labels(agent_type="workflow").time():
                # Execute workflow
                result = self.workflow.invoke(initial_state, config)
                
                execution_time = time.time() - start_time
                
                # Update session
                self.sessions[session_id]["message_count"] += 1
                self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
                
                # Track metrics
                agent_executions.labels(agent_type="workflow", status="success").inc()
                
                return {
                    "response": result.get("final_response", "No response generated"),
                    "session_id": session_id,
                    "execution_time": execution_time,
                    "request_id": request_id,
                    "metadata": {
                        "message_count": self.sessions[session_id]["message_count"],
                        "request_type": result.get("request_type"),
                        "priority": result.get("priority"),
                        "compliance_status": result.get("compliance_status"),
                        "requires_human_review": result.get("requires_human_review", False)
                    }
                }
        
        except Exception as e:
            execution_time = time.time() - start_time
            agent_executions.labels(agent_type="workflow", status="error").inc()
            raise Exception(f"Agent execution failed: {str(e)}")
    
    async def stream_query(
        self,
        query: str,
        customer_id: str,
        session_id: str = None
    ) -> AsyncIterator[str]:
        """Stream agent response"""
        import asyncio
        
        config = {"configurable": {"thread_id": session_id or str(uuid.uuid4())}}
        
        initial_state: AmexState = {
            "customer_id": customer_id,
            "request_id": str(uuid.uuid4()),
            "request_type": "support",
            "original_query": query,
            "session_id": session_id or str(uuid.uuid4()),
            "execution_plan": None,
            "required_agents": [],
            "priority": "medium",
            "support_result": None,
            "fraud_result": None,
            "account_intel_result": None,
            "compliance_result": None,
            "transactions": [],
            "risk_scores": [],
            "compliance_checks": [],
            "compliance_status": None,
            "requires_human_review": False,
            "human_approved": None,
            "human_notes": None,
            "final_response": None,
            "recommendations": [],
            "messages": [HumanMessage(content=query)],
            "errors": []
        }
        
        # Stream workflow execution
        for event in self.workflow.stream(initial_state, config):
            # Yield progress updates
            for node_name, node_state in event.items():
                yield f"Processing {node_name}...\n"
                await asyncio.sleep(0.1)
        
        # Get final result
        result = self.workflow.invoke(initial_state, config)
        response = result.get("final_response", "")
        
        # Yield response word by word
        words = response.split()
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            await asyncio.sleep(0.05)
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        return self.sessions[session_id]
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Global agent service instance
agent_service = AgentService()

