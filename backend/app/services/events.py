"""
Server-Sent Events (SSE) service for real-time notifications
"""
import json
import asyncio
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of events that can be broadcast"""
    CURRENT_QSO = "current_qso"
    QUEUE_UPDATE = "queue_update"
    SYSTEM_STATUS = "system_status"


class EventBroadcaster:
    """Manages Server-Sent Event connections and broadcasts"""
    
    def __init__(self):
        self._connections: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()
    
    async def add_connection(self, queue: asyncio.Queue):
        """Add a new SSE connection"""
        async with self._lock:
            self._connections.add(queue)
            logger.info(f"Added SSE connection. Total connections: {len(self._connections)}")
    
    async def remove_connection(self, queue: asyncio.Queue):
        """Remove an SSE connection"""
        async with self._lock:
            self._connections.discard(queue)
            logger.info(f"Removed SSE connection. Total connections: {len(self._connections)}")
    
    async def broadcast_event(self, event_type: EventType, data: Any):
        """Broadcast an event to all connected clients"""
        if not self._connections:
            logger.debug(f"No SSE connections to broadcast {event_type} event")
            return
        
        event_data = {
            "type": event_type.value,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Format as SSE message
        sse_message = f"event: {event_type.value}\ndata: {json.dumps(event_data)}\n\n"
        
        # Send to all connections
        async with self._lock:
            disconnected = set()
            for connection_queue in self._connections:
                try:
                    await connection_queue.put(sse_message)
                except Exception as e:
                    logger.warning(f"Failed to send event to connection: {e}")
                    disconnected.add(connection_queue)
            
            # Clean up disconnected connections
            for queue in disconnected:
                self._connections.discard(queue)
        
        logger.info(f"Broadcasted {event_type} event to {len(self._connections)} connections")
    
    async def broadcast_current_qso(self, current_qso: Optional[Dict[str, Any]]):
        """Broadcast current QSO change event"""
        await self.broadcast_event(EventType.CURRENT_QSO, current_qso)
    
    async def broadcast_queue_update(self, queue_data: Dict[str, Any]):
        """Broadcast queue update event"""
        await self.broadcast_event(EventType.QUEUE_UPDATE, queue_data)
    
    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status change event"""
        await self.broadcast_event(EventType.SYSTEM_STATUS, status)


# Global event broadcaster instance
event_broadcaster = EventBroadcaster()