"""WebSocket endpoints for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websockets"])

@router.websocket("/ws/scans/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint for scan progress updates.
    Connects to Redis Pub/Sub and streams messages to client.
    """
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
