from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import Dict, Any, TypedDict, Annotated, List
import operator
import os
import time
import uuid
from datetime import datetime

# Proper state definition for LangGraph
class AgentState(TypedDict):
    """State schema for the agent graph"""
    messages: Annotated[List[BaseMessage], operator.add]
    query: str
    response: str

class AgentService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._agent_node)
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)
        return workflow.compile(checkpointer=self.memory)
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent processing node"""
        messages = state.get("messages", [])
        user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
        
        if not user_message:
            user_message = state.get("query", "")
        
        response = self.llm.invoke(f"User asked: {user_message}. Provide a helpful response.")
        
        # Return updated state - LangGraph will merge this with existing state
        return {
            "messages": [AIMessage(content=response.content)],
            "query": state.get("query", user_message),
            "response": response.content
        }
    
    async def process_query(self, query: str, session_id: str = None, max_iterations: int = 10) -> Dict[str, Any]:
        start_time = time.time()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
        
        config = {"configurable": {"thread_id": session_id}}
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "response": ""
        }
        
        try:
            result = self.graph.invoke(initial_state, config)
            execution_time = time.time() - start_time
            
            self.sessions[session_id]["message_count"] += 1
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            
            return {
                "response": result.get("response", ""),
                "session_id": session_id,
                "execution_time": execution_time,
                "metadata": {
                    "message_count": self.sessions[session_id]["message_count"],
                    "iterations": 1
                }
            }
        except Exception as e:
            raise Exception(f"Agent execution failed: {str(e)}")

# Global agent service instance (lazy initialization)
agent_service = None

def get_agent_service():
    """Get or create agent service instance"""
    global agent_service
    if agent_service is None:
        agent_service = AgentService()
    return agent_service

