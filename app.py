import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment for cloud deployment
os.environ['USE_PADDLE_OCR'] = 'false'
os.environ['APP_ENV'] = 'production'
os.environ.setdefault('API_KEY', 'railway-demo-key')

try:
    from backend.app.main import app
    
    if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        print(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()