from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any

queue_router = APIRouter()

# In-memory storage for demo purposes
# In production, this would use MongoDB
queue_storage: List[Dict[str, Any]] = []

class CallsignRequest(BaseModel):
    callsign: str

class QueueEntry(BaseModel):
    callsign: str
    timestamp: str
    position: int

@queue_router.post('/register')
def register_callsign(request: CallsignRequest, fastapi_request: Request):
    """Register a callsign in the queue"""
    callsign = request.callsign.upper().strip()
    
    if not callsign:
        raise HTTPException(status_code=400, detail='Callsign is required')
    
    # Check if callsign already in queue
    for entry in queue_storage:
        if entry['callsign'] == callsign:
            raise HTTPException(status_code=400, detail='Callsign already in queue')
    
    # Check queue size limit
    max_queue_size = fastapi_request.app.state.max_queue_size
    if len(queue_storage) >= max_queue_size:
        raise HTTPException(status_code=400, detail=f'Queue is full. Maximum {max_queue_size} callsigns allowed.')
    
    # Add to queue
    entry = {
        'callsign': callsign,
        'timestamp': datetime.utcnow().isoformat(),
        'position': len(queue_storage) + 1
    }
    queue_storage.append(entry)
    
    return {'message': 'Callsign registered successfully', 'entry': entry}

@queue_router.get('/status/{callsign}')
def get_status(callsign: str):
    """Get position of callsign in queue"""
    callsign = callsign.upper().strip()
    
    for i, entry in enumerate(queue_storage):
        if entry['callsign'] == callsign:
            entry['position'] = i + 1
            return entry
    
    raise HTTPException(status_code=404, detail='Callsign not found in queue')

@queue_router.get('/list')
def list_queue():
    """Get current queue status"""
    # Update positions
    for i, entry in enumerate(queue_storage):
        entry['position'] = i + 1
    
    return {'queue': queue_storage, 'total': len(queue_storage)}