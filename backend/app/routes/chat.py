"""
Chat API endpoints for real-time messaging
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from app.database import queue_db
from app.services.events import event_broadcaster
from app.auth import verify_admin_credentials
from app.validation import validate_callsign
import logging

logger = logging.getLogger(__name__)

chat_router = APIRouter()


class ChatMessage(BaseModel):
    callsign: str
    message: str
    room_name: str = "general"
    
    @validator('callsign')
    def validate_callsign(cls, v):
        if not validate_callsign(v):
            raise ValueError('Invalid callsign format')
        return v.upper()
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 500:
            raise ValueError('Message too long (max 500 characters)')
        return v.strip()
    
    @validator('room_name')
    def validate_room_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Room name cannot be empty')
        if len(v) > 50:
            raise ValueError('Room name too long (max 50 characters)')
        # Only allow alphanumeric, hyphens, and underscores
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Room name can only contain letters, numbers, hyphens, and underscores')
        return v.strip().lower()


class ChatRoom(BaseModel):
    name: str
    description: str = ""
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Room name cannot be empty')
        if len(v) > 50:
            raise ValueError('Room name too long (max 50 characters)')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Room name can only contain letters, numbers, hyphens, and underscores')
        return v.strip().lower()
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) > 200:
            raise ValueError('Description too long (max 200 characters)')
        return v.strip()


class DeleteMessageRequest(BaseModel):
    room_name: str
    message_timestamp: str


@chat_router.get("/rooms")
async def get_chat_rooms():
    """Get list of available chat rooms"""
    try:
        rooms = queue_db.get_chat_rooms()
        return {"rooms": rooms}
    except Exception as e:
        logger.error(f"Failed to get chat rooms: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat rooms")


@chat_router.post("/rooms")
async def create_chat_room(room: ChatRoom, admin: str = Depends(verify_admin_credentials)):
    """Create a new chat room (admin only)"""
    try:
        room_data = queue_db.create_chat_room(
            room_name=room.name,
            description=room.description,
            created_by=admin
        )
        
        # Broadcast room update event
        await event_broadcaster.broadcast_chat_room_update({
            "action": "created",
            "room": room_data
        })
        
        return room_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create chat room: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat room")


@chat_router.get("/rooms/{room_name}/messages")
async def get_chat_messages(room_name: str, limit: int = 50, skip: int = 0):
    """Get messages from a chat room"""
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    if skip < 0:
        skip = 0
    
    try:
        messages = queue_db.get_chat_messages(
            room_name=room_name.lower(),
            limit=limit,
            skip=skip
        )
        return {"messages": messages, "room_name": room_name.lower()}
    except Exception as e:
        logger.error(f"Failed to get chat messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve messages")


@chat_router.post("/messages")
async def send_chat_message(message: ChatMessage):
    """Send a message to a chat room"""
    try:
        # Send message to database
        message_data = queue_db.send_chat_message(
            room_name=message.room_name,
            callsign=message.callsign,
            message=message.message
        )
        
        # Broadcast message event to all connected clients
        await event_broadcaster.broadcast_chat_message(message_data)
        
        return message_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@chat_router.delete("/messages")
async def delete_chat_message(
    delete_request: DeleteMessageRequest,
    admin: str = Depends(verify_admin_credentials)
):
    """Delete a chat message (admin only)"""
    try:
        success = queue_db.delete_chat_message(
            room_name=delete_request.room_name.lower(),
            message_timestamp=delete_request.message_timestamp,
            deleted_by=admin
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Broadcast message deletion event
        await event_broadcaster.broadcast_chat_message({
            "room_name": delete_request.room_name.lower(),
            "message_type": "deleted",
            "timestamp": delete_request.message_timestamp,
            "deleted_by": admin
        })
        
        return {"success": True, "message": "Message deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete message")


@chat_router.delete("/rooms/{room_name}/clear")
async def clear_chat_room(room_name: str, admin: str = Depends(verify_admin_credentials)):
    """Clear all messages in a chat room (admin only)"""
    try:
        count = queue_db.clear_chat_room(
            room_name=room_name.lower(),
            cleared_by=admin
        )
        
        # Broadcast room clear event
        await event_broadcaster.broadcast_chat_room_update({
            "action": "cleared",
            "room_name": room_name.lower(),
            "cleared_by": admin,
            "message_count": count
        })
        
        return {"success": True, "message": f"Cleared {count} messages from {room_name}"}
        
    except Exception as e:
        logger.error(f"Failed to clear chat room: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear chat room")


# Initialize default chat rooms when the module is imported
def initialize_default_chat_rooms():
    """Create default chat rooms if they don't exist"""
    try:
        existing_rooms = queue_db.get_chat_rooms()
        room_names = [room["name"] for room in existing_rooms]
        
        # Create general room if it doesn't exist
        if "general" not in room_names:
            queue_db.create_chat_room(
                room_name="general",
                description="General chat for all operators",
                created_by="system"
            )
            logger.info("Created default 'general' chat room")
        
        # Create pileup room if it doesn't exist  
        if "pileup" not in room_names:
            queue_db.create_chat_room(
                room_name="pileup",
                description="Chat room for operators in the pileup queue",
                created_by="system"
            )
            logger.info("Created default 'pileup' chat room")
            
    except Exception as e:
        logger.warning(f"Failed to initialize default chat rooms: {e}")


# Initialize default rooms when the module loads
try:
    initialize_default_chat_rooms()
except Exception as e:
    logger.warning(f"Could not initialize default chat rooms on startup: {e}")