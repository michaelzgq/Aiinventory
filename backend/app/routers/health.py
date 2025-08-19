from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging
import sys
import os
from ..database import get_db
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "inventory-ai",
        "version": "1.0.0"
    }


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including database connectivity"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
        db_error = None
    except Exception as e:
        db_status = "error"
        db_error = str(e)
        logger.error(f"Database health check failed: {e}")
    
    # Check storage
    try:
        storage_dir = settings.storage_local_dir
        storage_writable = os.access(storage_dir, os.W_OK) if os.path.exists(storage_dir) else False
        storage_status = "accessible" if storage_writable else "not_writable"
    except Exception as e:
        storage_status = "error"
        logger.error(f"Storage health check failed: {e}")
    
    # Check dependencies
    dependencies = {}
    
    # Check OpenCV
    try:
        import cv2
        dependencies["opencv"] = {"status": "available", "version": cv2.__version__}
    except ImportError:
        dependencies["opencv"] = {"status": "missing", "version": None}
    
    # Check PaddleOCR
    try:
        if settings.use_paddle_ocr:
            import paddleocr
            dependencies["paddleocr"] = {"status": "available", "enabled": True}
        else:
            dependencies["paddleocr"] = {"status": "disabled", "enabled": False}
    except ImportError:
        dependencies["paddleocr"] = {"status": "missing", "enabled": settings.use_paddle_ocr}
    
    # Check ReportLab
    try:
        import reportlab
        dependencies["reportlab"] = {"status": "available", "version": reportlab.Version}
    except ImportError:
        dependencies["reportlab"] = {"status": "missing", "version": None}
    
    # System info
    system_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "timezone": settings.tz
    }
    
    # Determine overall health
    overall_status = "healthy"
    if db_status != "connected":
        overall_status = "degraded"
    if storage_status == "error":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "service": "inventory-ai",
        "version": "1.0.0",
        "checks": {
            "database": {
                "status": db_status,
                "error": db_error
            },
            "storage": {
                "status": storage_status,
                "backend": settings.storage_backend,
                "local_dir": settings.storage_local_dir
            }
        },
        "dependencies": dependencies,
        "system": system_info,
        "configuration": {
            "use_paddle_ocr": settings.use_paddle_ocr,
            "staging_bins": settings.staging_bins_list,
            "staging_threshold_hours": settings.staging_threshold_hours
        }
    }


@router.get("/database", response_model=Dict[str, Any])
async def database_health_check(db: Session = Depends(get_db)):
    """Database-specific health check with table counts"""
    try:
        from ..models import Order, Item, Bin, Allocation, Snapshot, Anomaly
        
        # Test basic connectivity
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        # Get table counts
        counts = {
            "orders": db.query(Order).count(),
            "items": db.query(Item).count(),
            "bins": db.query(Bin).count(),
            "allocations": db.query(Allocation).count(),
            "snapshots": db.query(Snapshot).count(),
            "anomalies": db.query(Anomaly).count()
        }
        
        # Get recent activity
        from datetime import timedelta
        recent_snapshots = db.query(Snapshot).filter(
            Snapshot.ts >= datetime.now() - timedelta(hours=24)
        ).count()
        
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.ts >= datetime.now() - timedelta(hours=24)  
        ).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database_url": settings.db_url.split("@")[-1] if "@" in settings.db_url else settings.db_url,
            "table_counts": counts,
            "recent_activity": {
                "snapshots_24h": recent_snapshots,
                "anomalies_24h": recent_anomalies
            },
            "total_records": sum(counts.values())
        }
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database health check failed: {e}")


@router.get("/storage", response_model=Dict[str, Any])
async def storage_health_check():
    """Storage-specific health check"""
    try:
        from ..utils.storage import storage_manager
        
        # Check storage directories
        storage_info = {
            "backend": settings.storage_backend,
            "status": "unknown"
        }
        
        if settings.storage_backend == "local":
            storage_dir = settings.storage_local_dir
            
            # Check if directory exists and is writable
            if os.path.exists(storage_dir):
                if os.access(storage_dir, os.W_OK):
                    storage_info["status"] = "accessible"
                    
                    # Check subdirectories
                    subdirs = ["photos", "reports", "temp"]
                    subdir_status = {}
                    for subdir in subdirs:
                        subdir_path = os.path.join(storage_dir, subdir)
                        subdir_status[subdir] = {
                            "exists": os.path.exists(subdir_path),
                            "writable": os.access(subdir_path, os.W_OK) if os.path.exists(subdir_path) else False
                        }
                    
                    storage_info["subdirectories"] = subdir_status
                else:
                    storage_info["status"] = "not_writable"
            else:
                storage_info["status"] = "missing_directory"
                
            storage_info["local_path"] = storage_dir
        
        elif settings.storage_backend == "s3":
            # Would check S3 connectivity here
            storage_info["status"] = "not_implemented"
            storage_info["s3_bucket"] = settings.s3_bucket
        
        return {
            "timestamp": datetime.now().isoformat(),
            "storage": storage_info
        }
    
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Storage health check failed: {e}")


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness check"""
    try:
        # Test database
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        # Test storage
        storage_dir = settings.storage_local_dir
        if not os.path.exists(storage_dir) or not os.access(storage_dir, os.W_OK):
            raise Exception("Storage not accessible")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check():
    """Kubernetes-style liveness check"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }