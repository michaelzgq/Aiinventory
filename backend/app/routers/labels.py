from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..schemas import LabelGenerateRequest
from ..services.labels import create_label_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_labels(
    request: LabelGenerateRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Generate QR code labels PDF"""
    try:
        if not request.item_ids and not request.count:
            raise HTTPException(
                status_code=400, 
                detail="Either item_ids or count must be specified"
            )
        
        if request.item_ids and request.count:
            raise HTTPException(
                status_code=400, 
                detail="Only one of item_ids or count should be specified"
            )
        
        if request.count and (request.count < 1 or request.count > 100):
            raise HTTPException(
                status_code=400, 
                detail="Count must be between 1 and 100"
            )
        
        label_service = create_label_service()
        result = label_service.generate_labels_pdf(
            item_ids=request.item_ids,
            count=request.count
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating labels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-bin-labels", response_model=Dict[str, Any])
async def generate_bin_labels(
    bin_ids: List[str],
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Generate bin location labels PDF"""
    try:
        if not bin_ids:
            raise HTTPException(status_code=400, detail="bin_ids list cannot be empty")
        
        if len(bin_ids) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 bin labels per request")
        
        label_service = create_label_service()
        result = label_service.generate_bin_labels(bin_ids)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating bin labels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=Dict[str, Any])
async def get_label_templates():
    """Get information about available label templates"""
    try:
        templates = {
            "item_labels": {
                "description": "QR code labels for inventory items",
                "size": "2x5 grid on Letter/A4 page",
                "content": ["QR code", "Item ID", "Generation date"],
                "use_case": "Pallet and item tracking"
            },
            "bin_labels": {
                "description": "QR code labels for bin locations", 
                "size": "2x5 grid on Letter/A4 page",
                "content": ["QR code", "Bin ID", "Generation date"],
                "use_case": "Bin location identification"
            }
        }
        
        return {
            "available_templates": templates,
            "page_format": "Letter/A4",
            "labels_per_page": 10,
            "grid_layout": "2x5",
            "print_recommendations": [
                "Use black and white printing",
                "Use matte finish labels for better QR readability",
                "Ensure proper scaling - do not fit to page"
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting label templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{label_type}")
async def preview_label_format(
    label_type: str,
    sample_id: Optional[str] = "SAMPLE-001"
):
    """Get preview information for label format"""
    try:
        if label_type not in ["item", "bin"]:
            raise HTTPException(status_code=400, detail="label_type must be 'item' or 'bin'")
        
        preview_info = {
            "label_type": label_type,
            "sample_content": {
                "qr_code_data": sample_id,
                "display_text": sample_id,
                "date": "2024-01-01",
                "format": "QR Code + Text"
            },
            "dimensions": {
                "width": "4.25 inches",
                "height": "2.2 inches",
                "qr_size": "1.5x1.5 inches"
            },
            "layout": {
                "qr_position": "center-top",
                "text_position": "center-bottom",
                "margins": "0.25 inches"
            }
        }
        
        return preview_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating label preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=Dict[str, Any])
async def get_label_generation_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get history of recent label generations"""
    try:
        # This would typically query a label_history table
        # For now, return mock data
        history = {
            "recent_generations": [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "type": "item_labels",
                    "count": 10,
                    "filename": "labels_20240101_100000.pdf"
                },
                {
                    "timestamp": "2024-01-01T09:30:00Z", 
                    "type": "bin_labels",
                    "count": 5,
                    "filename": "bin_labels_20240101_093000.pdf"
                }
            ],
            "total_labels_generated_today": 15,
            "note": "Label generation history is not yet persisted to database"
        }
        
        return history
    
    except Exception as e:
        logger.error(f"Error getting label history: {e}")
        raise HTTPException(status_code=500, detail=str(e))