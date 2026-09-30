"""
統計與行政區彙總分析 RESTful API 端點 (/api/v1/stats, /api/v1/districts)
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
import app.crud as crud
from app.schemas import DistrictSummary, OverviewStats

stats_router = APIRouter(
    prefix="/stats",
    tags=["統計分析 (Statistics)"]
)

districts_router = APIRouter(
    prefix="/districts",
    tags=["行政區統計 (Districts)"]
)

@stats_router.get(
    "/overview",
    response_model=OverviewStats,
    summary="取得全台北市 YouBike 營運總覽統計",
    description="統計全台北市之場站總數、營運中/暫停場站數、車輛與空位總容量及涵蓋行政區數量。"
)
def get_overview(db: Session = Depends(get_db)):
    return crud.get_overview_stats(db)

@districts_router.get(
    "",
    response_model=List[DistrictSummary],
    summary="取得各行政區場站與車輛統計",
    description="彙總台北市各行政區（如大安區、信義區、中山區等）之場站數量、車位數、可借車輛與可還車位。"
)
def get_districts(db: Session = Depends(get_db)):
    return crud.get_districts_summary(db)
