"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class QueryRequest(BaseModel):
    """Request model for agent query"""
    query: str = Field(..., description="User query to process", min_length=1, max_length=2000)
    customer_id: str = Field(..., description="Customer ID")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    stream: bool = Field(False, description="Whether to stream the response")
    max_iterations: Optional[int] = Field(10, description="Maximum iterations for agent execution")


class QueryResponse(BaseModel):
    """Response model for agent query"""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    execution_time: float = Field(..., description="Execution time in seconds")
    request_id: str = Field(..., description="Request ID")
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


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str
    customer_id: str
    created_at: str
    message_count: int
    last_activity: Optional[str] = None

