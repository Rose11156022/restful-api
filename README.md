# 台北市 YouBike 2.0 Open Data RESTful API 服務系統

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Swagger](https://img.shields.io/badge/Docs-Swagger%20UI-brightgreen.svg)](http://127.0.0.1:8000/docs)
[![Tests](https://img.shields.io/badge/Pytest-12%20Passed%20(100%25)-success.svg)](tests/test_api.py)

本專案為 **「物聯網應用程式開發 (IoTApp)」** 課程作業——**Open Data RESTful API 實作**。
從政府開放資料平台下載 **「台北市 YouBike 2.0 即時場站資訊」**，儲存為單一 JSON 檔案並匯入 SQLite 資料庫建立索引，利用 **AI 輔助開發工具 (Google DeepMind Antigravity / Gemini 3.8)** 設計符合 RESTful 標準的 API 規格，並以 **Python + FastAPI** 實作完整的 RESTful API Server，提供 Client 進行標準 **CRUD (Create, Read, Update, Delete)** 與周邊地理查詢等進階功能。

---

## 目錄 (Table of Contents)

1. [Open Data 資料來源與說明](#1-open-data-資料來源與說明)
2. [系統技術架構與目錄結構](#2-系統技術架構與目錄結構)
3. [RESTful API 規格一覽](#3-restful-api-規格一覽)
4. [Online API Documentation (Swagger UI)](#4-online-api-documentation)
5. [環境建置與快速執行指南](#5-環境建置與快速執行指南)
6. [API Client 測試與驗證工具](#6-api-client-測試與驗證工具)
   - [Python API Client 實測展示](#1-使用-python-api-client)
   - [Pytest 自動化端對端測試](#2-執行-pytest-自動化測試)
   - [Postman 測試集合匯入](#3-使用-postman-測試集合)
   - [Bruno API Client 測試](#4-使用-bruno-api-client)
7. [實測範例 (Request & Response)](#7-實測範例-request--response)
8. [AI 輔助開發成果與紀錄](#8-ai-輔助開發成果與紀錄)
9. [作業繳交檢核清單與 Email 格式](#9-作業繳交檢核清單與-email-格式)

---

## 1. Open Data 資料來源與說明

* **資料集名稱**：台北市公共自行車 YouBike 2.0 即時資訊
* **資料來源機關**：台北市政府交通局 / 台北市政府資料開放平台
* **開放資料來源 URL**：[https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json](https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json)
* **單一資料檔案存放路徑**：[`data/youbike_raw.json`](file:///d:/restful%20api/data/youbike_raw.json) (共收錄 1,808 筆即時場站資料，大小約 1.16 MB)
* **資料庫存放路徑**：[`data/youbike.db`](file:///d:/restful%20api/data/youbike.db) (SQLite 關聯式資料庫)

### 資料主要欄位定義：
| 欄位名稱 | 型別 | 說明 | 範例 |
| :--- | :--- | :--- | :--- |
| `sno` | String | 場站代號 (Station ID) | `500101001` |
| `sna` | String | 場站中文名稱 | `YouBike2.0_捷運科技大樓站` |
| `sarea` | String | 場站行政區 | `大安區` |
| `ar` | String | 場站詳細地址 | `復興南路二段235號前` |
| `act` | String | 營運狀態代碼 | `1` (正常營運), `0` (暫停營運) |
| `total_slots` | Integer | 總停車格數 (Quantity) | `28` |
| `available_rent_bikes` | Integer | 目前可借單車數 | `7` |
| `available_return_bikes` | Integer | 目前可還空位數 | `21` |
| `latitude` | Float | 緯度座標 | `25.02605` |
| `longitude` | Float | 經度座標 | `121.54360` |
| `status_text` | String | 營運狀態文字 (衍生計算) | `營運中` |
| `available_rate` | Float | 單車可用率百分比 (衍生計算) | `25.0%` |

---

## 2. 系統技術架構與目錄結構

### 核心技術堆疊
* **後端框架**：FastAPI (高效能非同步 ASGI 框架，原生支援 OpenAPI 規範)
* **ASGI 伺服器**：Uvicorn
* **資料庫 ORM**：SQLAlchemy 2.0
* **資料庫引擎**：SQLite 3 (輕量且兼具 ACID 交易特性的關聯式資料庫)
* **資料驗證與序列化**：Pydantic V2
* **測試框架**：Pytest, HTTPX, Requests

### 專案目錄結構
```text
d:/restful api/
├── app/
│   ├── __init__.py
│   ├── config.py              # 系統配置與環境變數管理
│   ├── database.py            # SQLite 連線與 Session 相依注入
│   ├── models.py              # SQLAlchemy 關聯資料庫模型
│   ├── schemas.py             # Pydantic V2 請求與回應驗證模型
│   ├── crud.py                # 抽象化資料庫操作層 (CRUD + 距離計算)
│   └── routers/
│       ├── __init__.py
│       ├── stations.py        # /api/v1/stations 路由 (CRUD + Nearby)
│       └── stats.py           # /api/v1/stats 與 /api/v1/districts 統計路由
│   └── main.py                # FastAPI 核心應用實例與生命週期管理
├── data/
│   ├── youbike_raw.json       # 下載儲存的原始 Open Data 單一檔案
│   └── youbike.db             # 匯入完成的 SQLite 資料庫
├── scripts/
│   ├── download_opendata.py   # 自動自開放資料平台下載 JSON
│   └── init_db.py             # 初始化資料庫並匯入資料
├── client/
│   └── api_client.py          # Python API Client (互動展示全套 CRUD)
├── tests/
│   ├── __init__.py
│   └── test_api.py            # Pytest 自動化端對端測試套件 (12/12 通過)
├── postman/
│   └── YouBike_RESTful_API.postman_collection.json  # Postman Collection 匯出檔
├── bruno/                     # Bruno 測試工具組態檔
│   ├── bruno.json
│   ├── 01_List_Stations.bru
│   ├── 02_Create_Station.bru
│   ├── 03_Get_Station.bru
│   └── 04_Delete_Station.bru
├── openapi.json               # 匯出之標準 OpenAPI 3.0 JSON 規格檔
├── API_EXAMPLES.md            # 詳細實測範例記錄檔
├── AI_ASSISTED_DEV.md         # AI 輔助開發歷程與 Prompt 紀錄
├── requirements.txt           # 專案相依套件清單
└── README.md                  # 專案完整說明文件
```

---

## 3. RESTful API 規格一覽

本系統完全符合 RESTful 設計架構，使用適當的 HTTP 動詞與狀態碼：

| HTTP Method | API Endpoint | 描述 | 成功狀態碼 |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | API 伺服器健康狀態檢查 | `200 OK` |
| `GET` | `/api/v1/stations` | **[Read]** 查詢場站清單 (支援分頁、關鍵字、行政區、排序) | `200 OK` |
| `GET` | `/api/v1/stations/{id}` | **[Read]** 依 ID 或 SNO 查詢單一場站詳細資訊 | `200 OK` |
| `POST` | `/api/v1/stations` | **[Create]** 新增 YouBike 場站資源 | `201 Created` |
| `PUT` | `/api/v1/stations/{id}` | **[Update]** 完整覆蓋更新指定場站資訊 | `200 OK` |
| `PATCH` | `/api/v1/stations/{id}` | **[Update]** 局部修改場站特定屬性 (如車位數、備註) | `200 OK` |
| `DELETE` | `/api/v1/stations/{id}` | **[Delete]** 刪除指定場站資源 | `200 OK` |
| `GET` | `/api/v1/stations/nearby` | **[Nearby]** 依經緯度與半徑查詢周邊場站與直線距離 | `200 OK` |
| `GET` | `/api/v1/districts` | **[Summary]** 查詢全台北市各行政區場站與車位統計 | `200 OK` |
| `GET` | `/api/v1/stats/overview` | **[Stats]** 查詢台北市 YouBike 營運總覽指標 | `200 OK` |
| `POST` | `/api/v1/stations/reset-database` | **[Maintenance]** 重設資料庫為初始 Open Data 狀態 | `200 OK` |

---

## 4. Online API Documentation

FastAPI 內建產生符合 OpenAPI 3.0 標準的線上互動式文件，啟動服務後即可直接在瀏覽器操作：

1. **Swagger UI 介面**：
   * 網址：`http://127.0.0.1:8000/docs`
   * 可直接於網頁介面上點擊 **「Try it out」** 發送請求測試各端點。
2. **ReDoc 介面**：
   * 網址：`http://127.0.0.1:8000/redoc`
   * 提供易於閱讀的排版風格。
3. **OpenAPI JSON 規格匯出**：
   * 靜態規格檔已匯出於專案根目錄之 [`openapi.json`](file:///d:/restful%20api/openapi.json)。

---

## 5. 環境建置與快速執行指南

### 步驟 1：安裝相依套件
在專案根目錄下開啟命令列執行：
```bash
pip install -r requirements.txt
```

### 步驟 2：(可選) 重新下載 Open Data 與初始化資料庫
> *專案已內建下載完成的資料與初始化完成的 SQLite 資料庫，此步驟亦可跳過。*
```bash
# 下載最新 Open Data
python scripts/download_opendata.py

# 初始化 SQLite 資料庫
python scripts/init_db.py
```

### 步驟 3：啟動 RESTful API Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
啟動成功後，終端機將顯示：
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
瀏覽器開啟 `http://127.0.0.1:8000/` 將自動跳轉至 Swagger UI 頁面。

---

## 6. API Client 測試與驗證工具

本專案提供 **四種測試途徑**，滿足不同開發測試習慣：

### 1. 使用 Python API Client
本專案獨立實作了 [`client/api_client.py`](file:///d:/restful%20api/client/api_client.py)，能自動執行包含 CRUD、周邊搜尋、統計報表在內的 11 個步驟：
```bash
python client/api_client.py
```
執行過程會印出清晰的 HTTP Request (Method, URL, Body) 以及伺服器回傳的 HTTP Status Code 與格式化 JSON。

### 2. 執行 Pytest 自動化測試
執行包含 12 個測試案例的自動化測試套件：
```bash
pytest tests/test_api.py -v
```
**測試結果**：12 項測試 100% 通過（包含健康檢查、CRUD 生命週期、搜尋過濾、404 與 422 邊界異常等）。

### 3. 使用 Postman 測試集合
1. 開啟 Postman，點擊左上角 **「Import」**。
2. 選取專案中之 [`postman/YouBike_RESTful_API.postman_collection.json`](file:///d:/restful%20api/postman/YouBike_RESTful_API.postman_collection.json)。
3. 即可直接進行各 API 之點選測試。

### 4. 使用 Bruno API Client
本專案已包含 [`bruno/`](file:///d:/restful%20api/bruno) 組態目錄：
1. 開啟 Bruno，選擇 **「Open Collection」** 並選取 `bruno` 目錄。
2. 即可執行儲存好的場站清單查詢、新增、讀取與刪除請求。

---

## 7. 實測範例 (Request & Response)

以下節錄核心 CRUD 之實測請求與回應，完整端點範例請參閱獨立文件 [`API_EXAMPLES.md`](file:///d:/restful%20api/API_EXAMPLES.md)。

### 實測範例：新增場站 (POST)
* **Request**:
  ```http
  POST /api/v1/stations HTTP/1.1
  Host: 127.0.0.1:8000
  Content-Type: application/json

  {
    "sno": "demo_ntub_001",
    "sna": "YouBike2.0_國立臺北商業大學(專題示範站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號正門",
    "act": "1",
    "total_slots": 30,
    "available_rent_bikes": 18,
    "available_return_bikes": 12,
    "latitude": 25.0426,
    "longitude": 121.5252
  }
  ```
* **Response**:
  ```http
  HTTP/1.1 201 Created
  Location: /api/v1/stations/1809
  Content-Type: application/json

  {
    "id": 1809,
    "sno": "demo_ntub_001",
    "sna": "YouBike2.0_國立臺北商業大學(專題示範站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號正門",
    "act": "1",
    "total_slots": 30,
    "available_rent_bikes": 18,
    "available_return_bikes": 12,
    "latitude": 25.0426,
    "longitude": 121.5252,
    "status_text": "營運中",
    "available_rate": 60.0
  }
  ```

---

## 8. AI 輔助開發成果與紀錄

本專案運用 **Google DeepMind Antigravity / Gemini 3.8** 進行結對程式設計 (Pair Programming)，在以下關鍵環節提供核心價值：
1. **資料清洗與轉換**：自動解析官方 Open Data JSON 巢狀結構，建立對應之關聯式資料庫 Schema。
2. **RESTful 標準架構**：協助規劃資源導向 URL 路徑與精確的 HTTP 語意 (200, 201, 204, 400, 404, 422)。
3. **Pydantic V2 嚴謹型別校驗**：防範不合法之地理經緯度與車輛數量。
4. **地理演算法實現**：快速實現 Haversine 半正矢距離公式，支援空間半徑場站查詢。
5. **端對端自動化測試生成**：高效率產生覆蓋率達 100% 的 Pytest 測試案例與 Python API Client 展示程式。

詳細的 Prompt 與開發評估記錄請見 [`AI_ASSISTED_DEV.md`](file:///d:/restful%20api/AI_ASSISTED_DEV.md)。

---

## 9. 作業繳交檢核清單與 Email 格式

### 作業繳交必要檔案檢核：
- [x] **Open Data 資料檔**：[`data/youbike_raw.json`](file:///d:/restful%20api/data/youbike_raw.json)
- [x] **Python 程式碼**：`app/`, `scripts/`, `client/`, `tests/`
- [x] **API 規格與文件**：Swagger UI (`/docs`), ReDoc (`/redoc`), [`openapi.json`](file:///d:/restful%20api/openapi.json)
- [x] **實測範例**：[`API_EXAMPLES.md`](file:///d:/restful%20api/API_EXAMPLES.md)
- [x] **API Client 測試工具設定檔**：[`client/api_client.py`](file:///d:/restful%20api/client/api_client.py), [`postman/YouBike_RESTful_API.postman_collection.json`](file:///d:/restful%20api/postman/YouBike_RESTful_API.postman_collection.json), [`bruno/`](file:///d:/restful%20api/bruno)
- [x] **README 說明文件**：[`README.md`](file:///d:/restful%20api/README.md)
- [x] **AI 輔助開發相關設定檔/紀錄**：[`AI_ASSISTED_DEV.md`](file:///d:/restful%20api/AI_ASSISTED_DEV.md)

### 作業繳交 Email 寄送提醒模板：
* **收件者**：`wenchin@ntub.edu.tw`
* **主旨格式**：`[IoTApp] <我的學號> <我的姓名> ~ 繳交 Open Data RESTful API 實作`
* **郵件內文範例**：
  ```text
  老師您好：

  我是 <我的姓名>，學號：<我的學號>。
  在此繳交「物聯網應用程式開發 (IoTApp)」課程之 Open Data RESTful API 實作作業。

  主題：台北市公共自行車 YouBike 2.0 即時場站 Open Data RESTful API 系統
  GitHub / Google Drive 專案分享連結：
  https://github.com/<您的帳號>/youbike-restful-api (或 Google Drive 連結)
  （已設定權限為：知道連結者皆可讀取）

  專案摘要：
  1. Open Data 檔案：已下載台北市 YouBike 2.0 即時場站資料 (1,808 筆) 儲存於 data/youbike_raw.json 並匯入 SQLite。
  2. RESTful API Server：使用 Python + FastAPI + SQLAlchemy 實作，提供場站資源之完整 CRUD、經緯度周邊查詢與統計分析。
  3. API 文件：支援 Swagger UI (/docs) 與 ReDoc (/redoc)，並附帶 openapi.json 規格檔。
  4. 測試工具：提供 Python API Client (client/api_client.py)、Pytest 測試套件 (12/12 通過)、Postman Collection 匯出檔與 Bruno 設定檔。
  5. 完整說明文件與實測範例請參見 README.md 與 API_EXAMPLES.md，AI 輔助開發紀錄請參見 AI_ASSISTED_DEV.md。

  若有任何問題，煩請老師不吝指教，謝謝老師！

  學生 <我的姓名> 敬上
  學號：<我的學號>
  ```
