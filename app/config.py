"""
系統配置設定 (Configuration Settings)
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "youbike_raw.json")
DB_PATH = os.path.join(DATA_DIR, "youbike.db")

class Settings:
    PROJECT_NAME: str = "台北市 YouBike 2.0 開放資料 RESTful API 服務"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = """
## 台北市 YouBike 2.0 Open Data RESTful API 系統

本系統以台北市政府交通局 YouBike 2.0 即時開放資料為主題，採用 **Python + FastAPI + SQLite** 建構。
提供針對 YouBike 場站資源（Stations）之完整 **CRUD 操作**、分頁搜尋、經緯度周邊站點半徑查詢（Nearby）、以及行政區統計（Districts & Stats）。

### 主要功能特性：
* **Create (POST)**: 新增 YouBike 場站資源
* **Read (GET)**: 查詢場站清單（支援分頁、多條件篩選、關鍵字查詢）及單一站點詳細資訊
* **Update (PUT / PATCH)**: 提供完整更新 (PUT) 與局部修改 (PATCH)
* **Delete (DELETE)**: 刪除指定場站
* **Nearby Search**: 根據給定經緯度查詢半徑範圍內的 YouBike 站點與可借車輛數
* **Statistics**: 提供全台北市與各行政區（如大安區、信義區）之車位容量與車輛即時統計
* **API Documentation**: 自動產生符合 OpenAPI 3.0 標準之 Swagger UI 與 ReDoc 互動式文件
"""
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    RAW_DATA_PATH: str = RAW_DATA_PATH
    DB_PATH: str = DB_PATH

settings = Settings()
