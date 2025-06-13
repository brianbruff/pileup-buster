"""WebSocket connection manager for real-time notifications"""
import json
import logging
from typing import Dict, Any, List
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts events"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection removed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
    
    def broadcast_sync(self, message: Dict[str, Any]):
        """Synchronous wrapper for broadcasting (for use in non-async contexts)"""
        if not self.active_connections:
            return
        
        try:
            # Create a new event loop if none exists
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, we're likely in a sync context
            # We'll need to create a task for the async operation
            asyncio.create_task(self.broadcast(message))
            return
        
        # If there's already an event loop running, schedule the broadcast
        if loop.is_running():
            asyncio.create_task(self.broadcast(message))
        else:
            loop.run_until_complete(self.broadcast(message))
    
    def create_event_message(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized event message"""
        return {
            "type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data
        }
    
    # Event broadcasting methods for different database operations
    def broadcast_queue_update(self, action: str, callsign: str = None, queue_data: Dict[str, Any] = None):
        """Broadcast queue-related events"""
        event_data = {
            "action": action,  # "add", "remove", "clear", "reorder"
        }
        
        if callsign:
            event_data["callsign"] = callsign
        
        if queue_data:
            event_data.update(queue_data)
        
        message = self.create_event_message("queue_update", event_data)
        self.broadcast_sync(message)
    
    def broadcast_qso_update(self, action: str, callsign: str = None, qso_data: Dict[str, Any] = None):
        """Broadcast QSO-related events"""
        event_data = {
            "action": action,  # "start", "end", "next"
        }
        
        if callsign:
            event_data["callsign"] = callsign
        
        if qso_data:
            event_data.update(qso_data)
        
        message = self.create_event_message("qso_update", event_data)
        self.broadcast_sync(message)
    
    def broadcast_system_status_update(self, active: bool, updated_by: str, additional_data: Dict[str, Any] = None):
        """Broadcast system status changes"""
        event_data = {
            "active": active,
            "updated_by": updated_by
        }
        
        if additional_data:
            event_data.update(additional_data)
        
        message = self.create_event_message("system_status_update", event_data)
        self.broadcast_sync(message)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()