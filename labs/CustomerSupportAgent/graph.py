"""
LangGraph workflow for Customer Support Email Agent
Based on LangGraph thinking patterns
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import EmailAgentState
from nodes import (
    read_email,
    classify_intent,
    route_after_classify,
    doc_search,
    bug_tracking,
    draft_response,
    human_review,
    send_reply
)

def create_email_agent_graph(enable_checkpoints: bool = True):
    """Create and compile the email support agent graph"""
    
    # Create the graph
    workflow = StateGraph(EmailAgentState)
    
    # Add nodes
    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("doc_search", doc_search)
    workflow.add_node("bug_tracking", bug_tracking)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("send_reply", send_reply)
    
    # Add edges
    workflow.add_edge(START, "read_email")
    workflow.add_edge("read_email", "classify_intent")
    
    # Conditional edges from classify_intent
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {
            "doc_search": "doc_search",
            "bug_tracking": "bug_tracking",
            "human_review": "human_review",
            "draft_response": "draft_response"
        }
    )
    
    # Edges from doc_search and bug_tracking
    workflow.add_edge("doc_search", "draft_response")
    workflow.add_edge("bug_tracking", "draft_response")
    
    # Edge from draft_response to human_review
    workflow.add_edge("draft_response", "human_review")
    
    # Edge from human_review to send_reply
    workflow.add_edge("human_review", "send_reply")
    
    # Final edge
    workflow.add_edge("send_reply", END)
    
    # Compile with checkpoints if enabled
    if enable_checkpoints:
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    else:
        return workflow.compile()

