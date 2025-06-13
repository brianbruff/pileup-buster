from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn

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
    
    # Include routers
    from app.routes.queue import queue_router
    from app.routes.admin import admin_router
    from app.routes.public import public_router
    from app.routes.websocket import websocket_router
    
    app.include_router(queue_router, prefix="/api/queue", tags=["queue"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(public_router, prefix="/api/public", tags=["public"])
    app.include_router(websocket_router, prefix="/api", tags=["websocket"])
    
    return app

app = create_app()

def main():
    """Entry point for the application script"""
    uvicorn.run(app, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    main()