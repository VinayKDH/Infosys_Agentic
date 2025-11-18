from fastapi import APIRouter
from fastapi.responses import Response
from app.monitoring import get_metrics

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=get_metrics(),
        media_type="text/plain"
    )

