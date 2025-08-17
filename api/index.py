import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

# Set environment for cloud deployment
os.environ['USE_PADDLE_OCR'] = 'false'
os.environ['APP_ENV'] = 'production'
os.environ.setdefault('API_KEY', 'vercel-demo-key')

try:
    from backend.app.main import app
    
    # Vercel expects the app to be available as a module-level variable
    # This is the entry point for Vercel serverless functions
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    raise