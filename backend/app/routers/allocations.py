from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..schemas import Allocation, AllocationCreate
from ..services.ingest import create_ingest_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_allocations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Upload allocations from CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        ingest_service = create_ingest_service(db)
        result = ingest_service.import_allocations(csv_content)
        
        return {
            "message": "Allocations uploaded successfully",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Error uploading allocations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Allocation])
async def get_allocations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of allocations"""
    try:
        from ..models import Allocation as AllocationModel
        
        allocations = (
            db.query(AllocationModel)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return allocations
    
    except Exception as e:
        logger.error(f"Error getting allocations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{item_id}", response_model=Allocation)
async def get_allocation_by_item(
    item_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get allocation for specific item"""
    try:
        from ..models import Allocation as AllocationModel
        
        allocation = db.query(AllocationModel).filter(AllocationModel.item_id == item_id).first()
        if not allocation:
            raise HTTPException(status_code=404, detail="Allocation not found")
        
        return allocation
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bin/{bin_id}", response_model=List[Allocation])
async def get_allocations_by_bin(
    bin_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get all allocations for specific bin"""
    try:
        from ..models import Allocation as AllocationModel
        
        allocations = db.query(AllocationModel).filter(AllocationModel.bin_id == bin_id).all()
        
        return allocations
    
    except Exception as e:
        logger.error(f"Error getting bin allocations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=Allocation)
async def create_allocation(
    allocation: AllocationCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new allocation"""
    try:
        from ..models import Allocation as AllocationModel
        
        # Check if allocation already exists
        existing = db.query(AllocationModel).filter(AllocationModel.item_id == allocation.item_id).first()
        if existing:
            # Update existing allocation
            existing.bin_id = allocation.bin_id
            existing.status = allocation.status
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new allocation
            db_allocation = AllocationModel(**allocation.dict())
            db.add(db_allocation)
            db.commit()
            db.refresh(db_allocation)
            return db_allocation
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}")
async def update_allocation(
    item_id: str,
    bin_id: str,
    status: str = "allocated",
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update allocation for item"""
    try:
        from ..models import Allocation as AllocationModel
        
        allocation = db.query(AllocationModel).filter(AllocationModel.item_id == item_id).first()
        if not allocation:
            raise HTTPException(status_code=404, detail="Allocation not found")
        
        allocation.bin_id = bin_id
        allocation.status = status
        db.commit()
        
        return {"message": f"Allocation for {item_id} updated"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))