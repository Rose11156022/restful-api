"""
FastAPI 主應用程式核心進入點 (Main Entrypoint)
"""

import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import Station
from app.routers import stations, stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理：啟動時檢查資料庫並自動匯入資料"""
    # 建立資料表結構
    Base.metadata.create_all(bind=engine)
    
    # 檢查是否需要自動匯入初始 Open Data
    db: Session = SessionLocal()
    try:
        count = db.query(Station).count()
        if count == 0 and os.path.exists(settings.RAW_DATA_PATH):
            print(f"[*] 檢測到資料庫為空，正在從 {settings.RAW_DATA_PATH} 匯入 Open Data...")
            with open(settings.RAW_DATA_PATH, "r", encoding="utf-8") as f:
                raw_items = json.load(f)

            for item in raw_items:
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
                    notes="Open Data 初始匯入",
                )
                db.add(st)
            db.commit()
            print(f"[+] 資料庫初始匯入完成！共匯入 {len(raw_items)} 筆場站。")
        else:
            print(f"[*] 資料庫已就緒，目前包含 {count} 筆場站。")
    finally:
        db.close()

    yield
    print("[*] YouBike RESTful API 服務已安全關閉。")

tags_metadata = [
    {
        "name": "YouBike 場站管理 (Stations CRUD)",
        "description": "提供場站資源之查詢、新增、完整更新、局部修改、刪除與經緯度周邊搜尋。",
    },
    {
        "name": "行政區統計 (Districts)",
        "description": "統計各行政區之場站數、車位與車輛供應數據。",
    },
    {
        "name": "統計分析 (Statistics)",
        "description": "全台北市 YouBike 營運指標即時總覽。",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 設定 CORS 允許跨來源請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(stations.router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.stats_router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.districts_router, prefix=settings.API_V1_PREFIX)

@app.get("/", include_in_schema=False)
def root_redirect():
    """根路徑自動重導向至 Swagger 互動式 API 文件"""
    return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)

@app.get("/health", tags=["系統健康檢查"])
def health_check():
    """健康檢查端點，回傳 API 與資料庫狀態"""
    db = SessionLocal()
    try:
        count = db.query(Station).count()
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "database": "connected",
            "total_stations": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
