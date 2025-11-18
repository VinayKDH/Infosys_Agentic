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

