"""Customer support routes"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models import QueryRequest, QueryResponse, StreamChunk, ErrorResponse
from app.agent_service import agent_service
from app.auth import get_current_active_user
from app.cache import cache_service
from app.monitoring import cache_hits, cache_misses
import json
import uuid

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_agent(
    request: QueryRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Process a customer support query"""
    try:
        # Check cache
        cache_key = f"query:{request.customer_id}:{request.query}"
        cached_result = cache_service.get("query", customer_id=request.customer_id, query=request.query)
        
        if cached_result:
            cache_hits.labels(operation="query").inc()
            return QueryResponse(**cached_result)
        
        cache_misses.labels(operation="query").inc()
        
        # Process query
        result = await agent_service.process_query(
            query=request.query,
            customer_id=request.customer_id,
            session_id=request.session_id,
            max_iterations=request.max_iterations
        )
        
        # Cache result
        cache_service.set("query", result, ttl=300, customer_id=request.customer_id, query=request.query)
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/query/stream")
async def stream_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Stream agent response in real-time"""
    try:
        async def generate():
            async for chunk in agent_service.stream_query(
                query=request.query,
                customer_id=request.customer_id,
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
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get session information"""
    info = agent_service.get_session_info(session_id)
    
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    
    return info


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a session"""
    success = agent_service.clear_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

