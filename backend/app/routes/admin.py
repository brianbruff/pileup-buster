from fastapi import APIRouter, HTTPException, Depends
from app.auth import verify_admin_credentials

# Import database - use in-memory for testing if MongoDB not available
try:
    from app.database import queue_db
    if queue_db.collection is None:
        raise Exception("MongoDB not available")
except:
    from app.test_database import test_queue_db as queue_db

admin_router = APIRouter()

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
def next_callsign(username: str = Depends(verify_admin_credentials)):
    """Process the next callsign in queue"""
    try:
        next_entry = queue_db.get_next_callsign()
        if not next_entry:
            raise HTTPException(status_code=400, detail='Queue is empty')
        
        remaining_count = queue_db.get_queue_count()
        return {
            'message': f'Next callsign: {next_entry["callsign"]}',
            'processed': next_entry,
            'remaining': remaining_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')