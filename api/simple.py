from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

# Simple FastAPI app for Vercel
app = FastAPI(title="Inventory AI", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Inventory AI - Simple Version", 
        "status": "running",
        "platform": "vercel",
        "env": os.environ.get("APP_ENV", "unknown")
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": "2024-01-01"}

@app.get("/api/test")
async def test_api():
    return {"test": "ok", "message": "API is working"}

# Simple error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "Internal server error"}
    )