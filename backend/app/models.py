from sqlalchemy import Column, String, Integer, Float, DateTime, Date, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class Bin(Base):
    __tablename__ = "bins"
    
    bin_id = Column(String, primary_key=True)
    zone = Column(String, nullable=True)
    coords = Column(String, nullable=True)


class Item(Base):
    __tablename__ = "items"
    
    item_id = Column(String, primary_key=True)
    sku = Column(String, index=True)
    lot = Column(String, nullable=True)
    customer_id = Column(String, index=True)


class Allocation(Base):
    __tablename__ = "allocations"
    
    item_id = Column(String, ForeignKey("items.item_id"), primary_key=True)
    bin_id = Column(String, ForeignKey("bins.bin_id"))
    status = Column(String, default="allocated")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    item = relationship("Item")
    bin = relationship("Bin")


class Snapshot(Base):
    __tablename__ = "snapshots"
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, index=True, default=func.now())
    bin_id = Column(String, index=True)
    item_ids = Column(JSON)
    photo_ref = Column(String)
    ocr_text = Column(String)
    conf = Column(Float)


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String, index=True)
    ship_date = Column(Date)
    sku = Column(String)
    qty = Column(Integer)
    item_ids = Column(JSON, nullable=True)
    status = Column(String, default="pending")


class Movement(Base):
    __tablename__ = "movements"
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, index=True, default=func.now())
    item_id = Column(String, index=True)
    from_bin = Column(String)
    to_bin = Column(String)
    op_id = Column(String, nullable=True)


class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=func.now())
    type = Column(String)
    bin_id = Column(String, nullable=True)
    item_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    severity = Column(String, default="med")
    detail = Column(String)
    photo_ref = Column(String, nullable=True)
    status = Column(String, default="open")