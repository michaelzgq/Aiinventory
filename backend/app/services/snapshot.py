"""
Snapshot Service for Inventory AI
处理拍照→解析→生成快照的完整流程
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Snapshot, Item, Bin
from ..utils.qr import detect_codes_from_image, validate_qr_content
from ..utils.ocr import recognize_bin_from_image_data, extract_bin_id_from_text
from ..utils.storage import save_image_file, get_image_url
from ..config import settings

logger = logging.getLogger(__name__)


class SnapshotService:
    """快照服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_snapshot_upload(self, 
                               image_data: bytes, 
                               bin_id: Optional[str] = None,
                               notes: Optional[str] = None,
                               enhance_image: bool = True) -> Dict[str, Any]:
        """
        处理快照上传
        
        Args:
            image_data: 图像数据
            bin_id: 库位号（可选，如果不提供则通过 OCR 识别）
            notes: 备注信息
            enhance_image: 是否进行图像增强
            
        Returns:
            处理结果
        """
        try:
            logger.info(f"开始处理快照上传，图像大小: {len(image_data)} bytes")
            
            # 1. 保存图像文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            photo_ref = save_image_file(image_data, filename, "photos")
            
            # 2. 识别库位号
            detected_bin_id = self._detect_bin_id(image_data, bin_id)
            
            # 3. 识别物品 QR 码
            detected_items = self._detect_items(image_data, enhance_image)
            
            # 4. 计算综合置信度
            confidence = self._calculate_confidence(detected_items, detected_bin_id)
            
            # 5. 创建快照记录
            snapshot = self._create_snapshot(
                bin_id=detected_bin_id,
                item_ids=[item['text'] for item in detected_items],
                photo_ref=photo_ref,
                confidence=confidence,
                notes=notes
            )
            
            # 6. 返回结果
            result = {
                "bin_id": detected_bin_id,
                "item_ids": [item['text'] for item in detected_items],
                "photo_ref": photo_ref,
                "confidence": confidence,
                "snapshot_id": snapshot.id,
                "timestamp": snapshot.ts.isoformat(),
                "detection_details": {
                    "qr_codes": detected_items,
                    "bin_detection": detected_bin_id is not None
                }
            }
            
            logger.info(f"快照处理完成: 库位 {detected_bin_id}, 物品 {len(detected_items)} 个, 置信度 {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"快照处理失败: {e}")
            raise
    
    def _detect_bin_id(self, image_data: bytes, provided_bin_id: Optional[str] = None) -> Optional[str]:
        """
        检测库位号
        
        Args:
            image_data: 图像数据
            provided_bin_id: 用户提供的库位号
            
        Returns:
            检测到的库位号
        """
        # 如果用户提供了库位号，直接使用
        if provided_bin_id:
            if self._validate_bin_id(provided_bin_id):
                logger.info(f"使用用户提供的库位号: {provided_bin_id}")
                return provided_bin_id
            else:
                logger.warning(f"用户提供的库位号格式无效: {provided_bin_id}")
        
        # 尝试 OCR 识别库位号
        try:
            ocr_results = recognize_bin_from_image_data(image_data, use_paddle_ocr=settings.use_paddle_ocr)
            
            if ocr_results:
                # 选择置信度最高的结果
                best_result = max(ocr_results, key=lambda x: x.get('confidence', 0))
                detected_bin_id = best_result.get('bin_id')
                
                if detected_bin_id and self._validate_bin_id(detected_bin_id):
                    logger.info(f"OCR 识别到库位号: {detected_bin_id}, 置信度: {best_result.get('confidence', 0):.2f}")
                    return detected_bin_id
                else:
                    logger.warning(f"OCR 识别的库位号格式无效: {detected_bin_id}")
            
            logger.info("未检测到有效的库位号")
            return None
            
        except Exception as e:
            logger.error(f"库位号识别失败: {e}")
            return None
    
    def _detect_items(self, image_data: bytes, enhance_image: bool = True) -> List[Dict[str, Any]]:
        """
        检测物品 QR 码
        
        Args:
            image_data: 图像数据
            enhance_image: 是否进行图像增强
            
        Returns:
            检测到的物品列表
        """
        try:
            # 使用 QR 检测器识别物品
            detected_codes = detect_codes_from_image(image_data, enhance=enhance_image)
            
            # 过滤有效的物品 ID
            valid_items = []
            for code in detected_codes:
                if validate_qr_content(code['text']):
                    valid_items.append(code)
                    logger.info(f"检测到有效物品: {code['text']}, 置信度: {code['confidence']:.2f}")
                else:
                    logger.info(f"检测到无效物品码: {code['text']}")
            
            return valid_items
            
        except Exception as e:
            logger.error(f"物品检测失败: {e}")
            return []
    
    def _validate_bin_id(self, bin_id: str) -> bool:
        """
        验证库位号格式
        
        Args:
            bin_id: 库位号
            
        Returns:
            格式是否有效
        """
        if not bin_id:
            return False
        
        # 检查是否为已知的出库区
        if bin_id in settings.staging_bins_list:
            return True
        
        # 检查标准格式：A54, B12, S-01
        import re
        if re.match(r'^[A-Z]\d{1,2}$', bin_id) or re.match(r'^S-\d{1,2}$', bin_id):
            return True
        
        return False
    
    def _calculate_confidence(self, detected_items: List[Dict[str, Any]], 
                            bin_id: Optional[str]) -> float:
        """
        计算综合置信度
        
        Args:
            detected_items: 检测到的物品列表
            bin_id: 库位号
            
        Returns:
            综合置信度 (0.0 - 1.0)
        """
        try:
            # 基础置信度
            base_confidence = 0.5
            
            # 库位号检测加分
            if bin_id:
                base_confidence += 0.2
            
            # 物品检测加分
            if detected_items:
                # 计算物品检测的平均置信度
                item_confidences = [item.get('confidence', 0.5) for item in detected_items]
                avg_item_confidence = sum(item_confidences) / len(item_confidences)
                base_confidence += avg_item_confidence * 0.3
            
            # 确保置信度在 0.0 - 1.0 范围内
            confidence = max(0.0, min(1.0, base_confidence))
            
            return confidence
            
        except Exception as e:
            logger.error(f"置信度计算失败: {e}")
            return 0.5
    
    def _create_snapshot(self, bin_id: Optional[str], item_ids: List[str], 
                        photo_ref: str, confidence: float, 
                        notes: Optional[str] = None) -> Snapshot:
        """
        创建快照记录
        
        Args:
            bin_id: 库位号
            item_ids: 物品 ID 列表
            photo_ref: 照片引用
            confidence: 置信度
            notes: 备注
            
        Returns:
            创建的快照记录
        """
        try:
            # 创建快照记录
            snapshot = Snapshot(
                ts=datetime.now(),
                bin_id=bin_id,
                item_ids=item_ids,
                photo_ref=photo_ref,
                conf=confidence
            )
            
            # 保存到数据库
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
            
            logger.info(f"快照记录创建成功: ID {snapshot.id}")
            return snapshot
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"快照记录创建失败: {e}")
            raise
    
    def get_current_inventory(self) -> List[Dict[str, Any]]:
        """
        获取当前库存状态
        
        Returns:
            库存状态列表
        """
        try:
            # 获取每个库位的最新快照
            from sqlalchemy import func
            
            latest_snapshots = (
                self.db.query(
                    Snapshot.bin_id,
                    func.max(Snapshot.ts).label('latest_ts')
                )
                .filter(Snapshot.bin_id.isnot(None))
                .group_by(Snapshot.bin_id)
                .subquery()
            )
            
            # 获取最新快照的详细信息
            current_inventory = (
                self.db.query(Snapshot)
                .join(
                    latest_snapshots,
                    (Snapshot.bin_id == latest_snapshots.c.bin_id) &
                    (Snapshot.ts == latest_snapshots.c.latest_ts)
                )
                .order_by(Snapshot.bin_id)
                .all()
            )
            
            # 转换为字典格式
            inventory_list = []
            for snapshot in current_inventory:
                inventory_item = {
                    "bin_id": snapshot.bin_id,
                    "item_ids": snapshot.item_ids or [],
                    "item_count": len(snapshot.item_ids or []),
                    "last_scanned": snapshot.ts.isoformat(),
                    "confidence": snapshot.conf,
                    "photo_url": get_image_url(snapshot.photo_ref) if snapshot.photo_ref else None
                }
                inventory_list.append(inventory_item)
            
            logger.info(f"获取当前库存状态: {len(inventory_list)} 个库位")
            return inventory_list
            
        except Exception as e:
            logger.error(f"获取当前库存状态失败: {e}")
            return []
    
    def get_snapshots_by_bin(self, bin_id: str, limit: int = 10) -> List[Snapshot]:
        """
        获取指定库位的快照历史
        
        Args:
            bin_id: 库位号
            limit: 限制数量
            
        Returns:
            快照列表
        """
        try:
            snapshots = (
                self.db.query(Snapshot)
                .filter(Snapshot.bin_id == bin_id)
                .order_by(Snapshot.ts.desc())
                .limit(limit)
                .all()
            )
            
            logger.info(f"获取库位 {bin_id} 的快照历史: {len(snapshots)} 条记录")
            return snapshots
            
        except Exception as e:
            logger.error(f"获取库位快照历史失败: {e}")
            return []
    
    def get_snapshots_by_date(self, date: datetime, limit: int = 100) -> List[Snapshot]:
        """
        获取指定日期的快照
        
        Args:
            date: 日期
            limit: 限制数量
            
        Returns:
            快照列表
        """
        try:
            from datetime import timedelta
            
            start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
            snapshots = (
                self.db.query(Snapshot)
                .filter(Snapshot.ts >= start_time, Snapshot.ts < end_time)
                .order_by(Snapshot.ts.desc())
                .limit(limit)
                .all()
            )
            
            logger.info(f"获取日期 {date.date()} 的快照: {len(snapshots)} 条记录")
            return snapshots
            
        except Exception as e:
            logger.error(f"获取日期快照失败: {e}")
            return []
    
    def delete_snapshot(self, snapshot_id: int) -> bool:
        """
        删除快照记录
        
        Args:
            snapshot_id: 快照 ID
            
        Returns:
            是否删除成功
        """
        try:
            snapshot = self.db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
            
            if not snapshot:
                logger.warning(f"快照记录不存在: {snapshot_id}")
                return False
            
            # 删除照片文件
            if snapshot.photo_ref:
                from ..utils.storage import storage_manager
                storage_manager.delete_file(snapshot.photo_ref)
            
            # 删除数据库记录
            self.db.delete(snapshot)
            self.db.commit()
            
            logger.info(f"快照记录删除成功: {snapshot_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"快照记录删除失败: {e}")
            return False


def create_snapshot_service(db: Session) -> SnapshotService:
    """创建快照服务实例"""
    return SnapshotService(db)