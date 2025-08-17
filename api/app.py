# Vercel Serverless Function Entry Point for FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the main app
try:
    from backend.app.main import app
    handler = app
except ImportError:
    # Fallback if main app can't be imported
    app = FastAPI(title="Inventory AI - Vercel")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Inventory AI API on Vercel",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "api_status": "/api/status",
                "docs": "/docs"
            }
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "platform": "vercel"}
    
    handler = app
