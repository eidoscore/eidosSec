"""WebSocket endpoints for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from jose import jwt, JWTError
from sqlalchemy import select
import uuid

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Project, Scan, User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websockets"])

@router.websocket("/ws/scans/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint for scan progress updates.
    """
    # Authentication is required for WebSockets.
    token = websocket.query_params.get("token")
    if not token:
        await websocket.accept()
        await websocket.send_json({"error": "Missing token"})
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise JWTError("Missing subject")
    except JWTError:
        await websocket.accept()
        await websocket.send_json({"error": "Invalid token"})
        await websocket.close(code=1008)
        return

    try:
        scan_uuid = uuid.UUID(scan_id)
    except ValueError:
        await websocket.accept()
        await websocket.send_json({"error": "Invalid scan id"})
        await websocket.close(code=1008)
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        current_user = result.scalar_one_or_none()
        if not current_user or not current_user.is_active:
            await websocket.accept()
            await websocket.send_json({"error": "Unauthorized"})
            await websocket.close(code=1008)
            return

        scan_result = await db.execute(select(Scan).where(Scan.id == scan_uuid))
        scan = scan_result.scalar_one_or_none()
        if not scan:
            await websocket.accept()
            await websocket.send_json({"error": "Scan not found"})
            await websocket.close(code=1008)
            return

        if current_user.role != "admin":
            project_result = await db.execute(select(Project).where(Project.id == scan.project_id))
            project = project_result.scalar_one_or_none()
            if not project or project.owner_id != current_user.id:
                await websocket.accept()
                await websocket.send_json({"error": "Unauthorized"})
                await websocket.close(code=1008)
                return

    await websocket.accept()

    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()
    channel = f"scan:{scan_id}:progress"
    
    try:
        await pubsub.subscribe(channel)
        logger.info(f"Subscribed to Redis channel: {channel}")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                # data is already string due to decode_responses=True
                await websocket.send_text(data)
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from scan {scan_id}")
    except Exception as e:
        logger.error(f"WebSocket error for scan {scan_id}: {str(e)}")
    finally:
        # Cleanup
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await redis_client.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")
