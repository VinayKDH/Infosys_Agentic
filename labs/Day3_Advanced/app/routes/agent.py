from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse
from app.agent_service import agent_service

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Process a query through the agent system"""
    try:
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

