from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class ResearchState(TypedDict):
    """State schema for the research graph"""
    messages: Annotated[List[BaseMessage], operator.add]
    research_results: str
    final_answer: str
    query: str
    iteration_count: int

