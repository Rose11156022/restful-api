"""
手動初始化 SQLite 資料庫與匯入 Open Data 腳本
"""

import os
import sys
import json
from datetime import datetime

# 將專案根目錄加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import Station

def init_database():
    print("[*] 正在重設 SQLite 資料庫結構...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[+] 資料表 stations 已成功建立。")

    if not os.path.exists(settings.RAW_DATA_PATH):
        print(f"[-] 找不到 Open Data 原始檔案: {settings.RAW_DATA_PATH}")
        print("[*] 正在呼叫下載腳本...")
        from scripts.download_opendata import download_open_data
        download_open_data()

    print(f"[*] 正在從 {settings.RAW_DATA_PATH} 讀取資料...")
    with open(settings.RAW_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
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
                notes="Open Data 匯入",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(st)
            count += 1
            if count % 300 == 0:
                db.commit()
                print(f"[*] 已匯入 {count} 筆...")

        db.commit()
        print(f"[+] 資料庫初始化完成！成功匯入 {count} 筆 YouBike 2.0 場站資料至 SQLite: {settings.DB_PATH}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
