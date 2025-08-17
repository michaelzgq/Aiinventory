from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from collections import defaultdict
import logging
from ..models import Order, Allocation, Snapshot, Anomaly, Item
from ..config import settings

logger = logging.getLogger(__name__)


class ReconciliationService:
    def __init__(self, db: Session):
        self.db = db
    
    def run_reconciliation(self, target_date: date) -> Dict[str, Any]:
        """Run full reconciliation for the specified date"""
        try:
            logger.info(f"Starting reconciliation for {target_date}")
            
            # Clear existing anomalies for the date
            self.db.query(Anomaly).filter(
                Anomaly.ts >= target_date,
                Anomaly.ts < target_date + timedelta(days=1)
            ).delete()
            
            # Get data for reconciliation
            orders = self._get_orders_for_date(target_date)
            allocations = self._get_latest_allocations()
            snapshots = self._get_last_snapshots_before(target_date + timedelta(days=1))
            
            # Build indices
            seen_item_to_bin = self._index_seen_items(snapshots)
            seen_bin_to_items = self._index_bin_items(snapshots)
            
            # Run reconciliation checks
            anomalies = []
            
            # Check 1: Unshipped orders (should be shipped but still seen)
            anomalies.extend(self._check_unshipped_orders(orders, seen_item_to_bin, target_date))
            
            # Check 2: Misplaced items (wrong bin)
            anomalies.extend(self._check_misplaced_items(allocations, seen_item_to_bin))
            
            # Check 3: Orphan items (not in system)
            anomalies.extend(self._check_orphan_items(seen_item_to_bin))
            
            # Check 4: Staging area issues
            anomalies.extend(self._check_staging_issues(seen_bin_to_items))
            
            # Check 5: Missing expected items
            anomalies.extend(self._check_missing_items(allocations, seen_item_to_bin))
            
            # Save anomalies
            saved_anomalies = self._save_anomalies(anomalies, target_date)
            
            self.db.commit()
            
            summary = {
                "date": target_date.isoformat(),
                "total_anomalies": len(saved_anomalies),
                "anomaly_types": self._count_anomaly_types(saved_anomalies),
                "orders_checked": len(orders),
                "snapshots_processed": len(snapshots),
                "bins_scanned": len(seen_bin_to_items)
            }
            
            logger.info(f"Reconciliation completed: {summary}")
            return summary
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in reconciliation: {e}")
            raise
    
    def _get_orders_for_date(self, target_date: date) -> List[Order]:
        """Get orders that should have shipped on target date"""
        return (
            self.db.query(Order)
            .filter(Order.ship_date == target_date)
            .all()
        )
    
    def _get_latest_allocations(self) -> Dict[str, str]:
        """Get latest allocation per item_id"""
        allocations = self.db.query(Allocation).all()
        return {alloc.item_id: alloc.bin_id for alloc in allocations}
    
    def _get_last_snapshots_before(self, cutoff_datetime: datetime) -> List[Snapshot]:
        """Get last snapshot per bin before cutoff time"""
        from sqlalchemy import func
        
        # Convert date to datetime if needed
        if isinstance(cutoff_datetime, date):
            cutoff_datetime = datetime.combine(cutoff_datetime, datetime.min.time())
        
        # Get latest snapshot per bin
        subquery = (
            self.db.query(
                Snapshot.bin_id,
                func.max(Snapshot.ts).label('max_ts')
            )
            .filter(
                Snapshot.bin_id.isnot(None),
                Snapshot.ts < cutoff_datetime
            )
            .group_by(Snapshot.bin_id)
            .subquery()
        )
        
        snapshots = (
            self.db.query(Snapshot)
            .join(
                subquery,
                (Snapshot.bin_id == subquery.c.bin_id) & 
                (Snapshot.ts == subquery.c.max_ts)
            )
            .all()
        )
        
        return snapshots
    
    def _index_seen_items(self, snapshots: List[Snapshot]) -> Dict[str, str]:
        """Build index of item_id -> bin_id from snapshots"""
        seen_items = {}
        for snapshot in snapshots:
            if snapshot.item_ids and snapshot.bin_id:
                for item_id in snapshot.item_ids:
                    seen_items[item_id] = snapshot.bin_id
        return seen_items
    
    def _index_bin_items(self, snapshots: List[Snapshot]) -> Dict[str, List[str]]:
        """Build index of bin_id -> [item_ids] from snapshots"""
        bin_items = defaultdict(list)
        for snapshot in snapshots:
            if snapshot.item_ids and snapshot.bin_id:
                bin_items[snapshot.bin_id].extend(snapshot.item_ids)
        return dict(bin_items)
    
    def _check_unshipped_orders(
        self, 
        orders: List[Order], 
        seen_item_to_bin: Dict[str, str], 
        target_date: date
    ) -> List[Dict[str, Any]]:
        """Check for orders marked shipped but items still visible"""
        anomalies = []
        
        for order in orders:
            if order.status != "shipped":
                continue
                
            # Get items for this order
            item_ids = order.item_ids or self._get_items_by_sku(order.sku, order.qty)
            
            for item_id in item_ids:
                if item_id in seen_item_to_bin:
                    bin_seen = seen_item_to_bin[item_id]
                    anomaly = {
                        "type": "unshipped",
                        "order_id": order.order_id,
                        "item_id": item_id,
                        "bin_id": bin_seen,
                        "severity": "high",
                        "detail": f"Order {order.order_id} marked shipped but item {item_id} still seen at {bin_seen}"
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _check_misplaced_items(
        self, 
        allocations: Dict[str, str], 
        seen_item_to_bin: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Check for items in wrong bins"""
        anomalies = []
        
        for item_id, expected_bin in allocations.items():
            if item_id in seen_item_to_bin:
                actual_bin = seen_item_to_bin[item_id]
                if actual_bin != expected_bin:
                    anomaly = {
                        "type": "misplaced",
                        "item_id": item_id,
                        "bin_id": actual_bin,
                        "severity": "med",
                        "detail": f"Item {item_id} expected in {expected_bin}, found in {actual_bin}"
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _check_orphan_items(self, seen_item_to_bin: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for items not in system"""
        anomalies = []
        
        # Get all known item_ids from database
        known_items = set()
        items = self.db.query(Item.item_id).all()
        known_items.update([item.item_id for item in items])
        
        for item_id, bin_id in seen_item_to_bin.items():
            if item_id not in known_items:
                anomaly = {
                    "type": "orphan",
                    "item_id": item_id,
                    "bin_id": bin_id,
                    "severity": "med",
                    "detail": f"Item {item_id} seen in {bin_id} but not found in system"
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _check_staging_issues(self, seen_bin_to_items: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Check for staging area issues"""
        anomalies = []
        staging_bins = settings.staging_bins_list
        threshold_hours = settings.staging_threshold_hours
        
        for bin_id in staging_bins:
            if bin_id in seen_bin_to_items:
                for item_id in seen_bin_to_items[bin_id]:
                    # Check how long item has been in staging
                    hours_in_staging = self._get_hours_in_bin(item_id, bin_id)
                    if hours_in_staging > threshold_hours:
                        anomaly = {
                            "type": "stale_staging",
                            "item_id": item_id,
                            "bin_id": bin_id,
                            "severity": "high",
                            "detail": f"Item {item_id} in staging {bin_id} for {hours_in_staging:.1f}h (>{threshold_hours}h)"
                        }
                        anomalies.append(anomaly)
        
        return anomalies
    
    def _check_missing_items(
        self, 
        allocations: Dict[str, str], 
        seen_item_to_bin: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Check for allocated items not seen in snapshots"""
        anomalies = []
        
        for item_id, expected_bin in allocations.items():
            if item_id not in seen_item_to_bin:
                # Only flag as missing if the bin was actually scanned
                if self._was_bin_scanned(expected_bin):
                    anomaly = {
                        "type": "missing",
                        "item_id": item_id,
                        "bin_id": expected_bin,
                        "severity": "med",
                        "detail": f"Item {item_id} allocated to {expected_bin} but not seen in recent snapshots"
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _get_items_by_sku(self, sku: str, qty: int) -> List[str]:
        """Get item_ids for SKU (fallback when order doesn't specify items)"""
        items = (
            self.db.query(Item.item_id)
            .filter(Item.sku == sku)
            .limit(qty)
            .all()
        )
        return [item.item_id for item in items]
    
    def _get_hours_in_bin(self, item_id: str, bin_id: str) -> float:
        """Get hours since item was first seen in bin"""
        # Find first snapshot of this item in this bin
        first_snapshot = (
            self.db.query(Snapshot)
            .filter(
                Snapshot.bin_id == bin_id,
                Snapshot.item_ids.contains([item_id])
            )
            .order_by(Snapshot.ts.asc())
            .first()
        )
        
        if first_snapshot:
            delta = datetime.now() - first_snapshot.ts
            return delta.total_seconds() / 3600
        
        return 0.0
    
    def _was_bin_scanned(self, bin_id: str) -> bool:
        """Check if bin was scanned recently"""
        recent_snapshot = (
            self.db.query(Snapshot)
            .filter(
                Snapshot.bin_id == bin_id,
                Snapshot.ts >= datetime.now() - timedelta(days=1)
            )
            .first()
        )
        return recent_snapshot is not None
    
    def _save_anomalies(self, anomalies: List[Dict[str, Any]], target_date: date) -> List[Anomaly]:
        """Save anomalies to database"""
        saved_anomalies = []
        
        for anomaly_data in anomalies:
            anomaly = Anomaly(**anomaly_data)
            self.db.add(anomaly)
            saved_anomalies.append(anomaly)
        
        return saved_anomalies
    
    def _count_anomaly_types(self, anomalies: List[Anomaly]) -> Dict[str, int]:
        """Count anomalies by type"""
        counts = defaultdict(int)
        for anomaly in anomalies:
            counts[anomaly.type] += 1
        return dict(counts)
    
    def get_anomalies_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get anomalies for specific date"""
        try:
            anomalies = (
                self.db.query(Anomaly)
                .filter(
                    Anomaly.ts >= target_date,
                    Anomaly.ts < target_date + timedelta(days=1)
                )
                .order_by(Anomaly.severity.desc(), Anomaly.ts.desc())
                .all()
            )
            
            results = []
            for anomaly in anomalies:
                result = {
                    "id": anomaly.id,
                    "ts": anomaly.ts,
                    "type": anomaly.type,
                    "bin_id": anomaly.bin_id,
                    "item_id": anomaly.item_id,
                    "order_id": anomaly.order_id,
                    "severity": anomaly.severity,
                    "detail": anomaly.detail,
                    "status": anomaly.status
                }
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting anomalies: {e}")
            return []


def create_reconciliation_service(db: Session) -> ReconciliationService:
    """Factory function to create reconciliation service"""
    return ReconciliationService(db)