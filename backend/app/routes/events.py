"""
Server-Sent Events (SSE) endpoints for real-time notifications
"""
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.events import event_broadcaster
import logging

logger = logging.getLogger(__name__)

events_router = APIRouter()


@events_router.get('/stream')
async def events_stream():
    """Server-Sent Events endpoint for real-time notifications"""
    
    async def event_generator():
        # Create a queue for this connection
        connection_queue = asyncio.Queue()
        
        try:
            # Register this connection
            await event_broadcaster.add_connection(connection_queue)
            
            # Send initial connection message
            yield "event: connected\ndata: {\"message\": \"SSE connection established\"}\n\n"
            
            # Stream events
            while True:
                try:
                    # Wait for an event (with timeout to send keepalive)
                    event_data = await asyncio.wait_for(
                        connection_queue.get(), 
                        timeout=30.0  # 30 second keepalive
                    )
                    yield event_data
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield "event: keepalive\ndata: {}\n\n"
                except Exception as e:
                    logger.error(f"Error in SSE stream: {e}")
                    break
        
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
        finally:
            # Cleanup connection
            await event_broadcaster.remove_connection(connection_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )