from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging
from ..database import get_db
from ..deps import verify_api_key
from ..services.reconcile import create_reconciliation_service
from ..services.report import create_report_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run", response_model=Dict[str, Any])
async def run_reconciliation(
    target_date: Optional[date] = Query(None, description="Date to reconcile (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Run reconciliation for specified date and generate reports"""
    try:
        if target_date is None:
            target_date = date.today()
        
        # Run reconciliation
        reconcile_service = create_reconciliation_service(db)
        reconcile_result = reconcile_service.run_reconciliation(target_date)
        
        # Generate reports
        report_service = create_report_service(db)
        report_result = report_service.generate_reconciliation_report(target_date)
        
        return {
            "reconciliation": reconcile_result,
            "reports": report_result,
            "message": f"Reconciliation completed for {target_date}"
        }
    
    except Exception as e:
        logger.error(f"Error running reconciliation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies", response_model=List[Dict[str, Any]])
async def get_anomalies(
    target_date: Optional[date] = Query(None, description="Date to get anomalies for (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get anomalies for specified date"""
    try:
        if target_date is None:
            target_date = date.today()
        
        reconcile_service = create_reconciliation_service(db)
        anomalies = reconcile_service.get_anomalies_for_date(target_date)
        
        # Apply pagination
        paginated_anomalies = anomalies[skip:skip + limit]
        
        return paginated_anomalies
    
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies/summary", response_model=Dict[str, Any])
async def get_anomalies_summary(
    target_date: Optional[date] = Query(None, description="Date to get summary for (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get anomalies summary for specified date"""
    try:
        if target_date is None:
            target_date = date.today()
        
        reconcile_service = create_reconciliation_service(db)
        anomalies = reconcile_service.get_anomalies_for_date(target_date)
        
        # Calculate summary statistics
        total_anomalies = len(anomalies)
        by_type = {}
        by_severity = {}
        by_status = {}
        
        for anomaly in anomalies:
            # Count by type
            anomaly_type = anomaly.get('type', 'unknown')
            by_type[anomaly_type] = by_type.get(anomaly_type, 0) + 1
            
            # Count by severity
            severity = anomaly.get('severity', 'unknown')
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by status
            status = anomaly.get('status', 'unknown')
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "date": target_date.isoformat(),
            "total_anomalies": total_anomalies,
            "by_type": by_type,
            "by_severity": by_severity,
            "by_status": by_status,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting anomalies summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/generate", response_model=Dict[str, Any])
async def generate_reports(
    target_date: Optional[date] = Query(None, description="Date to generate reports for (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Generate reconciliation reports without running reconciliation"""
    try:
        if target_date is None:
            target_date = date.today()
        
        report_service = create_report_service(db)
        result = report_service.generate_reconciliation_report(target_date)
        
        return {
            "reports": result,
            "message": f"Reports generated for {target_date}"
        }
    
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/inventory", response_model=Dict[str, Any])
async def generate_inventory_report(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Generate current inventory report"""
    try:
        report_service = create_report_service(db)
        result = report_service.generate_inventory_report()
        
        return {
            "reports": result,
            "message": "Current inventory report generated"
        }
    
    except Exception as e:
        logger.error(f"Error generating inventory report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/anomalies/{anomaly_id}/status")
async def update_anomaly_status(
    anomaly_id: int,
    status: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update anomaly status (open/closed)"""
    try:
        from ..models import Anomaly
        
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        if status not in ["open", "closed"]:
            raise HTTPException(status_code=400, detail="Status must be 'open' or 'closed'")
        
        anomaly.status = status
        db.commit()
        
        return {"message": f"Anomaly {anomaly_id} status updated to {status}"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating anomaly status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
async def get_reconciliation_status(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get reconciliation system status"""
    try:
        from ..models import Snapshot, Anomaly, Order
        from datetime import timedelta
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Get counts
        today_snapshots = db.query(Snapshot).filter(
            Snapshot.ts >= datetime.combine(today, datetime.min.time())
        ).count()
        
        today_anomalies = db.query(Anomaly).filter(
            Anomaly.ts >= datetime.combine(today, datetime.min.time())
        ).count()
        
        today_orders = db.query(Order).filter(Order.ship_date == today).count()
        
        total_bins_scanned = db.query(Snapshot.bin_id).distinct().count()
        
        return {
            "date": today.isoformat(),
            "today_snapshots": today_snapshots,
            "today_anomalies": today_anomalies,
            "today_orders": today_orders,
            "total_bins_scanned": total_bins_scanned,
            "system_status": "operational",
            "last_check": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting reconciliation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))