"""
State definition for Customer Support Email Agent
Based on LangGraph thinking patterns
"""
from typing import TypedDict, Literal, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage
import operator
from typing import Annotated

# Define the structure for email classification
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    """State schema for the email support agent"""
    # Raw email data
    email_content: str
    sender_email: str
    email_id: str
    
    # Classification result
    classification: Optional[EmailClassification]
    
    # Raw search/API results
    search_results: Optional[List[str]]  # List of raw document chunks
    customer_history: Optional[Dict[str, Any]]  # Raw customer data from CRM
    bug_ticket_id: Optional[str]  # Ticket ID if bug was created
    
    # Generated content
    draft_response: Optional[str]
    final_response: Optional[str]
    
    # Messages for conversation tracking
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Human review
    requires_human_review: bool
    human_approved: Optional[bool]
    human_edited_response: Optional[str]
    
    # Execution metadata
    errors: Annotated[List[str], operator.add]

