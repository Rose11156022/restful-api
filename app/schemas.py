"""
Pydantic 請求與回應資料結構驗證模型 (Request/Response Schemas)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

class StationBase(BaseModel):
    sna: str = Field(..., min_length=2, max_length=128, description="場站中文名稱 (例: YouBike2.0_捷運科技大樓站)")
    sarea: str = Field(..., min_length=2, max_length=64, description="行政區 (例: 大安區)")
    ar: str = Field(..., min_length=2, max_length=256, description="中文地址 (例: 復興南路二段235號前)")
    
    snaen: Optional[str] = Field(None, max_length=128, description="場站英文名稱")
    sareaen: Optional[str] = Field(None, max_length=64, description="行政區英文名稱")
    aren: Optional[str] = Field(None, max_length=256, description="英文地址")
    
    act: str = Field(default="1", description="營運狀態 ('1': 正常營運, '0': 暫停營運)")
    total_slots: int = Field(default=20, ge=0, description="總車位數")
    available_rent_bikes: int = Field(default=10, ge=0, description="目前可借車輛數")
    available_return_bikes: int = Field(default=10, ge=0, description="目前可還空位數")
    
    latitude: float = Field(..., ge=-90.0, le=90.0, description="緯度 (Latitude)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="經度 (Longitude)")
    notes: Optional[str] = Field(default="", max_length=512, description="備註資訊")

    @field_validator("act")
    @classmethod
    def validate_act(cls, v: str) -> str:
        if v not in ("0", "1"):
            raise ValueError("營運狀態 act 必須為 '1' (正常營運) 或 '0' (暫停營運)")
        return v

class StationCreate(StationBase):
    sno: Optional[str] = Field(None, description="場站代號 (若未填寫系統將自動生成唯一代號)")

class StationUpdate(StationBase):
    """PUT 完整替換更新"""
    pass

class StationPatch(BaseModel):
    """PATCH 局部更新 (所有欄位皆可選)"""
    sna: Optional[str] = Field(None, min_length=2, max_length=128)
    sarea: Optional[str] = Field(None, min_length=2, max_length=64)
    ar: Optional[str] = Field(None, min_length=2, max_length=256)
    snaen: Optional[str] = None
    sareaen: Optional[str] = None
    aren: Optional[str] = None
    act: Optional[str] = None
    total_slots: Optional[int] = Field(None, ge=0)
    available_rent_bikes: Optional[int] = Field(None, ge=0)
    available_return_bikes: Optional[int] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    notes: Optional[str] = Field(None, max_length=512)

    @field_validator("act")
    @classmethod
    def validate_act(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("0", "1"):
            raise ValueError("營運狀態 act 必須為 '1' (正常營運) 或 '0' (暫停營運)")
        return v

class StationResponse(BaseModel):
    id: int
    sno: str
    sna: str
    sarea: str
    ar: str
    snaen: Optional[str] = None
    sareaen: Optional[str] = None
    aren: Optional[str] = None
    act: str
    total_slots: int
    available_rent_bikes: int
    available_return_bikes: int
    latitude: float
    longitude: float
    info_time: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 計算性欄位
    status_text: Optional[str] = None
    available_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class StationPaginationResponse(BaseModel):
    total: int = Field(..., description="總筆數")
    page: int = Field(..., description="目前頁數")
    page_size: int = Field(..., description="每頁筆數")
    total_pages: int = Field(..., description="總頁數")
    items: List[StationResponse] = Field(..., description="本頁場站資料清單")

class NearbyStationResponse(StationResponse):
    distance_meters: float = Field(..., description="距給定經緯度之直線距離 (公尺)")

class DistrictSummary(BaseModel):
    district: str = Field(..., description="行政區名稱")
    station_count: int = Field(..., description="站點總數")
    total_slots: int = Field(..., description="總車位數")
    total_available_bikes: int = Field(..., description="目前可借總車數")
    total_return_spaces: int = Field(..., description="目前可還總車位")
    active_station_count: int = Field(..., description="正常營運場站數")

class OverviewStats(BaseModel):
    total_stations: int = Field(..., description="總場站數")
    active_stations: int = Field(..., description="正常營運場站數")
    suspended_stations: int = Field(..., description="暫停營運場站數")
    total_capacity: int = Field(..., description="全市總車位數")
    total_available_bikes: int = Field(..., description="全市可借總車數")
    total_return_spaces: int = Field(..., description="全市可還總空位數")
    districts_count: int = Field(..., description="涵蓋行政區總數")

class MessageResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None
