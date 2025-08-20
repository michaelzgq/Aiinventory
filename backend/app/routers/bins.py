from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..models import Bin
from ..schemas import BinCreate, Bin

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[Bin])
async def get_bins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of bins"""
    try:
        bins = (
            db.query(Bin)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return bins
    
    except Exception as e:
        logger.error(f"Error getting bins: {e}")
        # 返回空列表而不是错误，提高兼容性
        return []


@router.get("/{bin_id}", response_model=Bin)
async def get_bin(
    bin_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific bin by ID"""
    try:
        bin_item = db.query(Bin).filter(Bin.bin_id == bin_id).first()
        if not bin_item:
            raise HTTPException(status_code=404, detail="Bin not found")
        
        return bin_item
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bin: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Bin)
async def create_bin(
    bin_data: BinCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new bin"""
    try:
        # Check if bin already exists
        existing = db.query(Bin).filter(Bin.bin_id == bin_data.bin_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bin already exists")
        
        db_bin = Bin(**bin_data.dict())
        db.add(db_bin)
        db.commit()
        db.refresh(db_bin)
        
        return db_bin
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bin: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{bin_id}", response_model=Bin)
async def update_bin(
    bin_id: str,
    bin_data: BinCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update an existing bin"""
    try:
        db_bin = db.query(Bin).filter(Bin.bin_id == bin_id).first()
        if not db_bin:
            raise HTTPException(status_code=404, detail="Bin not found")
        
        for key, value in bin_data.dict().items():
            setattr(db_bin, key, value)
        
        db.commit()
        db.refresh(db_bin)
        
        return db_bin
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating bin: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{bin_id}")
async def delete_bin(
    bin_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a bin"""
    try:
        db_bin = db.query(Bin).filter(Bin.bin_id == bin_id).first()
        if not db_bin:
            raise HTTPException(status_code=404, detail="Bin not found")
        
        db.delete(db_bin)
        db.commit()
        
        return {"message": "Bin deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting bin: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
