from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    stream: bool = False
    max_iterations: Optional[int] = 10

class QueryResponse(BaseModel):
    response: str
    session_id: str
    execution_time: float
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

