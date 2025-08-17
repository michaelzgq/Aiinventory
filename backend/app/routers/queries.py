from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..schemas import NLQRequest, NLQResponse
from ..services.nlq import create_nlq_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=NLQResponse)
async def natural_language_query(
    request: NLQRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Process natural language query"""
    try:
        nlq_service = create_nlq_service(db)
        result = nlq_service.process_query(request.text)
        
        return NLQResponse(**result)
    
    except Exception as e:
        logger.error(f"Error processing NLQ: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples", response_model=Dict[str, Any])
async def get_query_examples():
    """Get example queries that can be processed"""
    try:
        examples = {
            "bin_queries": [
                "A54现在有什么？",
                "What's in bin A54?",
                "Check A54",
                "看看S-01"
            ],
            "sku_queries": [
                "找 SKU-5566",
                "Find SKU-5566",
                "Where is SKU-5566?",
                "SKU 5566 在哪里"
            ],
            "item_queries": [
                "PALT-0001 在哪",
                "Where is PALT-0001?",
                "Find item PALT-0001",
                "托盘 PALT-0001"
            ],
            "report_queries": [
                "导出今天的差异报告",
                "Export today's anomaly report",
                "Download today's reconciliation report",
                "生成报告"
            ],
            "stats_queries": [
                "今天有多少异常",
                "How many anomalies today?",
                "异常统计",
                "Anomaly count"
            ],
            "inventory_queries": [
                "库存总览",
                "Inventory summary",
                "Current inventory",
                "总共有多少货物"
            ]
        }
        
        return {
            "examples": examples,
            "supported_languages": ["English", "中文"],
            "note": "The system supports natural language queries about bin contents, SKU locations, item tracking, report generation, and inventory statistics."
        }
    
    except Exception as e:
        logger.error(f"Error getting query examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intents", response_model=Dict[str, Any])
async def get_supported_intents():
    """Get list of supported query intents"""
    try:
        intents = {
            "check_bin": {
                "description": "Check contents of a specific bin",
                "examples": ["A54现在有什么？", "What's in bin A54?"],
                "returns": "List of items in the bin with photo reference"
            },
            "find_sku": {
                "description": "Find locations of items with specific SKU",
                "examples": ["找 SKU-5566", "Where is SKU-5566?"],
                "returns": "List of locations where the SKU was found"
            },
            "find_item": {
                "description": "Find location of specific item ID",
                "examples": ["PALT-0001 在哪", "Where is PALT-0001?"],
                "returns": "Current location and status of the item"
            },
            "export_report": {
                "description": "Generate and export reconciliation reports",
                "examples": ["导出今天的差异报告", "Export today's report"],
                "returns": "Instructions and links for report generation"
            },
            "anomaly_stats": {
                "description": "Get anomaly statistics for a date",
                "examples": ["今天有多少异常", "How many anomalies today?"],
                "returns": "Count and breakdown of anomalies"
            },
            "inventory_summary": {
                "description": "Get overall inventory summary",
                "examples": ["库存总览", "Inventory summary"],
                "returns": "High-level inventory statistics"
            }
        }
        
        return {
            "supported_intents": intents,
            "total_intents": len(intents)
        }
    
    except Exception as e:
        logger.error(f"Error getting supported intents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=Dict[str, Any])
async def test_query_parsing(
    request: NLQRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Test query parsing without executing (for debugging)"""
    try:
        nlq_service = create_nlq_service(db)
        
        # Extract intent and entities without processing
        intent, entities = nlq_service._parse_intent(request.text.lower())
        
        return {
            "input_text": request.text,
            "detected_intent": intent,
            "extracted_entities": entities,
            "note": "This is a test endpoint that shows parsing results without executing the query."
        }
    
    except Exception as e:
        logger.error(f"Error testing query parsing: {e}")
        raise HTTPException(status_code=500, detail=str(e))