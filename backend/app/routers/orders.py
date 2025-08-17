from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..schemas import Order, OrderCreate
from ..services.ingest import create_ingest_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Upload orders from CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        ingest_service = create_ingest_service(db)
        result = ingest_service.import_orders(csv_content)
        
        return {
            "message": "Orders uploaded successfully",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Error uploading orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Order])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get list of orders"""
    try:
        from ..models import Order as OrderModel
        
        orders = (
            db.query(OrderModel)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return orders
    
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get specific order by ID"""
    try:
        from ..models import Order as OrderModel
        
        order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=Order)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new order"""
    try:
        from ..models import Order as OrderModel
        
        db_order = OrderModel(**order.dict())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update order status"""
    try:
        from ..models import Order as OrderModel
        
        order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order.status = status
        db.commit()
        
        return {"message": f"Order {order_id} status updated to {status}"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail=str(e))