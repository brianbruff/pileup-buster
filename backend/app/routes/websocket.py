"""WebSocket routes for real-time notifications"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import websocket_manager
import logging

logger = logging.getLogger(__name__)

websocket_router = APIRouter()


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications"""
    await websocket_manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket_manager.send_personal_message(
            '{"type": "connection", "status": "connected", "message": "Connected to Pileup Buster notifications"}',
            websocket
        )
        
        # Keep the connection alive and handle incoming messages
        while True:
            # Wait for any message from client (could be ping/heartbeat)
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message: {data}")
                
                # Echo back as heartbeat response
                await websocket_manager.send_personal_message(
                    '{"type": "heartbeat", "status": "ok"}',
                    websocket
                )
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket)