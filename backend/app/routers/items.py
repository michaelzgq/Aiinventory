from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..models import Item
from ..schemas import ItemCreate, Item

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[Item])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of items"""
    try:
        items = (
            db.query(Item)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return items
    
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        # 返回空列表而不是错误，提高兼容性
        return []


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific item by ID"""
    try:
        item = db.query(Item).filter(Item.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Item)
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new item"""
    try:
        # Check if item already exists
        existing = db.query(Item).filter(Item.item_id == item_data.item_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Item already exists")
        
        db_item = Item(**item_data.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        return db_item
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: str,
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update an existing item"""
    try:
        db_item = db.query(Item).filter(Item.item_id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        for key, value in item_data.dict().items():
            setattr(db_item, key, value)
        
        db.commit()
        db.refresh(db_item)
        
        return db_item
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating item: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete an item"""
    try:
        db_item = db.query(Item).filter(Item.item_id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        db.delete(db_item)
        db.commit()
        
        return {"message": "Item deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
