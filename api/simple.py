from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from typing import List, Dict

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set environment
os.environ['USE_PADDLE_OCR'] = 'false'
os.environ['APP_ENV'] = 'production'

# FastAPI app with enhanced features
app = FastAPI(
    title="Inventory AI", 
    version="1.0.0",
    description="AI-powered inventory management system"
)

# Add CORS middleware
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
        "message": "Inventory AI - Enhanced Version", 
        "status": "running",
        "platform": "vercel",
        "env": os.environ.get("APP_ENV", "unknown"),
        "features": ["REST API", "Health Check", "Basic Inventory"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "platform": "vercel",
        "database": "in-memory",
        "opencv": "disabled",
        "ocr": "disabled"
    }

# Simple in-memory storage for demo
inventory_items = []
bins = [
    {"id": "A01", "location": "Aisle A, Level 1", "capacity": 100},
    {"id": "A02", "location": "Aisle A, Level 2", "capacity": 100},
    {"id": "B01", "location": "Aisle B, Level 1", "capacity": 150},
    {"id": "S-01", "location": "Staging Area 1", "capacity": 200}
]

@app.get("/api/bins")
async def get_bins():
    """Get all bins"""
    return {"bins": bins, "count": len(bins)}

@app.get("/api/inventory")
async def get_inventory():
    """Get all inventory items"""
    return {"items": inventory_items, "count": len(inventory_items)}

@app.post("/api/inventory")
async def add_item(item: Dict):
    """Add inventory item"""
    item["id"] = len(inventory_items) + 1
    inventory_items.append(item)
    return {"message": "Item added", "item": item}

@app.get("/api/bins/{bin_id}")
async def get_bin(bin_id: str):
    """Get specific bin"""
    bin_data = next((b for b in bins if b["id"] == bin_id), None)
    if not bin_data:
        raise HTTPException(status_code=404, detail="Bin not found")
    return bin_data

@app.get("/dashboard")
async def dashboard():
    """Simple dashboard"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inventory AI Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏭 Inventory AI Dashboard</h1>
            <div class="card">
                <h3>System Status</h3>
                <p class="status">✅ System Running on Vercel</p>
                <p>Platform: Vercel Serverless</p>
                <p>Environment: Production</p>
            </div>
            <div class="card">
                <h3>Quick Links</h3>
                <p><a href="/api/bins">📦 View Bins</a></p>
                <p><a href="/api/inventory">📋 View Inventory</a></p>
                <p><a href="/health">❤️ Health Check</a></p>
            </div>
            <div class="card">
                <h3>API Endpoints</h3>
                <ul>
                    <li>GET /api/bins - List all bins</li>
                    <li>GET /api/inventory - List inventory</li>
                    <li>POST /api/inventory - Add item</li>
                    <li>GET /api/bins/{id} - Get bin details</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """)

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "Internal server error", "platform": "vercel"}
    )