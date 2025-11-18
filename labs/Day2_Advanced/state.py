from typing import TypedDict, List, Annotated, Optional, Dict, Any
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime
from enum import Enum

class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class Task(TypedDict):
    id: str
    description: str
    assigned_to: AgentRole
    status: TaskStatus
    result: Optional[str]
    dependencies: List[str]
    created_at: str
    completed_at: Optional[str]

class MultiAgentState(TypedDict):
    """Advanced state schema for multi-agent system"""
    # Messages
    messages: Annotated[List[BaseMessage], operator.add]
    
    # User query
    original_query: str
    
    # Planning
    plan: Optional[Dict[str, Any]]
    tasks: Annotated[List[Task], operator.add]
    current_task_id: Optional[str]
    
    # Research
    research_findings: Annotated[List[Dict[str, str]], operator.add]
    
    # Code
    code_artifacts: Annotated[List[Dict[str, str]], operator.add]
    
    # Review
    review_feedback: Annotated[List[Dict[str, str]], operator.add]
    
    # Final output
    final_output: str
    
    # Metadata
    iteration_count: int
    agent_history: Annotated[List[Dict[str, Any]], operator.add]
    errors: Annotated[List[str], operator.add]
    requires_human_input: bool
    human_feedback: Optional[str]

