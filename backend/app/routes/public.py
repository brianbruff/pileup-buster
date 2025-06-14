from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.database import queue_db
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

public_router = APIRouter()

@public_router.get('/status')
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