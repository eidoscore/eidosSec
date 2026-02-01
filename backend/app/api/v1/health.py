"""Health check endpoint"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import redis.asyncio as redis

from app.database import get_db
from app.config import settings
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    
    Checks:
    - API is running
    - Database connectivity
    - Redis connectivity
    """
    # Check database
    db_status = "disconnected"
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Redis
    redis_status = "disconnected"
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        redis_status = "connected"
        await r.close()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    # Overall status
    overall_status = "healthy" if (db_status == "connected" and redis_status == "connected") else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        timestamp=datetime.utcnow()
    )
