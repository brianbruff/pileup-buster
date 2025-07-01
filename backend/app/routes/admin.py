from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import queue_db
from app.auth import verify_admin_credentials
from app.services.events import event_broadcaster
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

admin_router = APIRouter()

class SystemStatusRequest(BaseModel):
    active: bool

class FrequencyRequest(BaseModel):
    frequency: str

class SplitRequest(BaseModel):
    split: str

@admin_router.get('/queue')
def admin_queue(username: str = Depends(verify_admin_credentials)):
    """Admin view of the queue"""
    try:
        queue_list = queue_db.get_queue_list()
        return {
            'queue': queue_list,
            'total': len(queue_list),
            'admin': True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.delete('/queue/{callsign}')
def remove_callsign(callsign: str, username: str = Depends(verify_admin_credentials)):
    """Remove a callsign from the queue"""
    callsign = callsign.upper().strip()
    
    try:
        removed_entry = queue_db.remove_callsign(callsign)
        if removed_entry:
            return {
                'message': f'Callsign {callsign} removed from queue',
                'removed': removed_entry
            }
        raise HTTPException(status_code=404, detail='Callsign not found in queue')
    except Exception as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail='Callsign not found in queue')
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.post('/queue/clear')
def clear_queue(username: str = Depends(verify_admin_credentials)):
    """Clear the entire queue"""
    try:
        count = queue_db.clear_queue()
        return {
            'message': f'Queue cleared. Removed {count} entries.',
            'cleared_count': count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.post('/queue/next')
async def next_callsign(username: str = Depends(verify_admin_credentials)):
    """Process the next callsign in queue and manage QSO status"""
    try:
        # Clear any existing current QSO
        current_qso = queue_db.clear_current_qso()
        
        # Get the next callsign from queue
        next_entry = queue_db.get_next_callsign()
        
        if not next_entry:
            # If no one is in queue, return None for current_qso
            # Broadcast that current QSO is now None
            try:
                await event_broadcaster.broadcast_current_qso(None)
            except Exception as e:
                logger.warning(f"Failed to broadcast current QSO event: {e}")
            return None
        
        # Put the next callsign into QSO status with stored QRZ information
        qrz_info = next_entry.get('qrz', {
            'callsign': next_entry["callsign"],
            'name': None,
            'address': None,
            'image': None,
            'error': 'QRZ information not available'
        })
        new_qso = queue_db.set_current_qso(next_entry["callsign"], qrz_info)
        
        # Broadcast the new current QSO
        try:
            await event_broadcaster.broadcast_current_qso(new_qso)
            
            # Broadcast updated queue (since someone was removed)
            queue_list = queue_db.get_queue_list()
            max_queue_size = int(os.getenv('MAX_QUEUE_SIZE', '4'))
            await event_broadcaster.broadcast_queue_update({
                'queue': queue_list, 
                'total': len(queue_list), 
                'max_size': max_queue_size,
                'system_active': True
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast SSE events: {e}")
        
        return new_qso
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.post('/qso/complete')
async def complete_current_qso(username: str = Depends(verify_admin_credentials)):
    """Complete the current QSO without advancing to the next station"""
    try:
        # Clear the current QSO
        cleared_qso = queue_db.clear_current_qso()
        
        if not cleared_qso:
            return {
                'message': 'No active QSO to complete',
                'cleared_qso': None
            }
        
        # Broadcast that current QSO is now None
        try:
            await event_broadcaster.broadcast_current_qso(None)
        except Exception as e:
            logger.warning(f"Failed to broadcast current QSO clear event: {e}")
        
        return {
            'message': f'QSO with {cleared_qso["callsign"]} completed successfully',
            'cleared_qso': cleared_qso
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.post('/status')
async def set_system_status(
    request: SystemStatusRequest, 
    username: str = Depends(verify_admin_credentials)
):
    """Set the system status (activate/deactivate)"""
    try:
        status = queue_db.set_system_status(request.active, username)
        action = "activated" if request.active else "deactivated"
        cleared_count = status.get("cleared_count", 0)
        qso_cleared = status.get("qso_cleared", False)
        
        # Build message with queue and QSO clearing information
        message_parts = [f'System {action} successfully.']
        message_parts.append(f'Queue cleared ({cleared_count} entries removed)')
        if qso_cleared:
            message_parts.append('Current QSO cleared')
        message = '. '.join(message_parts)
        
        # Broadcast system status change
        try:
            await event_broadcaster.broadcast_system_status({
                'active': request.active
            })
            
            # If system was deactivated, also broadcast empty queue and no current QSO
            if not request.active:
                await event_broadcaster.broadcast_current_qso(None)
                max_queue_size = int(os.getenv('MAX_QUEUE_SIZE', '4'))
                await event_broadcaster.broadcast_queue_update({
                    'queue': [], 
                    'total': 0, 
                    'max_size': max_queue_size,
                    'system_active': False
                })
                
                # Clear split when system goes offline
                try:
                    split_data = queue_db.clear_split(username)
                    await event_broadcaster.broadcast_split_update(split_data)
                except Exception as e:
                    logger.warning(f"Failed to clear split when going offline: {e}")
        except Exception as e:
            logger.warning(f"Failed to broadcast system status events: {e}")
        
        return {
            'message': message,
            'status': status
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f'Database error: {str(e)}'
        )

@admin_router.get('/status')
def get_system_status(username: str = Depends(verify_admin_credentials)):
    """Get the current system status"""
    try:
        status = queue_db.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.post('/frequency')
async def set_frequency(
    request: FrequencyRequest, 
    username: str = Depends(verify_admin_credentials)
):
    """Set the current transmission frequency (admin only)"""
    try:
        frequency_data = queue_db.set_frequency(request.frequency, username)
        
        # Broadcast frequency update
        try:
            await event_broadcaster.broadcast_frequency_update(frequency_data)
        except Exception as e:
            logger.warning(f"Failed to broadcast frequency update event: {e}")
        
        return {
            'message': f'Frequency set to {request.frequency}',
            'frequency_data': frequency_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.delete('/frequency')
async def clear_frequency(
    username: str = Depends(verify_admin_credentials)
):
    """Clear the current transmission frequency (admin only)"""
    try:
        frequency_data = queue_db.clear_frequency(username)
        
        # Broadcast frequency update (with None frequency)
        try:
            await event_broadcaster.broadcast_frequency_update({
                'frequency': None,
                'last_updated': frequency_data['last_updated'],
                'updated_by': frequency_data['updated_by']
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast frequency clear event: {e}")
        
        return {
            'message': 'Frequency cleared successfully',
            'frequency_data': frequency_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.post('/split')
async def set_split(
    request: SplitRequest, 
    username: str = Depends(verify_admin_credentials)
):
    """Set the current split value (admin only)"""
    try:
        split_data = queue_db.set_split(request.split, username)
        
        # Broadcast split update
        try:
            await event_broadcaster.broadcast_split_update(split_data)
        except Exception as e:
            logger.warning(f"Failed to broadcast split update event: {e}")
        
        return {
            'message': f'Split set to {request.split}',
            'split_data': split_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.delete('/split')
async def clear_split(
    username: str = Depends(verify_admin_credentials)
):
    """Clear the current split value (admin only)"""
    try:
        split_data = queue_db.clear_split(username)
        
        # Broadcast split update
        try:
            await event_broadcaster.broadcast_split_update(split_data)
        except Exception as e:
            logger.warning(f"Failed to broadcast split clear event: {e}")
        
        return {
            'message': 'Split cleared',
            'split_data': split_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@admin_router.get('/current')
def admin_get_current_qso(username: str = Depends(verify_admin_credentials)):
    """Admin endpoint to get current QSO regardless of system status"""
    try:
        current_qso = queue_db.get_current_qso()
        return current_qso
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')