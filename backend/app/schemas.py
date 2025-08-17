from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional, Any


class BinBase(BaseModel):
    bin_id: str
    zone: Optional[str] = None
    coords: Optional[str] = None


class BinCreate(BinBase):
    pass


class Bin(BinBase):
    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    item_id: str
    sku: str
    lot: Optional[str] = None
    customer_id: str


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    class Config:
        from_attributes = True


class AllocationBase(BaseModel):
    item_id: str
    bin_id: str
    status: str = "allocated"


class AllocationCreate(AllocationBase):
    pass


class Allocation(AllocationBase):
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SnapshotBase(BaseModel):
    bin_id: str
    item_ids: List[str]
    photo_ref: str
    ocr_text: Optional[str] = None
    conf: float


class SnapshotCreate(SnapshotBase):
    pass


class Snapshot(SnapshotBase):
    id: int
    ts: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    order_id: str
    ship_date: date
    sku: str
    qty: int
    item_ids: Optional[List[str]] = None
    status: str = "pending"


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    
    class Config:
        from_attributes = True


class MovementBase(BaseModel):
    item_id: str
    from_bin: Optional[str] = None
    to_bin: str
    op_id: Optional[str] = None


class MovementCreate(MovementBase):
    pass


class Movement(MovementBase):
    id: int
    ts: datetime
    
    class Config:
        from_attributes = True


class AnomalyBase(BaseModel):
    type: str
    bin_id: Optional[str] = None
    item_id: Optional[str] = None
    order_id: Optional[str] = None
    severity: str = "med"
    detail: str
    photo_ref: Optional[str] = None
    status: str = "open"


class AnomalyCreate(AnomalyBase):
    pass


class Anomaly(AnomalyBase):
    id: int
    ts: datetime
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    bin_id: str
    item_ids: List[str]
    photo_ref: str
    conf: float


class NLQRequest(BaseModel):
    text: str


class NLQResponse(BaseModel):
    answer: str
    data: Optional[Any] = None


class LabelGenerateRequest(BaseModel):
    item_ids: Optional[List[str]] = None
    count: Optional[int] = None