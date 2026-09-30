"""
SQLAlchemy ORM 資料庫模型定義
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sno = Column(String(32), unique=True, index=True, nullable=False, doc="站點代號")
    sna = Column(String(128), index=True, nullable=False, doc="站點名稱 (中文)")
    sarea = Column(String(64), index=True, nullable=False, doc="行政區 (中文)")
    ar = Column(String(256), nullable=False, doc="地址 (中文)")
    
    snaen = Column(String(128), nullable=True, doc="站點名稱 (英文)")
    sareaen = Column(String(64), nullable=True, doc="行政區 (英文)")
    aren = Column(String(256), nullable=True, doc="地址 (英文)")
    
    act = Column(String(8), default="1", index=True, doc="營運狀態 (1: 營運中, 0: 暫停營運)")
    total_slots = Column(Integer, default=0, doc="總車位數 (Quantity)")
    available_rent_bikes = Column(Integer, default=0, doc="可借車輛數")
    available_return_bikes = Column(Integer, default=0, doc="可還車位數")
    
    latitude = Column(Float, nullable=False, doc="緯度")
    longitude = Column(Float, nullable=False, doc="經度")
    
    info_time = Column(String(64), nullable=True, doc="資訊來源時間")
    notes = Column(String(512), nullable=True, default="", doc="站點備註")
    
    created_at = Column(DateTime, default=datetime.utcnow, doc="系統建立時間")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="系統更新時間")

    __table_args__ = (
        Index("idx_station_coords", "latitude", "longitude"),
        Index("idx_station_sarea_act", "sarea", "act"),
    )

    def __repr__(self):
        return f"<Station sno={self.sno} sna={self.sna} sarea={self.sarea}>"
