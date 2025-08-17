from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from ..models import Snapshot, Bin
from ..utils.qr import decode_image_bytes, filter_item_codes
from ..utils.ocr import extract_bin_from_image, is_valid_bin_id
from ..utils.storage import storage_manager

logger = logging.getLogger(__name__)


class SnapshotService:
    def __init__(self, db: Session):
        self.db = db
    
    def process_snapshot(
        self, 
        image_bytes: bytes, 
        bin_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a snapshot image and extract bin_id and item_ids"""
        try:
            # Step 1: Decode QR codes from image
            qr_codes, qr_confidence = decode_image_bytes(image_bytes)
            item_ids = filter_item_codes(qr_codes)
            
            # Step 2: Extract bin_id if not provided
            detected_bin_id = bin_id
            ocr_text = ""
            ocr_confidence = 0.0
            
            if not detected_bin_id:
                detected_bin_id, ocr_confidence = extract_bin_from_image(image_bytes)
                if detected_bin_id and is_valid_bin_id(detected_bin_id):
                    ocr_text = detected_bin_id
                else:
                    detected_bin_id = None
            
            # Step 3: Calculate overall confidence
            overall_confidence = self._calculate_confidence(
                qr_confidence, ocr_confidence, len(item_ids), bool(detected_bin_id)
            )
            
            # Step 4: Save image to storage
            photo_ref = storage_manager.save_photo(image_bytes, detected_bin_id)
            
            # Step 5: Create snapshot record
            snapshot_data = {
                "bin_id": detected_bin_id,
                "item_ids": item_ids,
                "photo_ref": photo_ref,
                "ocr_text": ocr_text,
                "conf": overall_confidence
            }
            
            snapshot = Snapshot(**snapshot_data)
            self.db.add(snapshot)
            
            # Step 6: Ensure bin exists in database
            if detected_bin_id:
                existing_bin = self.db.query(Bin).filter(Bin.bin_id == detected_bin_id).first()
                if not existing_bin:
                    bin_obj = Bin(bin_id=detected_bin_id)
                    self.db.add(bin_obj)
            
            self.db.commit()
            
            return {
                "bin_id": detected_bin_id,
                "item_ids": item_ids,
                "photo_ref": photo_ref,
                "conf": overall_confidence,
                "snapshot_id": snapshot.id,
                "ocr_text": ocr_text,
                "notes": notes
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing snapshot: {e}")
            raise
    
    def process_multiple_snapshots(
        self, 
        images: List[bytes], 
        bin_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process multiple snapshot images and combine results"""
        try:
            all_item_ids = set()
            all_bin_ids = []
            photo_refs = []
            confidences = []
            
            for i, image_bytes in enumerate(images):
                try:
                    result = self.process_snapshot(image_bytes, bin_id, f"{notes} (frame {i+1})" if notes else f"Frame {i+1}")
                    
                    if result["item_ids"]:
                        all_item_ids.update(result["item_ids"])
                    
                    if result["bin_id"]:
                        all_bin_ids.append(result["bin_id"])
                    
                    photo_refs.append(result["photo_ref"])
                    confidences.append(result["conf"])
                
                except Exception as e:
                    logger.error(f"Error processing frame {i+1}: {e}")
                    continue
            
            # Determine consensus bin_id
            consensus_bin_id = self._get_consensus_bin_id(all_bin_ids)
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "bin_id": consensus_bin_id or bin_id,
                "item_ids": list(all_item_ids),
                "photo_refs": photo_refs,
                "conf": avg_confidence,
                "frames_processed": len(images),
                "successful_frames": len(confidences)
            }
        
        except Exception as e:
            logger.error(f"Error processing multiple snapshots: {e}")
            raise
    
    def get_latest_snapshots(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest snapshots with details"""
        try:
            snapshots = (
                self.db.query(Snapshot)
                .order_by(Snapshot.ts.desc())
                .limit(limit)
                .all()
            )
            
            results = []
            for snapshot in snapshots:
                result = {
                    "id": snapshot.id,
                    "ts": snapshot.ts,
                    "bin_id": snapshot.bin_id,
                    "item_ids": snapshot.item_ids or [],
                    "photo_url": storage_manager.get_file_url(snapshot.photo_ref) if snapshot.photo_ref else None,
                    "conf": snapshot.conf,
                    "ocr_text": snapshot.ocr_text
                }
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting latest snapshots: {e}")
            return []
    
    def get_bin_snapshots(self, bin_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get snapshots for specific bin"""
        try:
            snapshots = (
                self.db.query(Snapshot)
                .filter(Snapshot.bin_id == bin_id)
                .order_by(Snapshot.ts.desc())
                .limit(limit)
                .all()
            )
            
            results = []
            for snapshot in snapshots:
                result = {
                    "id": snapshot.id,
                    "ts": snapshot.ts,
                    "item_ids": snapshot.item_ids or [],
                    "photo_url": storage_manager.get_file_url(snapshot.photo_ref) if snapshot.photo_ref else None,
                    "conf": snapshot.conf,
                    "ocr_text": snapshot.ocr_text
                }
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting bin snapshots: {e}")
            return []
    
    def get_current_inventory(self) -> List[Dict[str, Any]]:
        """Get current inventory based on latest snapshots per bin"""
        try:
            # Get latest snapshot per bin
            from sqlalchemy import func
            
            subquery = (
                self.db.query(
                    Snapshot.bin_id,
                    func.max(Snapshot.ts).label('max_ts')
                )
                .filter(Snapshot.bin_id.isnot(None))
                .group_by(Snapshot.bin_id)
                .subquery()
            )
            
            latest_snapshots = (
                self.db.query(Snapshot)
                .join(
                    subquery,
                    (Snapshot.bin_id == subquery.c.bin_id) & 
                    (Snapshot.ts == subquery.c.max_ts)
                )
                .all()
            )
            
            inventory = []
            for snapshot in latest_snapshots:
                item = {
                    "bin_id": snapshot.bin_id,
                    "item_ids": snapshot.item_ids or [],
                    "last_seen": snapshot.ts,
                    "photo_ref": snapshot.photo_ref,
                    "photo_url": storage_manager.get_file_url(snapshot.photo_ref) if snapshot.photo_ref else None,
                    "confidence": snapshot.conf
                }
                inventory.append(item)
            
            return inventory
        
        except Exception as e:
            logger.error(f"Error getting current inventory: {e}")
            return []
    
    def _calculate_confidence(
        self, 
        qr_confidence: float, 
        ocr_confidence: float, 
        item_count: int, 
        has_bin_id: bool
    ) -> float:
        """Calculate overall confidence score"""
        # Base confidence from QR detection
        base_confidence = qr_confidence
        
        # Boost confidence if we found items
        if item_count > 0:
            base_confidence = min(1.0, base_confidence + (item_count * 0.1))
        
        # Boost confidence if we identified the bin
        if has_bin_id:
            base_confidence = min(1.0, base_confidence + 0.2)
        
        # Consider OCR confidence if available
        if ocr_confidence > 0:
            base_confidence = min(1.0, (base_confidence + ocr_confidence) / 2)
        
        return round(base_confidence, 2)
    
    def _get_consensus_bin_id(self, bin_ids: List[str]) -> Optional[str]:
        """Get consensus bin_id from multiple detections"""
        if not bin_ids:
            return None
        
        # Count occurrences of each bin_id
        from collections import Counter
        counter = Counter(bin_ids)
        
        # Return most common bin_id
        most_common = counter.most_common(1)
        return most_common[0][0] if most_common else None


def create_snapshot_service(db: Session) -> SnapshotService:
    """Factory function to create snapshot service"""
    return SnapshotService(db)