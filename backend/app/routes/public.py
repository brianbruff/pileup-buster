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

@public_router.get('/frequency')
def get_current_frequency():
    """Get the current transmission frequency - public endpoint"""
    try:
        frequency_data = queue_db.get_frequency()
        if frequency_data is None:
            return {
                'frequency': None,
                'last_updated': None
            }
        
        # Return frequency data excluding admin username for public consumption
        return {
            'frequency': frequency_data.get('frequency'),
            'last_updated': frequency_data.get('last_updated')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@public_router.get('/split')
def get_current_split():
    """Get the current split value - public endpoint"""
    try:
        split_data = queue_db.get_split()
        if split_data is None:
            return {
                'split': None,
                'last_updated': None
            }
        
        # Return split data excluding admin username for public consumption
        return {
            'split': split_data.get('split'),
            'last_updated': split_data.get('last_updated')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')