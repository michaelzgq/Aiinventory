from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..schemas import Snapshot, UploadResponse
from ..services.snapshot import create_snapshot_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_snapshot(
    image: UploadFile = File(...),
    bin_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Upload and process a snapshot image"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_bytes = await image.read()
        
        snapshot_service = create_snapshot_service(db)
        result = snapshot_service.process_snapshot(image_bytes, bin_id, notes)
        
        return UploadResponse(**result)
    
    except Exception as e:
        logger.error(f"Error uploading snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-multiple", response_model=Dict[str, Any])
async def upload_multiple_snapshots(
    images: List[UploadFile] = File(...),
    bin_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Upload and process multiple snapshot images (for voting/confidence)"""
    try:
        if len(images) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 images allowed")
        
        image_bytes_list = []
        for image in images:
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="All files must be images")
            image_bytes_list.append(await image.read())
        
        snapshot_service = create_snapshot_service(db)
        result = snapshot_service.process_multiple_snapshots(image_bytes_list, bin_id, notes)
        
        return result
    
    except Exception as e:
        logger.error(f"Error uploading multiple snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Dict[str, Any]])
async def get_snapshots(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of recent snapshots"""
    try:
        snapshot_service = create_snapshot_service(db)
        snapshots = snapshot_service.get_latest_snapshots(limit)
        
        return snapshots
    
    except Exception as e:
        logger.error(f"Error getting snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bin/{bin_id}", response_model=List[Dict[str, Any]])
async def get_bin_snapshots(
    bin_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get snapshots for specific bin"""
    try:
        snapshot_service = create_snapshot_service(db)
        snapshots = snapshot_service.get_bin_snapshots(bin_id, limit)
        
        return snapshots
    
    except Exception as e:
        logger.error(f"Error getting bin snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/current", response_model=List[Dict[str, Any]])
async def get_current_inventory(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get current inventory based on latest snapshots"""
    try:
        snapshot_service = create_snapshot_service(db)
        inventory = snapshot_service.get_current_inventory()
        
        return inventory
    
    except Exception as e:
        logger.error(f"Error getting current inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{snapshot_id}", response_model=Dict[str, Any])
async def get_snapshot(
    snapshot_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific snapshot by ID"""
    try:
        from ..models import Snapshot as SnapshotModel
        from ..utils.storage import storage_manager
        
        snapshot = db.query(SnapshotModel).filter(SnapshotModel.id == snapshot_id).first()
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        result = {
            "id": snapshot.id,
            "ts": snapshot.ts,
            "bin_id": snapshot.bin_id,
            "item_ids": snapshot.item_ids or [],
            "photo_url": storage_manager.get_file_url(snapshot.photo_ref) if snapshot.photo_ref else None,
            "conf": snapshot.conf,
            "ocr_text": snapshot.ocr_text
        }
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a snapshot"""
    try:
        from ..models import Snapshot as SnapshotModel
        
        snapshot = db.query(SnapshotModel).filter(SnapshotModel.id == snapshot_id).first()
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        
        db.delete(snapshot)
        db.commit()
        
        return {"message": f"Snapshot {snapshot_id} deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))