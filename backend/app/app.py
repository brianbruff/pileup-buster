from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import uvicorn
import logging
from datetime import datetime


def generate_status_html_optimized(frontend_url: str, timestamp: str, system_status: dict, current_qso: dict = None, queue_list: list = None) -> str:
    """
    Generate optimized HTML status page without screenshots
    
    Args:
        frontend_url: URL to link back to frontend
        timestamp: Timestamp of page generation
        system_status: System status information from database
        current_qso: Current QSO information (optional)
        queue_list: List of users in queue (optional)
        
    Returns:
        HTML content as string
    """
    is_active = system_status.get('active', False)
    status_class = 'active' if is_active else 'inactive'
    status_text = 'ACTIVE' if is_active else 'INACTIVE'
    status_color = '#28a745' if is_active else '#dc3545'
    
    # Build current user section
    current_user_section = ""
    if current_qso and current_qso.get('callsign'):
        callsign = current_qso['callsign']
        qrz_info = current_qso.get('qrz', {})
        name = qrz_info.get('name', 'Unknown')
        dxcc = qrz_info.get('dxcc_name', 'Unknown')
        
        current_user_section = f"""
        <div class="current-user-section">
            <h2>Currently Working</h2>
            <div class="current-user-card">
                <div class="callsign">{callsign}</div>
                <div class="user-details">
                    <div class="name">{name}</div>
                    <div class="dxcc">{dxcc}</div>
                </div>
            </div>
        </div>"""
    else:
        current_user_section = """
        <div class="current-user-section">
            <h2>Currently Working</h2>
            <div class="no-current-user">No active QSO</div>
        </div>"""
    
    # Build queue section
    queue_section = ""
    if queue_list and len(queue_list) > 0:
        queue_items = ""
        for i, entry in enumerate(queue_list[:10]):  # Show max 10 entries
            callsign = entry.get('callsign', 'Unknown')
            qrz_info = entry.get('qrz', {})
            name = qrz_info.get('name', 'Unknown')
            position = entry.get('position', i + 1)
            
            queue_items += f"""
            <div class="queue-item">
                <div class="position">#{position}</div>
                <div class="queue-callsign">{callsign}</div>
                <div class="queue-name">{name}</div>
            </div>"""
        
        if len(queue_list) > 10:
            queue_items += f"""
            <div class="queue-item more-users">
                <div class="position">...</div>
                <div class="queue-callsign">+{len(queue_list) - 10} more</div>
                <div class="queue-name">users in queue</div>
            </div>"""
        
        queue_section = f"""
        <div class="queue-section">
            <h2>Queue ({len(queue_list)} users)</h2>
            <div class="queue-list">
                {queue_items}
            </div>
        </div>"""
    else:
        queue_section = """
        <div class="queue-section">
            <h2>Queue (0 users)</h2>
            <div class="no-queue">No users in queue</div>
        </div>"""

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pileup Buster Status</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background-color: #ffffff;
            padding: 30px;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }}
        .header-logo {{
            max-height: 80px;
            max-width: 300px;
            height: auto;
            width: auto;
            margin-bottom: 15px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2rem;
            font-weight: 700;
            color: #2d3748;
        }}
        .timestamp {{
            opacity: 0.7;
            font-size: 0.9rem;
            color: #718096;
        }}
        .status-banner {{
            background-color: {status_color};
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0;
        }}
        .content {{
            padding: 30px;
        }}
        .current-user-section, .queue-section {{
            margin-bottom: 30px;
        }}
        .current-user-section h2, .queue-section h2 {{
            color: #4a5568;
            margin: 0 0 15px 0;
            font-size: 1.3rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 5px;
        }}
        .current-user-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .callsign {{
            font-size: 1.8rem;
            font-weight: bold;
            min-width: 120px;
        }}
        .user-details .name {{
            font-size: 1.1rem;
            margin-bottom: 5px;
        }}
        .user-details .dxcc {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        .no-current-user, .no-queue {{
            text-align: center;
            padding: 30px;
            color: #718096;
            font-style: italic;
            background-color: #f7fafc;
            border-radius: 8px;
            border: 2px dashed #e2e8f0;
        }}
        .queue-list {{
            background-color: #f7fafc;
            border-radius: 8px;
            overflow: hidden;
        }}
        .queue-item {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            border-bottom: 1px solid #e2e8f0;
            gap: 15px;
        }}
        .queue-item:last-child {{
            border-bottom: none;
        }}
        .queue-item.more-users {{
            background-color: #edf2f7;
            font-style: italic;
            color: #718096;
        }}
        .position {{
            font-weight: bold;
            color: #4a5568;
            min-width: 30px;
        }}
        .queue-callsign {{
            font-weight: 600;
            color: #2d3748;
            min-width: 80px;
        }}
        .queue-name {{
            color: #718096;
        }}
        .link-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .frontend-link {{
            display: inline-block;
            background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%);
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .frontend-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .note {{
            margin-top: 30px;
            padding: 20px;
            background-color: #ebf8ff;
            border-left: 4px solid #3182ce;
            border-radius: 0 8px 8px 0;
            color: #2c5282;
            font-size: 0.95rem;
        }}
        .status-details {{
            margin-top: 20px;
            padding: 20px;
            background-color: #f7fafc;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #4a5568;
        }}
        .status-details strong {{
            color: #2d3748;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            .header {{
                padding: 20px;
            }}
            .header-logo {{
                max-height: 60px;
                max-width: 250px;
            }}
            .header h1 {{
                font-size: 1.5rem;
            }}
            .content {{
                padding: 20px;
            }}
            .current-user-card {{
                flex-direction: column;
                text-align: center;
                gap: 10px;
            }}
            .queue-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/static/logo.png" alt="Pileup Buster Logo" class="header-logo" onerror="this.style.display='none';">
            <h1>Pileup Buster Status</h1>
            <div class="timestamp">Last updated: {timestamp}</div>
        </div>
        
        <div class="status-banner {status_class}">
            System Status: {status_text}
        </div>
        
        <div class="content">
            {current_user_section}
            
            {queue_section}
            
            <div class="link-container">
                <a href="{frontend_url}" class="frontend-link" target="_blank">
                    🚀 Visit Pileup Buster ({status_text})
                </a>
            </div>
            
            <div class="note">
                <strong>📻 Welcome to Pileup Buster!</strong><br>
                This page shows the current status of the ham radio queue management system. 
                Click the link above to access the live application and join the queue.
            </div>
            
            <div class="status-details">
                <strong>System Status:</strong> {status_text}<br>
                <strong>Current QSO:</strong> {current_qso.get('callsign', 'None') if current_qso else 'None'}<br>
                <strong>Queue Length:</strong> {len(queue_list) if queue_list else 0} users<br>
                <strong>Last Status Update:</strong> {system_status.get('last_updated', 'Unknown')}<br>
                <strong>Page Generated:</strong> {timestamp}
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_template


def create_app():
    # Load environment variables
    load_dotenv()
    
    # Create FastAPI app
    app = FastAPI(
        title="Pileup Buster API",
        description="Ham radio callsign queue management system",
        version="1.0.0",
        swagger_ui_parameters={
            "tryItOutEnabled": True,
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "filter": True
        }
    )
    
    # Enable CORS for frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configuration (stored as app state)
    app.state.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.state.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/pileup_buster')
    
    # Mount static files (logo, etc.)
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Add the status endpoint at root level
    @app.get('/status', response_class=HTMLResponse)
    async def get_status_page():
        """Get static HTML status page with current system status and queue information"""
        from app.database import queue_db
        
        try:
            # Get frontend URL from environment variable
            frontend_url = os.getenv('FRONTEND_URL', 'https://briankeating.net/pileup-buster')
            
            # Get system status from database
            system_status = queue_db.get_system_status()
            
            # Get current QSO information
            current_qso = None
            try:
                current_qso = queue_db.get_current_qso()
            except Exception:
                pass  # No current QSO is fine
            
            # Get queue list
            queue_list = []
            try:
                queue_list = queue_db.get_queue_list()
            except Exception:
                pass  # Empty queue is fine
            
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Generate HTML page with system status and queue info
            html_content = generate_status_html_optimized(frontend_url, timestamp, system_status, current_qso, queue_list)
            
            return HTMLResponse(content=html_content, status_code=200)
            
        except Exception as e:
            logging.error(f"Failed to generate status page: {e}")
            # Return a simple error page
            error_html = f"""
            <!DOCTYPE html>
            <html><head><title>Status Page Error</title></head>
            <body><h1>Status Page Unavailable</h1>
            <p>Unable to generate status page: {str(e)}</p>
            </body></html>
            """
            return HTMLResponse(content=error_html, status_code=500)

    # Include routers
    from app.routes.queue import queue_router
    from app.routes.admin import admin_router
    from app.routes.public import public_router
    from app.routes.events import events_router
    
    app.include_router(queue_router, prefix="/api/queue", tags=["queue"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(public_router, prefix="/api/public", tags=["public"])
    app.include_router(events_router, prefix="/api/events", tags=["events"])
    
    return app

app = create_app()

def main():
    """Entry point for the application script"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    main()