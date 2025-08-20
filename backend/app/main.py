from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

# 添加错误处理
try:
    from .config import settings
    from .database import create_tables, get_db
    from .routers import orders, allocations, snapshots, reconcile, queries, labels, health, ingest, bins, items
except ImportError as e:
    logging.error(f"Import error: {e}")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Inventory AI application...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # 不中断启动，继续运行
    
    # Ensure storage directories exist
    try:
        from .utils.storage import storage_manager
        logger.info("Storage system initialized")
    except Exception as e:
        logger.error(f"Failed to initialize storage: {e}")
        # 不中断启动，继续运行
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down Inventory AI application...")


# Create FastAPI app
app = FastAPI(
    title="Inventory AI",
    description="AI-powered warehouse inventory management system",
    version="1.0.0",
    docs_url="/docs" if settings.app_env == "dev" else None,
    redoc_url="/redoc" if settings.app_env == "dev" else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="backend/app/templates")

# Include API routers with error handling
try:
    app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
    app.include_router(allocations.router, prefix="/api/allocations", tags=["allocations"])
    app.include_router(snapshots.router, prefix="/api/snapshots", tags=["snapshots"])
    app.include_router(reconcile.router, prefix="/api/reconcile", tags=["reconcile"])
    app.include_router(queries.router, prefix="/api/nlq", tags=["queries"])
    app.include_router(labels.router, prefix="/api/labels", tags=["labels"])
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
    
    # 新添加的路由
    app.include_router(bins.router, prefix="/api/bins", tags=["bins"])
    app.include_router(items.router, prefix="/api/items", tags=["items"])
    
    logger.info("All routers included successfully")
except Exception as e:
    logger.error(f"Error including routers: {e}")
    # 继续运行，不中断应用

# Serve storage files
if settings.storage_backend == "local":
    try:
        storage_path = os.path.abspath(settings.storage_local_dir)
        if os.path.exists(storage_path):
            app.mount("/storage", StaticFiles(directory=storage_path), name="storage")
    except Exception as e:
        logger.error(f"Error mounting storage: {e}")


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page"""
    try:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "api_key": settings.api_key
        })
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error loading dashboard")


@app.get("/scan", response_class=HTMLResponse)
async def scan_page(request: Request):
    """Scan/Photo page"""
    try:
        return templates.TemplateResponse("scan.html", {
            "request": request,
            "api_key": settings.api_key
        })
    except Exception as e:
        logger.error(f"Error rendering scan page: {e}")
        raise HTTPException(status_code=500, detail="Error loading scan page")


@app.get("/upload-orders", response_class=HTMLResponse)
async def upload_orders_page(request: Request):
    """Upload orders page"""
    try:
        return templates.TemplateResponse("upload_orders.html", {
            "request": request,
            "api_key": settings.api_key
        })
    except Exception as e:
        logger.error(f"Error rendering upload orders page: {e}")
        raise HTTPException(status_code=500, detail="Error loading upload orders page")


@app.get("/reconcile", response_class=HTMLResponse)
async def reconcile_page(request: Request):
    """Reconcile page"""
    try:
        return templates.TemplateResponse("reconcile.html", {
            "request": request,
            "api_key": settings.api_key
        })
    except Exception as e:
        logger.error(f"Error rendering reconcile page: {e}")
        raise HTTPException(status_code=500, detail="Error loading reconcile page")


@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    """Orders management page"""
    try:
        return templates.TemplateResponse("orders.html", {
            "request": request,
            "api_key": settings.api_key
        })
    except Exception as e:
        logger.error(f"Error rendering orders page: {e}")
        raise HTTPException(status_code=500, detail="Error loading orders page")


# API status endpoint
@app.get("/api/status")
async def get_status():
    """Get application status"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "inventory-ai",
            "version": "1.0.0",
            "features": {
                "scanning": True,
                "ai_queries": True,
                "csv_import": True,
                "reconciliation": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "inventory-ai",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# API endpoint for inventory today (dashboard)
@app.get("/api/inventory/today")
async def get_inventory_today(db: Session = Depends(get_db)):
    """Get today's inventory snapshot"""
    try:
        from .services.snapshot import create_snapshot_service
        
        snapshot_service = create_snapshot_service(db)
        inventory = snapshot_service.get_current_inventory()
        
        return {
            "date": datetime.now().date().isoformat(),
            "inventory": inventory,
            "total_bins": len(inventory),
            "total_items": sum(len(item.get("item_ids", [])) for item in inventory)
        }
    except Exception as e:
        logger.error(f"Error getting today's inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    if request.url.path.startswith("/api/"):
        return {"detail": "API endpoint not found"}
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "error": "Page not found", "status_code": 404},
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    if request.url.path.startswith("/api/"):
        return {"detail": "Internal server error"}
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Internal server error", "status_code": 500},
        status_code=500
    )


# Webhook endpoints for WMS integration
@app.post("/webhook/wms/order-update")
async def wms_order_update(request: Request, db: Session = Depends(get_db)):
    """Webhook for WMS order updates"""
    try:
        data = await request.json()
        logger.info(f"Received WMS order update: {data}")
        
        # Process order update
        # This would integrate with your WMS system
        
        return {"status": "received", "message": "Order update processed"}
    except Exception as e:
        logger.error(f"Error processing WMS webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/wms/allocation-update")
async def wms_allocation_update(request: Request, db: Session = Depends(get_db)):
    """Webhook for WMS allocation updates"""
    try:
        data = await request.json()
        logger.info(f"Received WMS allocation update: {data}")
        
        # Process allocation update
        # This would integrate with your WMS system
        
        return {"status": "received", "message": "Allocation update processed"}
    except Exception as e:
        logger.error(f"Error processing WMS webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Development and debugging endpoints
if settings.app_env == "dev":
    @app.get("/api/dev/sample-data")
    async def create_sample_data(db: Session = Depends(get_db)):
        """Create sample data for development/testing"""
        try:
            from .models import Bin, Item, Order, Allocation
            from datetime import date
            
            # Create sample bins
            sample_bins = [
                Bin(bin_id="A51", zone="Zone-A", coords="10,20"),
                Bin(bin_id="A52", zone="Zone-A", coords="30,20"),
                Bin(bin_id="A53", zone="Zone-A", coords="50,20"),
                Bin(bin_id="A54", zone="Zone-A", coords="70,20"),
                Bin(bin_id="S-01", zone="Staging", coords="10,100"),
                Bin(bin_id="S-02", zone="Staging", coords="30,100"),
            ]
            
            # Create sample items
            sample_items = [
                Item(item_id="PALT-0001", sku="SKU-5566", customer_id="CUST-001"),
                Item(item_id="PALT-0002", sku="SKU-5566", customer_id="CUST-001"),
                Item(item_id="PALT-0003", sku="SKU-8899", customer_id="CUST-002"),
                Item(item_id="PALT-0004", sku="SKU-7777", customer_id="CUST-003"),
                Item(item_id="PALT-0005", sku="SKU-7777", customer_id="CUST-003"),
            ]
            
            # Create sample orders
            sample_orders = [
                Order(order_id="SO-1001", ship_date=date.today(), sku="SKU-5566", qty=2, 
                      item_ids=["PALT-0001", "PALT-0002"], status="pending"),
                Order(order_id="SO-1002", ship_date=date.today(), sku="SKU-8899", qty=1, 
                      item_ids=["PALT-0003"], status="pending"),
            ]
            
            # Create sample allocations
            sample_allocations = [
                Allocation(item_id="PALT-0001", bin_id="A54", status="allocated"),
                Allocation(item_id="PALT-0002", bin_id="A52", status="allocated"),
                Allocation(item_id="PALT-0003", bin_id="A51", status="allocated"),
                Allocation(item_id="PALT-0004", bin_id="A53", status="allocated"),
                Allocation(item_id="PALT-0005", bin_id="S-01", status="staged"),
            ]
            
            # Add to database
            for bins in sample_bins:
                existing = db.query(Bin).filter(Bin.bin_id == bins.bin_id).first()
                if not existing:
                    db.add(bins)
            
            for item in sample_items:
                existing = db.query(Item).filter(Item.item_id == item.item_id).first()
                if not existing:
                    db.add(item)
            
            for order in sample_orders:
                existing = db.query(Order).filter(Order.order_id == order.order_id).first()
                if not existing:
                    db.add(order)
            
            for allocation in sample_allocations:
                existing = db.query(Allocation).filter(Allocation.item_id == allocation.item_id).first()
                if not existing:
                    db.add(allocation)
            
            db.commit()
            
            return {
                "message": "Sample data created successfully",
                "bins": len(sample_bins),
                "items": len(sample_items),
                "orders": len(sample_orders),
                "allocations": len(sample_allocations)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating sample data: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/dev/reset-db")
    async def reset_database():
        """Reset database (development only)"""
        try:
            from .database import engine, Base
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            return {"message": "Database reset successfully"}
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# System information endpoint
@app.get("/api/system/info")
async def system_info():
    """Get system information"""
    try:
        import sys
        import platform
        
        return {
            "application": "Inventory AI",
            "version": "1.0.0",
            "environment": settings.app_env,
            "python_version": sys.version,
            "platform": platform.platform(),
            "timezone": settings.tz,
            "database_url": settings.db_url.split("@")[-1] if "@" in settings.db_url else "local",
            "storage_backend": settings.storage_backend,
            "features": {
                "paddle_ocr": settings.use_paddle_ocr,
                "staging_bins": settings.staging_bins_list,
                "staging_threshold_hours": settings.staging_threshold_hours
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "dev",
        log_level="info"
    )