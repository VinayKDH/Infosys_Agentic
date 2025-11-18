# Day 3 - Medium Level Lab: Deploying AI Agent as FastAPI Service

## Lab Overview
**Duration:** 90 minutes  
**Objective:** Deploy your multi-agent system as a production-ready FastAPI service with async endpoints, streaming responses, and basic error handling.

## Prerequisites
- Completed Day 1 and Day 2 labs
- Understanding of REST APIs
- Basic knowledge of FastAPI

## Learning Outcomes
By the end of this lab, you will:
- Integrate LangGraph/LangChain with FastAPI
- Create async API endpoints for agent execution
- Implement streaming responses for real-time updates
- Handle concurrent user sessions
- Add basic error handling and validation
- Deploy the service locally

## Lab Setup

### Step 1: Environment Setup
```bash
pip install fastapi uvicorn[standard]
pip install langchain langchain-openai langgraph
pip install pydantic python-multipart
pip install python-dotenv
```

### Step 2: Project Structure
```
day3_medium_lab/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── agent_service.py
│   └── routes/
│       ├── __init__.py
│       └── agent.py
├── .env
├── requirements.txt
└── README.md
```

## Lab Implementation

### Part 1: FastAPI Application Setup (20 minutes)

**File: `app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.agent import router as agent_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Agentic AI API",
    description="FastAPI service for multi-agent AI system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router, prefix="/api/v1", tags=["agent"])

@app.get("/")
async def root():
    return {
        "message": "Agentic AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**File: `app/models.py`**
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

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
```

### Part 2: Agent Service Integration (30 minutes)

**File: `app/agent_service.py`**
```python
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, AsyncIterator
import os
import time
import uuid
from datetime import datetime

# Simple state for this example
class AgentState(dict):
    pass

class AgentService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def _build_graph(self):
        """Build a simple agent graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        
        # Set entry point and edges
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)
        
        # Compile with checkpoints
        return workflow.compile(checkpointer=self.memory)
    
    def _agent_node(self, state: AgentState):
        """Agent processing node"""
        messages = state.get("messages", [])
        
        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
        
        if not user_message:
            user_message = state.get("query", "")
        
        # Simple agent response (replace with your actual agent logic)
        response = self.llm.invoke(f"User asked: {user_message}. Provide a helpful response.")
        
        state["messages"] = state.get("messages", []) + [AIMessage(content=response.content)]
        state["response"] = response.content
        
        return state
    
    async def process_query(
        self, 
        query: str, 
        session_id: str = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """Process a user query"""
        start_time = time.time()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize or retrieve session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
        
        # Prepare state
        config = {"configurable": {"thread_id": session_id}}
        
        # Get existing messages from session
        existing_messages = []
        # In a real implementation, you'd load from checkpoints
        
        initial_state = {
            "messages": existing_messages + [HumanMessage(content=query)],
            "query": query
        }
        
        try:
            # Execute graph
            result = self.graph.invoke(initial_state, config)
            
            execution_time = time.time() - start_time
            
            # Update session
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
    
    async def stream_query(
        self,
        query: str,
        session_id: str = None
    ) -> AsyncIterator[str]:
        """Stream agent response"""
        # For streaming, we'll yield chunks as they're generated
        # This is a simplified version - in production, you'd stream from the agent
        
        config = {"configurable": {"thread_id": session_id or str(uuid.uuid4())}}
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "query": query
        }
        
        # Stream response word by word (simplified)
        result = self.graph.invoke(initial_state, config)
        response = result.get("response", "")
        
        # Yield chunks
        words = response.split()
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            
            # Small delay to simulate streaming
            import asyncio
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
```

### Part 3: API Routes (25 minutes)

**File: `app/routes/agent.py`**
```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.models import QueryRequest, QueryResponse, StreamChunk, ErrorResponse
from app.agent_service import agent_service
import json
import asyncio

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Process a query through the agent system.
    
    - **query**: User's question or request
    - **session_id**: Optional session ID for conversation continuity
    - **stream**: Whether to stream the response (not implemented in basic version)
    - **max_iterations**: Maximum agent iterations
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=400,
                detail="Streaming not supported via this endpoint. Use /query/stream instead."
            )
        
        result = await agent_service.process_query(
            query=request.query,
            session_id=request.session_id,
            max_iterations=request.max_iterations
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/query/stream")
async def stream_query(request: QueryRequest):
    """
    Stream agent response in real-time.
    
    Returns Server-Sent Events (SSE) stream.
    """
    try:
        async def generate():
            async for chunk in agent_service.stream_query(
                query=request.query,
                session_id=request.session_id
            ):
                chunk_data = StreamChunk(
                    chunk=chunk,
                    done=False
                )
                yield f"data: {chunk_data.model_dump_json()}\n\n"
            
            # Send final chunk
            final_chunk = StreamChunk(
                chunk="",
                done=True,
                metadata={"session_id": request.session_id or "new"}
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error streaming query: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get information about a session"""
    info = agent_service.get_session_info(session_id)
    
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    
    return info

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = agent_service.clear_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

@router.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "sessions": list(agent_service.sessions.keys()),
        "count": len(agent_service.sessions)
    }
```

### Part 4: Running and Testing (15 minutes)

**File: `requirements.txt`**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.1.0
langchain-openai==0.0.5
langgraph==0.0.20
pydantic==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
```

**Running the service:**
```bash
# Activate virtual environment
source agentic_ai_env/bin/activate

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Testing with curl:**
```bash
# Health check
curl http://localhost:8000/health

# Query endpoint
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "stream": false}'

# Stream endpoint
curl -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain AI in simple terms"}'

# Get session info
curl http://localhost:8000/api/v1/session/{session_id}
```

**Testing with Python:**
```python
import requests
import json

# Query endpoint
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "What is FastAPI?",
        "stream": False
    }
)
print(json.dumps(response.json(), indent=2))

# Stream endpoint
response = requests.post(
    "http://localhost:8000/api/v1/query/stream",
    json={"query": "Tell me about Python"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## Lab Exercises

### Exercise 1: Add Request Validation (15 minutes)
- Add input sanitization
- Validate query length and content
- Add rate limiting per session
- Implement request timeout handling

### Exercise 2: Error Handling Enhancement (15 minutes)
- Add try-catch blocks for all endpoints
- Create custom exception handlers
- Add logging for errors
- Return user-friendly error messages

### Exercise 3: Background Tasks (15 minutes)
- Implement long-running queries as background tasks
- Add task status endpoint
- Store task results
- Allow querying task status

### Exercise 4: API Documentation (10 minutes)
- Add detailed docstrings
- Include example requests/responses
- Add OpenAPI tags and descriptions
- Test the interactive docs at `/docs`

## Testing Checklist

- [ ] Health check endpoint works
- [ ] Query endpoint processes requests
- [ ] Streaming endpoint returns chunks
- [ ] Session management works
- [ ] Error handling returns proper status codes
- [ ] API documentation is accessible at `/docs`
- [ ] Concurrent requests are handled
- [ ] Memory is managed properly

## Deliverables

1. Complete FastAPI application with:
   - All endpoints implemented
   - Error handling
   - Basic validation

2. Test script with:
   - Unit tests for endpoints
   - Integration tests
   - Performance tests

3. API documentation:
   - OpenAPI/Swagger docs
   - Postman collection (optional)
   - Usage examples

4. Deployment guide:
   - Local setup instructions
   - Environment configuration
   - Running instructions

## Troubleshooting

**Issue:** "Module not found" errors
- Solution: Ensure all dependencies are installed and virtual environment is activated

**Issue:** Port already in use
- Solution: Change port in uvicorn command or kill existing process

**Issue:** Streaming not working
- Solution: Check that client supports Server-Sent Events (SSE)

**Issue:** Session not persisting
- Solution: Verify checkpoint configuration and memory saver setup

## Next Steps

After completing this lab:
- Add authentication and authorization
- Implement rate limiting
- Add monitoring and logging
- Prepare for production deployment (Day 3 Advanced Lab)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Uvicorn Documentation](https://www.uvicorn.org/)

