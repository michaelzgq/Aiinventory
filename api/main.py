# Vercel Adapter for FastAPI
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

# Import and export the FastAPI app
from backend.app.main import app

# This is what Vercel will use
handler = app
