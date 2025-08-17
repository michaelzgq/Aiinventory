#!/usr/bin/env python3
"""
Ultra-simple server for cloud deployment
Fallback option if other deployment methods fail
"""

import os
import sys
from pathlib import Path

# Set up paths
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"
sys.path.insert(0, str(backend_dir))

# Set essential environment variables
os.environ.setdefault("USE_PADDLE_OCR", "false")
os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("API_KEY", "railway-demo-key-2025")

def main():
    try:
        import uvicorn
        from backend.app.main import app
        
        # Get port from environment
        port = int(os.environ.get("PORT", 8000))
        
        print(f"🚀 Starting Inventory AI on port {port}")
        print(f"📱 Health check: http://localhost:{port}/health")
        print(f"📖 API docs: http://localhost:{port}/docs")
        
        # Run the app
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()