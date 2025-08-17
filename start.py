#!/usr/bin/env python3
"""
Inventory AI - Production Startup Script
Handles deployment on various platforms (Railway, Vercel, Render, etc.)
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    import uvicorn
    from backend.app.main import app
    
    # Get port from environment (Railway, Heroku, etc. set this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Production settings
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )