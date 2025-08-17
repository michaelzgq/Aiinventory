#!/usr/bin/env python3
"""
Single-file launcher for cloud platforms
Ultra-compatible deployment entry point
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Disable complex features for cloud deployment
os.environ["USE_PADDLE_OCR"] = "false"
os.environ["APP_ENV"] = "production"

# Import and run
from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)