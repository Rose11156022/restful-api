"""
資料庫存取層 (CRUD - Create, Read, Update, Delete)
"""

import math
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc, case

from app.models import Station
from app.schemas import StationCreate, StationUpdate, StationPatch, StationResponse

def enrich_station(station: Station) -> dict:
    """計算衍生欄位並轉為 dict 格式相容於 StationResponse"""
    rate = 0.0
    if station.total_slots and station.total_slots > 0:
        rate = round((station.available_rent_bikes / station.total_slots) * 100, 1)

    status_text = "營運中" if station.act == "1" else "暫停營運"

    data = {
        "id": station.id,
        "sno": station.sno,
        "sna": station.sna,
        "sarea": station.sarea,
        "ar": station.ar,
        "snaen": station.snaen,
        "sareaen": station.sareaen,
        "aren": station.aren,
        "act": station.act,
        "total_slots": station.total_slots,
        "available_rent_bikes": station.available_rent_bikes,
        "available_return_bikes": station.available_return_bikes,
        "latitude": station.latitude,
        "longitude": station.longitude,
        "info_time": station.info_time,
        "notes": station.notes,
        "created_at": station.created_at,
        "updated_at": station.updated_at,
        "status_text": status_text,
        "available_rate": rate,
    }
    return data

def get_station_by_id(db: Session, station_id: int) -> Optional[Station]:
    return db.query(Station).filter(Station.id == station_id).first()

def get_station_by_sno(db: Session, sno: str) -> Optional[Station]:
    return db.query(Station).filter(Station.sno == sno).first()

def get_stations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    district: Optional[str] = None,
    keyword: Optional[str] = None,
    act: Optional[str] = None,
    min_available: Optional[int] = None,
    sort_by: str = "id",
    order: str = "asc"
) -> Tuple[List[Station], int]:
    """多條件篩選與分頁查詢場站列表"""
    query = db.query(Station)

    if district:
        query = query.filter(Station.sarea.like(f"%{district}%"))

    if keyword:
        kw_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Station.sna.like(kw_filter),
                Station.ar.like(kw_filter),
                Station.sno.like(kw_filter)
            )
        )

    if act is not None:
        query = query.filter(Station.act == act)

    if min_available is not None:
        query = query.filter(Station.available_rent_bikes >= min_available)

    # 排序邏輯
    sort_column = getattr(Station, sort_by, Station.id)
    if order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def create_station(db: Session, station_in: StationCreate) -> Station:
    """新增場站資源 (POST)"""
    # 若無 sno 則自動依時間戳與最大 id 產生唯一序號
    sno = station_in.sno
    if not sno:
        max_id = db.query(func.max(Station.id)).scalar() or 0
        sno = f"custom_{int(datetime.utcnow().timestamp())}_{max_id + 1}"

    db_station = Station(
        sno=sno,
        sna=station_in.sna,
        sarea=station_in.sarea,
        ar=station_in.ar,
        snaen=station_in.snaen,
        sareaen=station_in.sareaen,
        aren=station_in.aren,
        act=station_in.act,
        total_slots=station_in.total_slots,
        available_rent_bikes=station_in.available_rent_bikes,
        available_return_bikes=station_in.available_return_bikes,
        latitude=station_in.latitude,
        longitude=station_in.longitude,
        info_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        notes=station_in.notes or "",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

def update_station(db: Session, db_station: Station, station_in: StationUpdate) -> Station:
    """完整更新場站資源 (PUT)"""
    db_station.sna = station_in.sna
    db_station.sarea = station_in.sarea
    db_station.ar = station_in.ar
    db_station.snaen = station_in.snaen
    db_station.sareaen = station_in.sareaen
    db_station.aren = station_in.aren
    db_station.act = station_in.act
    db_station.total_slots = station_in.total_slots
    db_station.available_rent_bikes = station_in.available_rent_bikes
    db_station.available_return_bikes = station_in.available_return_bikes
    db_station.latitude = station_in.latitude
    db_station.longitude = station_in.longitude
    db_station.notes = station_in.notes or db_station.notes
    db_station.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_station)
    return db_station

def patch_station(db: Session, db_station: Station, station_in: StationPatch) -> Station:
    """部分更新場站資源 (PATCH)"""
    update_data = station_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_station, field):
            setattr(db_station, field, value)

    db_station.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_station)
    return db_station

def delete_station(db: Session, db_station: Station) -> None:
    """刪除場站資源 (DELETE)"""
    db.delete(db_station)
    db.commit()

def get_districts_summary(db: Session) -> List[dict]:
    """計算各行政區彙總統計"""
    results = db.query(
        Station.sarea.label("district"),
        func.count(Station.id).label("station_count"),
        func.sum(Station.total_slots).label("total_slots"),
        func.sum(Station.available_rent_bikes).label("total_available_bikes"),
        func.sum(Station.available_return_bikes).label("total_return_spaces"),
        func.sum(case((Station.act == "1", 1), else_=0)).label("active_station_count")
    ).group_by(Station.sarea).order_by(desc("station_count")).all()

    return [
        {
            "district": row.district,
            "station_count": row.station_count,
            "total_slots": int(row.total_slots or 0),
            "total_available_bikes": int(row.total_available_bikes or 0),
            "total_return_spaces": int(row.total_return_spaces or 0),
            "active_station_count": int(row.active_station_count or 0),
        }
        for row in results
    ]

def get_overview_stats(db: Session) -> dict:
    """全台北市總覽統計"""
    total_stations = db.query(Station).count()
    active_stations = db.query(Station).filter(Station.act == "1").count()
    suspended_stations = total_stations - active_stations

    totals = db.query(
        func.sum(Station.total_slots).label("total_capacity"),
        func.sum(Station.available_rent_bikes).label("total_available_bikes"),
        func.sum(Station.available_return_bikes).label("total_return_spaces"),
        func.count(func.distinct(Station.sarea)).label("districts_count")
    ).first()

    return {
        "total_stations": total_stations,
        "active_stations": active_stations,
        "suspended_stations": suspended_stations,
        "total_capacity": int(totals.total_capacity or 0) if totals else 0,
        "total_available_bikes": int(totals.total_available_bikes or 0) if totals else 0,
        "total_return_spaces": int(totals.total_return_spaces or 0) if totals else 0,
        "districts_count": int(totals.districts_count or 0) if totals else 0,
    }

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """計算兩經緯度點間的大圓距離 (公尺)"""
    R = 6371000  # 地球半徑 (公尺)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_nearby_stations(
    db: Session,
    latitude: float,
    longitude: float,
    radius_meters: float = 1000.0,
    limit: int = 10
) -> List[dict]:
    """根據經緯度搜尋半徑內的場站，依距離遞增排序"""
    # 先以經緯度大致範圍縮小查詢範圍（1度緯度約 111,000 公尺）
    lat_delta = (radius_meters / 111000.0) * 1.5
    lng_delta = (radius_meters / (111000.0 * math.cos(math.radians(latitude)))) * 1.5

    candidates = db.query(Station).filter(
        Station.latitude.between(latitude - lat_delta, latitude + lat_delta),
        Station.longitude.between(longitude - lng_delta, longitude + lng_delta)
    ).all()

    results = []
    for station in candidates:
        dist = calculate_haversine_distance(latitude, longitude, station.latitude, station.longitude)
        if dist <= radius_meters:
            station_dict = enrich_station(station)
            station_dict["distance_meters"] = round(dist, 1)
            results.append(station_dict)

    results.sort(key=lambda x: x["distance_meters"])
    return results[:limit]
