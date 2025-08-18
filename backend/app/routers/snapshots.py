"""
Snapshot Router for Inventory AI
提供拍照上传、查询、删除等 API 接口
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.snapshot import SnapshotService, create_snapshot_service
from ..models import Snapshot
from ..schemas import SnapshotResponse, SnapshotCreate, SnapshotList
from ..deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.post("/upload", response_model=Dict[str, Any])
async def upload_snapshot(
    photo: UploadFile = File(..., description="快照照片"),
    bin_id: Optional[str] = Form(None, description="库位号（可选，如果不提供则通过 OCR 识别）"),
    notes: Optional[str] = Form(None, description="备注信息"),
    enhance_image: bool = Form(True, description="是否进行图像增强"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    上传快照照片
    
    - **photo**: 快照照片文件
    - **bin_id**: 库位号（可选）
    - **notes**: 备注信息（可选）
    - **enhance_image**: 是否进行图像增强（默认开启）
    """
    try:
        # 验证文件类型
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图像文件")
        
        # 读取图像数据
        image_data = await photo.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="图像文件为空")
        
        # 验证文件大小（限制为 10MB）
        if len(image_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="图像文件过大，请上传小于 10MB 的文件")
        
        # 创建快照服务
        snapshot_service = create_snapshot_service(db)
        
        # 处理快照上传
        result = snapshot_service.process_snapshot_upload(
            image_data=image_data,
            bin_id=bin_id,
            notes=notes,
            enhance_image=enhance_image
        )
        
        logger.info(f"用户 {current_user} 上传快照成功: {result['snapshot_id']}")
        
        return {
            "success": True,
            "message": "快照上传成功",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"快照上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"快照上传失败: {str(e)}")


@router.get("/", response_model=SnapshotList)
async def get_snapshots(
    bin_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取快照列表
    
    - **bin_id**: 库位号过滤（可选）
    - **limit**: 限制数量（默认 50）
    - **offset**: 偏移量（默认 0）
    """
    try:
        snapshot_service = create_snapshot_service(db)
        
        if bin_id:
            # 获取指定库位的快照
            snapshots = snapshot_service.get_snapshots_by_bin(bin_id, limit=limit)
        else:
            # 获取所有快照
            from sqlalchemy.orm import Query
            query = db.query(Snapshot).order_by(Snapshot.ts.desc())
            snapshots = query.offset(offset).limit(limit).all()
        
        # 转换为响应格式
        snapshot_list = []
        for snapshot in snapshots:
            snapshot_data = {
                "id": snapshot.id,
                "ts": snapshot.ts,
                "bin_id": snapshot.bin_id,
                "item_ids": snapshot.item_ids or [],
                "photo_ref": snapshot.photo_ref,
                "conf": snapshot.conf,
                "notes": getattr(snapshot, 'notes', None)
            }
            snapshot_list.append(snapshot_data)
        
        logger.info(f"用户 {current_user} 获取快照列表: {len(snapshot_list)} 条记录")
        
        return SnapshotList(
            snapshots=snapshot_list,
            total=len(snapshot_list),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"获取快照列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取快照列表失败: {str(e)}")


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(
    snapshot_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取指定快照详情
    
    - **snapshot_id**: 快照 ID
    """
    try:
        snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        # 获取照片 URL
        from ..utils.storage import get_image_url
        photo_url = get_image_url(snapshot.photo_ref) if snapshot.photo_ref else None
        
        snapshot_data = {
            "id": snapshot.id,
            "ts": snapshot.ts,
            "bin_id": snapshot.bin_id,
            "item_ids": snapshot.item_ids or [],
            "photo_ref": snapshot.photo_ref,
            "photo_url": photo_url,
            "conf": snapshot.conf,
            "notes": getattr(snapshot, 'notes', None)
        }
        
        logger.info(f"用户 {current_user} 获取快照详情: {snapshot_id}")
        
        return SnapshotResponse(**snapshot_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取快照详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取快照详情失败: {str(e)}")


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    删除指定快照
    
    - **snapshot_id**: 快照 ID
    """
    try:
        snapshot_service = create_snapshot_service(db)
        
        success = snapshot_service.delete_snapshot(snapshot_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="快照不存在或删除失败")
        
        logger.info(f"用户 {current_user} 删除快照成功: {snapshot_id}")
        
        return {
            "success": True,
            "message": "快照删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除快照失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除快照失败: {str(e)}")


@router.get("/bin/{bin_id}/history")
async def get_bin_history(
    bin_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取指定库位的快照历史
    
    - **bin_id**: 库位号
    - **limit**: 限制数量（默认 20）
    """
    try:
        snapshot_service = create_snapshot_service(db)
        
        snapshots = snapshot_service.get_snapshots_by_bin(bin_id, limit=limit)
        
        # 转换为响应格式
        history_list = []
        for snapshot in snapshots:
            from ..utils.storage import get_image_url
            photo_url = get_image_url(snapshot.photo_ref) if snapshot.photo_ref else None
            
            history_item = {
                "id": snapshot.id,
                "ts": snapshot.ts,
                "item_ids": snapshot.item_ids or [],
                "photo_url": photo_url,
                "conf": snapshot.conf,
                "notes": getattr(snapshot, 'notes', None)
            }
            history_list.append(history_item)
        
        logger.info(f"用户 {current_user} 获取库位 {bin_id} 历史: {len(history_list)} 条记录")
        
        return {
            "bin_id": bin_id,
            "history": history_list,
            "total": len(history_list)
        }
        
    except Exception as e:
        logger.error(f"获取库位历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取库位历史失败: {str(e)}")


@router.get("/today/count")
async def get_today_snapshots_count(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取今日快照数量
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        count = db.query(func.count(Snapshot.id)).filter(
            Snapshot.ts >= today_start,
            Snapshot.ts < today_end
        ).scalar()
        
        logger.info(f"用户 {current_user} 获取今日快照数量: {count}")
        
        return {
            "date": today_start.date().isoformat(),
            "count": count
        }
        
    except Exception as e:
        logger.error(f"获取今日快照数量失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取今日快照数量失败: {str(e)}")


@router.get("/bins/today")
async def get_bins_scanned_today(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取今日扫描的库位数量
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # 统计今日扫描的唯一库位数量
        bin_count = db.query(func.count(func.distinct(Snapshot.bin_id))).filter(
            Snapshot.ts >= today_start,
            Snapshot.ts < today_end,
            Snapshot.bin_id.isnot(None)
        ).scalar()
        
        logger.info(f"用户 {current_user} 获取今日扫描库位数量: {bin_count}")
        
        return {
            "date": today_start.date().isoformat(),
            "count": bin_count
        }
        
    except Exception as e:
        logger.error(f"获取今日扫描库位数量失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取今日扫描库位数量失败: {str(e)}")


@router.get("/current/inventory")
async def get_current_inventory(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    获取当前库存状态
    """
    try:
        snapshot_service = create_snapshot_service(db)
        
        inventory = snapshot_service.get_current_inventory()
        
        logger.info(f"用户 {current_user} 获取当前库存状态: {len(inventory)} 个库位")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_bins": len(inventory),
            "total_items": sum(item.get('item_count', 0) for item in inventory),
            "inventory": inventory
        }
        
    except Exception as e:
        logger.error(f"获取当前库存状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取当前库存状态失败: {str(e)}")


@router.post("/bulk-upload")
async def bulk_upload_snapshots(
    photos: List[UploadFile] = File(..., description="快照照片列表"),
    bin_id: str = Form(..., description="库位号"),
    notes: Optional[str] = Form(None, description="备注信息"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    批量上传快照照片
    
    - **photos**: 快照照片文件列表
    - **bin_id**: 库位号
    - **notes**: 备注信息（可选）
    """
    try:
        if len(photos) == 0:
            raise HTTPException(status_code=400, detail="请选择至少一张照片")
        
        if len(photos) > 10:
            raise HTTPException(status_code=400, detail="一次最多上传 10 张照片")
        
        snapshot_service = create_snapshot_service(db)
        results = []
        
        for i, photo in enumerate(photos):
            try:
                # 验证文件类型
                if not photo.content_type or not photo.content_type.startswith('image/'):
                    logger.warning(f"跳过非图像文件: {photo.filename}")
                    continue
                
                # 读取图像数据
                image_data = await photo.read()
                
                if len(image_data) == 0:
                    logger.warning(f"跳过空文件: {photo.filename}")
                    continue
                
                # 处理快照上传
                result = snapshot_service.process_snapshot_upload(
                    image_data=image_data,
                    bin_id=bin_id,
                    notes=f"{notes} (第{i+1}张)" if notes else f"第{i+1}张照片",
                    enhance_image=True
                )
                
                results.append({
                    "photo_index": i + 1,
                    "filename": photo.filename,
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"处理第 {i+1} 张照片失败: {e}")
                results.append({
                    "photo_index": i + 1,
                    "filename": photo.filename,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        logger.info(f"用户 {current_user} 批量上传快照: {len(photos)} 张照片, 成功 {success_count} 张")
        
        return {
            "success": True,
            "message": f"批量上传完成，成功 {success_count}/{len(photos)} 张",
            "total_photos": len(photos),
            "successful_photos": success_count,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量上传快照失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量上传快照失败: {str(e)}")