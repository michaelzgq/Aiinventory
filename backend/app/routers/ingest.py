"""
Data ingestion router for CSV file imports
支持 CSV 文件导入的路由
"""

import logging
import csv
import io
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Bin, Order, Allocation, Snapshot
from ..deps import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["ingest"])


def parse_csv_data(file_content: bytes) -> List[Dict[str, Any]]:
    """解析 CSV 文件内容"""
    try:
        # 解码文件内容
        content = file_content.decode('utf-8')
        
        # 使用 StringIO 创建文件对象
        csv_file = io.StringIO(content)
        reader = csv.DictReader(csv_file)
        
        # 转换为字典列表
        data = []
        for row in reader:
            # 清理空值
            cleaned_row = {k: v.strip() if v else None for k, v in row.items()}
            data.append(cleaned_row)
        
        return data
    except Exception as e:
        logger.error(f"CSV 解析失败: {e}")
        raise HTTPException(status_code=400, detail=f"CSV 解析失败: {str(e)}")


@router.post("/bins", response_model=Dict[str, Any])
async def ingest_bins(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """导入库位数据"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持 CSV 文件")
        
        # 读取文件内容
        content = await file.read()
        data = parse_csv_data(content)
        
        imported_count = 0
        errors = []
        
        for row in data:
            try:
                # 检查是否已存在
                existing_bin = db.query(Bin).filter(Bin.bin_id == row['bin_id']).first()
                if existing_bin:
                    # 更新现有记录
                    existing_bin.zone = row['zone']
                    existing_bin.coords = row['coords']
                    logger.info(f"更新库位: {row['bin_id']}")
                else:
                    # 创建新记录
                    new_bin = Bin(
                        bin_id=row['bin_id'],
                        zone=row['zone'],
                        coords=row['coords']
                    )
                    db.add(new_bin)
                    logger.info(f"创建库位: {row['bin_id']}")
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"行 {imported_count + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"导入库位失败 {error_msg}")
        
        # 提交事务
        db.commit()
        
        return {
            "message": "库位数据导入完成",
            "imported_count": imported_count,
            "total_rows": len(data),
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"库位导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"库位导入失败: {str(e)}")


@router.post("/orders", response_model=Dict[str, Any])
async def ingest_orders(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """导入订单数据"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持 CSV 文件")
        
        # 读取文件内容
        content = await file.read()
        data = parse_csv_data(content)
        
        imported_count = 0
        errors = []
        
        for row in data:
            try:
                # 检查是否已存在
                existing_order = db.query(Order).filter(Order.order_id == row['order_id']).first()
                if existing_order:
                    # 更新现有记录
                    existing_order.ship_date = row['ship_date']
                    existing_order.sku = row['sku']
                    existing_order.qty = int(row['qty'])
                    existing_order.item_ids = row['item_ids']
                    existing_order.status = row['status']
                    logger.info(f"更新订单: {row['order_id']}")
                else:
                    # 创建新记录
                    new_order = Order(
                        order_id=row['order_id'],
                        ship_date=row['ship_date'],
                        sku=row['sku'],
                        qty=int(row['qty']),
                        item_ids=row['item_ids'],
                        status=row['status']
                    )
                    db.add(new_order)
                    logger.info(f"创建订单: {row['order_id']}")
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"行 {imported_count + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"导入订单失败 {error_msg}")
        
        # 提交事务
        db.commit()
        
        return {
            "message": "订单数据导入完成",
            "imported_count": imported_count,
            "total_rows": len(data),
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"订单导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"订单导入失败: {str(e)}")


@router.post("/allocations", response_model=Dict[str, Any])
async def ingest_allocations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """导入分配数据"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持 CSV 文件")
        
        # 读取文件内容
        content = await file.read()
        data = parse_csv_data(content)
        
        imported_count = 0
        errors = []
        
        for row in data:
            try:
                # 检查是否已存在
                existing_allocation = db.query(Allocation).filter(
                    Allocation.item_id == row['item_id']
                ).first()
                
                if existing_allocation:
                    # 更新现有记录
                    existing_allocation.bin_id = row['bin_id']
                    existing_allocation.status = row['status']
                    logger.info(f"更新分配: {row['item_id']}")
                else:
                    # 创建新记录
                    new_allocation = Allocation(
                        item_id=row['item_id'],
                        bin_id=row['bin_id'],
                        status=row['status']
                    )
                    db.add(new_allocation)
                    logger.info(f"创建分配: {row['item_id']}")
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"行 {imported_count + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"导入分配失败 {error_msg}")
        
        # 提交事务
        db.commit()
        
        return {
            "message": "分配数据导入完成",
            "imported_count": imported_count,
            "total_rows": len(data),
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"分配导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"分配导入失败: {str(e)}")


@router.post("/snapshots", response_model=Dict[str, Any])
async def ingest_snapshots(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """导入快照数据"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持 CSV 文件")
        
        # 读取文件内容
        content = await file.read()
        data = parse_csv_data(content)
        
        imported_count = 0
        errors = []
        
        for row in data:
            try:
                # 检查是否已存在
                existing_snapshot = db.query(Snapshot).filter(
                    Snapshot.snapshot_id == int(row['snapshot_id'])
                ).first()
                
                if existing_snapshot:
                    # 更新现有记录
                    existing_snapshot.ts = row['ts']
                    existing_snapshot.bin_id = row['bin_id']
                    existing_snapshot.item_ids = row['item_ids']
                    existing_snapshot.photo_ref = row['photo_ref']
                    existing_snapshot.conf = float(row['conf'])
                    existing_snapshot.notes = row['notes']
                    logger.info(f"更新快照: {row['snapshot_id']}")
                else:
                    # 创建新记录
                    new_snapshot = Snapshot(
                        ts=row['ts'],
                        bin_id=row['bin_id'],
                        item_ids=row['item_ids'],
                        photo_ref=row['photo_ref'],
                        conf=float(row['conf']),
                        notes=row['notes']
                    )
                    db.add(new_snapshot)
                    logger.info(f"创建快照: {row['snapshot_id']}")
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"行 {imported_count + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"导入快照失败 {error_msg}")
        
        # 提交事务
        db.commit()
        
        return {
            "message": "快照数据导入完成",
            "imported_count": imported_count,
            "total_rows": len(data),
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"快照导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"快照导入失败: {str(e)}")
