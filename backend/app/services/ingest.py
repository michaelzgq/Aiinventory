from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from ..models import Order, Allocation, Item, Bin
from ..utils.csv_io import parse_orders_csv, parse_allocations_csv, parse_bins_csv

logger = logging.getLogger(__name__)


class DataIngestService:
    def __init__(self, db: Session):
        self.db = db
    
    def import_orders(self, csv_content: str) -> Dict[str, Any]:
        """Import orders from CSV content"""
        try:
            orders_data = parse_orders_csv(csv_content)
            
            imported_count = 0
            updated_count = 0
            errors = []
            
            for order_data in orders_data:
                try:
                    # Check if order already exists
                    existing_order = self.db.query(Order).filter(
                        Order.order_id == order_data['order_id'],
                        Order.sku == order_data['sku']
                    ).first()
                    
                    if existing_order:
                        # Update existing order
                        for key, value in order_data.items():
                            if hasattr(existing_order, key):
                                setattr(existing_order, key, value)
                        updated_count += 1
                    else:
                        # Create new order
                        order = Order(**order_data)
                        self.db.add(order)
                        imported_count += 1
                        
                        # Create items if they don't exist
                        if order_data.get('item_ids'):
                            for item_id in order_data['item_ids']:
                                existing_item = self.db.query(Item).filter(Item.item_id == item_id).first()
                                if not existing_item:
                                    item = Item(
                                        item_id=item_id,
                                        sku=order_data['sku'],
                                        customer_id="default"  # Could be extracted from order_id or set separately
                                    )
                                    self.db.add(item)
                
                except Exception as e:
                    error_msg = f"Error processing order {order_data.get('order_id', 'unknown')}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            self.db.commit()
            
            return {
                "imported": imported_count,
                "updated": updated_count,
                "errors": errors,
                "total_processed": len(orders_data)
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing orders: {e}")
            raise
    
    def import_allocations(self, csv_content: str) -> Dict[str, Any]:
        """Import allocations from CSV content"""
        try:
            allocations_data = parse_allocations_csv(csv_content)
            
            imported_count = 0
            updated_count = 0
            errors = []
            
            for alloc_data in allocations_data:
                try:
                    # Check if allocation already exists
                    existing_alloc = self.db.query(Allocation).filter(
                        Allocation.item_id == alloc_data['item_id']
                    ).first()
                    
                    if existing_alloc:
                        # Update existing allocation
                        existing_alloc.bin_id = alloc_data['bin_id']
                        existing_alloc.status = alloc_data['status']
                        updated_count += 1
                    else:
                        # Create new allocation
                        allocation = Allocation(**alloc_data)
                        self.db.add(allocation)
                        imported_count += 1
                    
                    # Ensure item exists
                    item = self.db.query(Item).filter(Item.item_id == alloc_data['item_id']).first()
                    if not item:
                        # Create placeholder item
                        item = Item(
                            item_id=alloc_data['item_id'],
                            sku="UNKNOWN",
                            customer_id="default"
                        )
                        self.db.add(item)
                    
                    # Ensure bin exists
                    bin_obj = self.db.query(Bin).filter(Bin.bin_id == alloc_data['bin_id']).first()
                    if not bin_obj:
                        bin_obj = Bin(bin_id=alloc_data['bin_id'])
                        self.db.add(bin_obj)
                
                except Exception as e:
                    error_msg = f"Error processing allocation {alloc_data.get('item_id', 'unknown')}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            self.db.commit()
            
            return {
                "imported": imported_count,
                "updated": updated_count,
                "errors": errors,
                "total_processed": len(allocations_data)
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing allocations: {e}")
            raise
    
    def import_bins(self, csv_content: str) -> Dict[str, Any]:
        """Import bins from CSV content"""
        try:
            bins_data = parse_bins_csv(csv_content)
            
            imported_count = 0
            updated_count = 0
            errors = []
            
            for bin_data in bins_data:
                try:
                    # Check if bin already exists
                    existing_bin = self.db.query(Bin).filter(Bin.bin_id == bin_data['bin_id']).first()
                    
                    if existing_bin:
                        # Update existing bin
                        for key, value in bin_data.items():
                            if hasattr(existing_bin, key) and value is not None:
                                setattr(existing_bin, key, value)
                        updated_count += 1
                    else:
                        # Create new bin
                        bin_obj = Bin(**bin_data)
                        self.db.add(bin_obj)
                        imported_count += 1
                
                except Exception as e:
                    error_msg = f"Error processing bin {bin_data.get('bin_id', 'unknown')}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            self.db.commit()
            
            return {
                "imported": imported_count,
                "updated": updated_count,
                "errors": errors,
                "total_processed": len(bins_data)
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing bins: {e}")
            raise
    
    def get_import_summary(self) -> Dict[str, int]:
        """Get summary of imported data"""
        try:
            summary = {
                "total_orders": self.db.query(Order).count(),
                "total_items": self.db.query(Item).count(),
                "total_bins": self.db.query(Bin).count(),
                "total_allocations": self.db.query(Allocation).count()
            }
            return summary
        
        except Exception as e:
            logger.error(f"Error getting import summary: {e}")
            return {}


def create_ingest_service(db: Session) -> DataIngestService:
    """Factory function to create ingest service"""
    return DataIngestService(db)