from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Dict

# Set environment
os.environ['USE_PADDLE_OCR'] = 'false'
os.environ['APP_ENV'] = 'production'

# FastAPI app
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
        "message": "🏭 Inventory AI - Running on Vercel", 
        "status": "running",
        "platform": "vercel",
        "env": os.environ.get("APP_ENV", "unknown"),
        "features": ["REST API", "Health Check", "Basic Inventory", "Dashboard"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "platform": "vercel",
        "database": "in-memory",
        "opencv": "disabled",
        "ocr": "disabled",
        "timestamp": "2024-01-01"
    }

# Simple in-memory storage for demo
inventory_items = []
bins = [
    {"id": "A01", "location": "Aisle A, Level 1", "capacity": 100, "current_items": 0},
    {"id": "A02", "location": "Aisle A, Level 2", "capacity": 100, "current_items": 0},
    {"id": "B01", "location": "Aisle B, Level 1", "capacity": 150, "current_items": 0},
    {"id": "S-01", "location": "Staging Area 1", "capacity": 200, "current_items": 0}
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
    return {"message": "Item added successfully", "item": item}

@app.get("/api/bins/{bin_id}")
async def get_bin(bin_id: str):
    """Get specific bin"""
    bin_data = next((b for b in bins if b["id"] == bin_id), None)
    if not bin_data:
        raise HTTPException(status_code=404, detail="Bin not found")
    return bin_data

@app.get("/dashboard")
async def dashboard():
    """Interactive dashboard"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inventory AI Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                margin: 0; padding: 20px; background: #f5f5f5; 
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #333; margin: 0; }
            .header p { color: #666; margin: 10px 0; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { 
                background: white; border-radius: 8px; padding: 20px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }
            .card h3 { margin-top: 0; color: #333; }
            .status { color: #22c55e; font-weight: bold; }
            .api-link { 
                display: inline-block; padding: 8px 16px; background: #3b82f6; 
                color: white; text-decoration: none; border-radius: 4px; margin: 4px;
            }
            .api-link:hover { background: #2563eb; }
            .endpoint { 
                background: #f8f9fa; padding: 8px; margin: 4px 0; 
                border-radius: 4px; font-family: monospace; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏭 Inventory AI Dashboard</h1>
                <p>AI-powered inventory management system running on Vercel</p>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>📊 System Status</h3>
                    <p class="status">✅ System Online</p>
                    <p><strong>Platform:</strong> Vercel Serverless</p>
                    <p><strong>Environment:</strong> Production</p>
                    <p><strong>Database:</strong> In-Memory</p>
                </div>
                
                <div class="card">
                    <h3>🚀 Quick Actions</h3>
                    <a href="/api/bins" class="api-link">📦 View Bins</a>
                    <a href="/api/inventory" class="api-link">📋 Inventory</a>
                    <a href="/health" class="api-link">❤️ Health</a>
                </div>
                
                <div class="card">
                    <h3>🔗 API Endpoints</h3>
                    <div class="endpoint">GET /api/bins</div>
                    <div class="endpoint">GET /api/inventory</div>
                    <div class="endpoint">POST /api/inventory</div>
                    <div class="endpoint">GET /api/bins/{id}</div>
                </div>
                
                <div class="card">
                    <h3>📈 Features</h3>
                    <ul>
                        <li>✅ REST API</li>
                        <li>✅ Bin Management</li>
                        <li>✅ Inventory Tracking</li>
                        <li>✅ Health Monitoring</li>
                        <li>🔄 Real-time Updates</li>
                    </ul>
                </div>
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
        content={
            "error": str(exc), 
            "detail": "Internal server error", 
            "platform": "vercel",
            "path": str(request.url)
        }
    )

# This is required for Vercel
handler = app