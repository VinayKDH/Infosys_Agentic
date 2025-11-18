from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    """Request model for agent query"""
    query: str = Field(..., description="User query to process", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    stream: bool = Field(False, description="Whether to stream the response")
    max_iterations: Optional[int] = Field(10, description="Maximum iterations for agent execution")

class QueryResponse(BaseModel):
    """Response model for agent query"""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    execution_time: float = Field(..., description="Execution time in seconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class StreamChunk(BaseModel):
    """Model for streaming response chunks"""
    chunk: str = Field(..., description="Response chunk")
    done: bool = Field(False, description="Whether this is the final chunk")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Chunk metadata")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")

