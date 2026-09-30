"""
YouBike 場站資源 RESTful API 端點 (/api/v1/stations)
"""

import json
import os
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import Station
import app.crud as crud
from app.schemas import (
    StationCreate,
    StationUpdate,
    StationPatch,
    StationResponse,
    StationPaginationResponse,
    NearbyStationResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/stations",
    tags=["YouBike 場站管理 (Stations CRUD)"]
)

@router.get(
    "",
    response_model=StationPaginationResponse,
    summary="取得場站分頁列表與多條件搜尋",
    description="""
查詢 YouBike 2.0 場站清單，支援分頁、關鍵字搜尋（站名/地址/編號）、行政區過濾、營運狀態及最小可借車輛數篩選。
"""
)
def list_stations(
    page: int = Query(1, ge=1, description="頁碼 (從 1 開始)"),
    page_size: int = Query(20, ge=1, le=100, description="每頁筆數 (預設 20，上限 100)"),
    district: Optional[str] = Query(None, description="行政區名稱過濾 (例: 大安區, 信義區)"),
    keyword: Optional[str] = Query(None, description="關鍵字搜尋 (模糊搜尋站名、地址或代號)"),
    act: Optional[str] = Query(None, pattern="^[01]$", description="營運狀態 ('1': 營運中, '0': 暫停營運)"),
    min_available: Optional[int] = Query(None, ge=0, description="篩選至少有多少輛可借單車"),
    sort_by: str = Query("id", pattern="^(id|sno|total_slots|available_rent_bikes|available_return_bikes)$", description="排序欄位"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="排序方向 (asc: 遞增, desc: 遞減)"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    items, total = crud.get_stations(
        db=db,
        skip=skip,
        limit=page_size,
        district=district,
        keyword=keyword,
        act=act,
        min_available=min_available,
        sort_by=sort_by,
        order=order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    enriched_items = [crud.enrich_station(st) for st in items]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": enriched_items
    }

@router.get(
    "/nearby",
    response_model=List[NearbyStationResponse],
    summary="經緯度周邊場站查詢 (Nearby)",
    description="給定經緯度座標與半徑 (公尺)，計算並回傳周邊最近的 YouBike 場站資訊與直線距離。"
)
def get_nearby_stations(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="中心點緯度 (例: 25.02605)"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="中心點經度 (例: 121.54360)"),
    radius: float = Query(1000.0, ge=50.0, le=10000.0, description="搜尋半徑 (公尺，預設 1000m)"),
    limit: int = Query(10, ge=1, le=50, description="最多回傳筆數 (預設 10)"),
    db: Session = Depends(get_db)
):
    results = crud.get_nearby_stations(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius,
        limit=limit
    )
    return results

@router.get(
    "/{station_id}",
    response_model=StationResponse,
    summary="取得單一場站詳細資訊 (Read)",
    description="傳入場站 ID (整數) 或站點代號 sno (字串) 查詢場站詳細內容與即時可用率。"
)
def get_station(
    station_id: str = Path(..., description="場站內部 ID (數字) 或 站點代號 sno (例: 500101001)"),
    db: Session = Depends(get_db)
):
    station = None
    if station_id.isdigit():
        station = crud.get_station_by_id(db, int(station_id))
    if not station:
        station = crud.get_station_by_sno(db, station_id)

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到指定的場站 (ID/SNO: {station_id})"
        )

    return crud.enrich_station(station)

@router.post(
    "",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增場站資源 (Create)",
    description="新增一筆 YouBike 場站資料。若未指定場站代號 sno，系統將自動產生唯一代號。"
)
def create_station(
    station_in: StationCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    # 若有指定 sno，檢查是否重複
    if station_in.sno:
        existing = crud.get_station_by_sno(db, station_in.sno)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"場站代號 {station_in.sno} 已存在，不可重複建立。"
            )

    station = crud.create_station(db, station_in)
    response.headers["Location"] = f"/api/v1/stations/{station.id}"
    return crud.enrich_station(station)

@router.put(
    "/{station_id}",
    response_model=StationResponse,
    summary="完整更新場站資訊 (Update - PUT)",
    description="完整替換指定的場站資料。若欄位缺失將觸發驗證錯誤。"
)
def update_station(
    station_in: StationUpdate,
    station_id: str = Path(..., description="場站內部 ID 或 sno"),
    db: Session = Depends(get_db)
):
    station = None
    if station_id.isdigit():
        station = crud.get_station_by_id(db, int(station_id))
    if not station:
        station = crud.get_station_by_sno(db, station_id)

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"無法更新：找不到場站 (ID/SNO: {station_id})"
        )

    updated = crud.update_station(db, station, station_in)
    return crud.enrich_station(updated)

@router.patch(
    "/{station_id}",
    response_model=StationResponse,
    summary="局部更新場站資訊 (Update - PATCH)",
    description="局部修改場站部分屬性（例如：單獨調整可借車輛數、更新備註或改變營運狀態）。"
)
def patch_station(
    station_in: StationPatch,
    station_id: str = Path(..., description="場站內部 ID 或 sno"),
    db: Session = Depends(get_db)
):
    station = None
    if station_id.isdigit():
        station = crud.get_station_by_id(db, int(station_id))
    if not station:
        station = crud.get_station_by_sno(db, station_id)

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"無法更新：找不到場站 (ID/SNO: {station_id})"
        )

    patched = crud.patch_station(db, station, station_in)
    return crud.enrich_station(patched)

@router.delete(
    "/{station_id}",
    response_model=MessageResponse,
    summary="刪除場站資源 (Delete)",
    description="永久刪除指定之場站資源。"
)
def delete_station(
    station_id: str = Path(..., description="場站內部 ID 或 sno"),
    db: Session = Depends(get_db)
):
    station = None
    if station_id.isdigit():
        station = crud.get_station_by_id(db, int(station_id))
    if not station:
        station = crud.get_station_by_sno(db, station_id)

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"無法刪除：找不到場站 (ID/SNO: {station_id})"
        )

    deleted_sno = station.sno
    deleted_sna = station.sna
    crud.delete_station(db, station)

    return {
        "success": True,
        "message": f"場站 [{deleted_sno}] {deleted_sna} 已成功刪除。",
        "data": {"sno": deleted_sno, "sna": deleted_sna}
    }

@router.post(
    "/reset-database",
    response_model=MessageResponse,
    summary="重設資料庫為初始 Open Data (資料重置)",
    description="清空現有資料庫並從原始下載的 Open Data JSON 重新匯入，方便測試與重現。"
)
def reset_database(db: Session = Depends(get_db)):
    if not os.path.exists(settings.RAW_DATA_PATH):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"原始資料檔不存在: {settings.RAW_DATA_PATH}"
        )

    # 清空現有資料
    db.query(Station).delete()
    db.commit()

    with open(settings.RAW_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for item in data:
        st = Station(
            sno=str(item.get("sno")),
            sna=item.get("sna", ""),
            sarea=item.get("sarea", ""),
            ar=item.get("ar", ""),
            snaen=item.get("snaen"),
            sareaen=item.get("sareaen"),
            aren=item.get("aren"),
            act=str(item.get("act", "1")),
            total_slots=int(item.get("Quantity", 0)),
            available_rent_bikes=int(item.get("available_rent_bikes", 0)),
            available_return_bikes=int(item.get("available_return_bikes", 0)),
            latitude=float(item.get("latitude", 0.0)),
            longitude=float(item.get("longitude", 0.0)),
            info_time=item.get("infoTime"),
            notes="自原始 Open Data 重置匯入",
        )
        db.add(st)
        count += 1

    db.commit()
    return {
        "success": True,
        "message": f"資料庫已成功重設並重新匯入 {count} 筆 Open Data 場站！"
    }
