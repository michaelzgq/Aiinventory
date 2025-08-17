import os
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Set environment for cloud deployment
os.environ['USE_PADDLE_OCR'] = 'false'
os.environ['APP_ENV'] = 'production'
os.environ.setdefault('API_KEY', 'vercel-demo-key')

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Create a simple fallback app
app = FastAPI(title="Inventory AI - Vercel", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Inventory AI is running on Vercel", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "platform": "vercel"}

# Try to import the full app
try:
    from backend.app.main import app as main_app
    # If successful, use the main app
    app = main_app
    print("Successfully loaded main application")
except Exception as e:
    print(f"Failed to load main app, using fallback: {e}")
    import traceback
    traceback.print_exc()
    
    # Add basic error info endpoint
    @app.get("/error")
    async def error_info():
        return {
            "error": str(e),
            "message": "Main application failed to load",
            "fallback": True
        }