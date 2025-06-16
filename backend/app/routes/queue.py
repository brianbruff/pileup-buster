from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any
from app.services.qrz import qrz_service
from app.database import queue_db
from app.validation import validate_callsign
from app.services.events import event_broadcaster
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

queue_router = APIRouter()

@queue_router.get('/status')
def get_public_system_status():
    """Get the current system status (active/inactive) - public endpoint"""
    try:
        status = queue_db.get_system_status()
        # Return only the active status for public consumption
        # Exclude sensitive information like updated_by (admin usernames)
        return {
            'active': status.get('active', False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

class CallsignRequest(BaseModel):
    callsign: str

class QueueEntry(BaseModel):
    callsign: str
    timestamp: str
    position: int

@queue_router.post('/register')
async def register_callsign(request: CallsignRequest):
    """Register a callsign in the queue"""
    callsign = request.callsign.upper().strip()
    
    if not callsign:
        raise HTTPException(status_code=400, detail='Callsign is required')
    
    if not validate_callsign(callsign):
        raise HTTPException(status_code=400, detail='Invalid callsign format. Must follow ITU standards (e.g., KC1ABC, W1AW)')
    
    try:
        # Check if system is active before allowing registration
        system_status = queue_db.get_system_status()
        if not system_status.get('active', False):
            raise HTTPException(status_code=503, detail='System is currently inactive. Registration is not available.')
        
        # Fetch QRZ information at registration time
        qrz_info = qrz_service.lookup_callsign(callsign)
        
        # Register callsign with QRZ information
        entry = queue_db.register_callsign(callsign, qrz_info)
        
        # Broadcast updated queue
        try:
            queue_list = queue_db.get_queue_list()
            max_queue_size = int(os.getenv('MAX_QUEUE_SIZE', '4'))
            await event_broadcaster.broadcast_queue_update({
                'queue': queue_list, 
                'total': len(queue_list), 
                'max_size': max_queue_size,
                'system_active': True
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast queue update event: {e}")
        
        return {'message': 'Callsign registered successfully', 'entry': entry}
    except HTTPException:
        raise  # Re-raise HTTP exceptions (like system inactive)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to register callsign: {e}")
        raise HTTPException(status_code=500, detail='Failed to register callsign')

@queue_router.get('/status/{callsign}')
def get_status(callsign: str):
    """Get position of callsign in queue with stored QRZ.com profile information"""
    callsign = callsign.upper().strip()
    
    try:
        # Check if system is active
        system_status = queue_db.get_system_status()
        if not system_status.get('active', False):
            raise HTTPException(status_code=503, detail='System is currently inactive.')
        
        entry = queue_db.find_callsign(callsign)
        if not entry:
            raise HTTPException(status_code=404, detail='Callsign not found in queue')
        
        # QRZ information is already stored in the entry - no need for additional lookup
        return entry
    except HTTPException:
        raise  # Re-raise HTTP exceptions (like system inactive or not found)
    except Exception as e:
        logger.error(f"Failed to get callsign status: {e}")
        raise HTTPException(status_code=500, detail='Failed to get callsign status')

@queue_router.get('/list')
def list_queue():
    """Get current queue status"""
    try:
        # Check if system is active
        system_status = queue_db.get_system_status()
        max_queue_size = int(os.getenv('MAX_QUEUE_SIZE', '4'))
        
        if not system_status.get('active', False):
            # Return empty queue if system is inactive
            return {
                'queue': [], 
                'total': 0, 
                'max_size': max_queue_size,
                'system_active': False
            }
        
        queue = queue_db.get_queue_list()
        return {
            'queue': queue, 
            'total': len(queue), 
            'max_size': max_queue_size,
            'system_active': True
        }
    except Exception as e:
        logger.error(f"Failed to get queue list: {e}")
        raise HTTPException(status_code=500, detail='Failed to get queue list')

@queue_router.get('/current')
def get_current_qso():
    """Get the current callsign in QSO with stored QRZ.com profile information"""
    try:
        # Check if system is active
        system_status = queue_db.get_system_status()
        if not system_status.get('active', False):
            # Return None instead of error when system is inactive
            return None
        
        # Get current QSO - QRZ information is already stored
        current_qso = queue_db.get_current_qso()
        if not current_qso:
            return None
        
        return current_qso
    except Exception as e:
        logger.error(f"Failed to get current QSO: {e}")
        raise HTTPException(status_code=500, detail='Failed to get current QSO')