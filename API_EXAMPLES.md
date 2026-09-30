# 台北市 YouBike 2.0 RESTful API 實測範例

本文件詳細記錄各項 RESTful API 端點之實測請求 (HTTP Request) 與伺服器回傳 (HTTP Response)，包含 HTTP Method、URL Path、Query/Body 參數、HTTP 狀態碼及回應內容。

---

## 1. 系統健康檢查 (Health Check)

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/health`
* **Request Headers**:
  ```http
  Accept: application/json
  ```
* **Request Body**: 無
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "status": "healthy",
    "service": "台北市 YouBike 2.0 開放資料 RESTful API 服務",
    "version": "1.0.0",
    "database": "connected",
    "total_stations": 1808
  }
  ```

---

## 2. 查詢場站分頁清單 (Read List - GET /api/v1/stations)

支援多條件篩選：分頁 (`page`, `page_size`)、行政區 (`district`)、關鍵字 (`keyword`)、營運狀態 (`act`)、排序 (`sort_by`, `order`)。

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations?page=1&page_size=2&district=大安區&keyword=科技大樓`
* **Request Headers**:
  ```http
  Accept: application/json
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "total": 1,
    "page": 1,
    "page_size": 2,
    "total_pages": 1,
    "items": [
      {
        "id": 1,
        "sno": "500101001",
        "sna": "YouBike2.0_捷運科技大樓站",
        "sarea": "大安區",
        "ar": "復興南路二段235號前",
        "snaen": "YouBike2.0_MRT Technology Bldg. Sta.",
        "sareaen": "Daan Dist.",
        "aren": "No.235, Sec. 2, Fuxing S. Rd.",
        "act": "1",
        "total_slots": 28,
        "available_rent_bikes": 7,
        "available_return_bikes": 21,
        "latitude": 25.02605,
        "longitude": 121.5436,
        "info_time": "2026-09-30 15:11:02",
        "notes": "Open Data 初始匯入",
        "created_at": "2026-09-30T07:37:12",
        "updated_at": "2026-09-30T07:37:12",
        "status_text": "營運中",
        "available_rate": 25.0
      }
    ]
  }
  ```

---

## 3. 查詢單一場站明細 (Read Single - GET /api/v1/stations/{id})

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations/1` (亦支援傳入 `sno` 如 `/api/v1/stations/500101001`)
* **Request Headers**:
  ```http
  Accept: application/json
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "id": 1,
    "sno": "500101001",
    "sna": "YouBike2.0_捷運科技大樓站",
    "sarea": "大安區",
    "ar": "復興南路二段235號前",
    "snaen": "YouBike2.0_MRT Technology Bldg. Sta.",
    "sareaen": "Daan Dist.",
    "aren": "No.235, Sec. 2, Fuxing S. Rd.",
    "act": "1",
    "total_slots": 28,
    "available_rent_bikes": 7,
    "available_return_bikes": 21,
    "latitude": 25.02605,
    "longitude": 121.5436,
    "info_time": "2026-09-30 15:11:02",
    "notes": "Open Data 初始匯入",
    "created_at": "2026-09-30T07:37:12",
    "updated_at": "2026-09-30T07:37:12",
    "status_text": "營運中",
    "available_rate": 25.0
  }
  ```

---

## 4. 新增場站資源 (Create - POST /api/v1/stations)

* **HTTP Method**: `POST`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations`
* **Request Headers**:
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Request Body**:
  ```json
  {
    "sno": "demo_ntub_001",
    "sna": "YouBike2.0_國立臺北商業大學(專題示範站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號正門",
    "snaen": "YouBike2.0_National Taipei University of Business",
    "sareaen": "Zhongzheng Dist.",
    "aren": "No.321, Sec. 1, Jinan Rd.",
    "act": "1",
    "total_slots": 30,
    "available_rent_bikes": 18,
    "available_return_bikes": 12,
    "latitude": 25.0426,
    "longitude": 121.5252,
    "notes": "此站點為 AI 輔助開發 RESTful API 課程作業建立之示範場站"
  }
  ```
* **Response Status**: `201 Created`
* **Response Headers**:
  ```http
  Location: /api/v1/stations/1809
  ```
* **Response Body**:
  ```json
  {
    "id": 1809,
    "sno": "demo_ntub_001",
    "sna": "YouBike2.0_國立臺北商業大學(專題示範站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號正門",
    "snaen": "YouBike2.0_National Taipei University of Business",
    "sareaen": "Zhongzheng Dist.",
    "aren": "No.321, Sec. 1, Jinan Rd.",
    "act": "1",
    "total_slots": 30,
    "available_rent_bikes": 18,
    "available_return_bikes": 12,
    "latitude": 25.0426,
    "longitude": 121.5252,
    "info_time": "2026-09-30 15:41:16",
    "notes": "此站點為 AI 輔助開發 RESTful API 課程作業建立之示範場站",
    "created_at": "2026-09-30T07:41:16.250823",
    "updated_at": "2026-09-30T07:41:16.250823",
    "status_text": "營運中",
    "available_rate": 60.0
  }
  ```

---

## 5. 完整更新場站資訊 (Update - PUT /api/v1/stations/{id})

* **HTTP Method**: `PUT`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations/demo_ntub_001`
* **Request Headers**:
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Request Body**:
  ```json
  {
    "sna": "YouBike2.0_國立臺北商業大學(智慧校園旗艦站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號行政大樓前",
    "snaen": "YouBike2.0_NTUB Smart Flagship Station",
    "sareaen": "Zhongzheng Dist.",
    "aren": "No.321, Sec. 1, Jinan Rd. (Admin Building)",
    "act": "1",
    "total_slots": 50,
    "available_rent_bikes": 35,
    "available_return_bikes": 15,
    "latitude": 25.0427,
    "longitude": 121.5253,
    "notes": "已升級為智慧旗艦站點，增加車容量與感應設備"
  }
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "id": 1809,
    "sno": "demo_ntub_001",
    "sna": "YouBike2.0_國立臺北商業大學(智慧校園旗艦站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號行政大樓前",
    "snaen": "YouBike2.0_NTUB Smart Flagship Station",
    "sareaen": "Zhongzheng Dist.",
    "aren": "No.321, Sec. 1, Jinan Rd. (Admin Building)",
    "act": "1",
    "total_slots": 50,
    "available_rent_bikes": 35,
    "available_return_bikes": 15,
    "latitude": 25.0427,
    "longitude": 121.5253,
    "info_time": "2026-09-30 15:41:16",
    "notes": "已升級為智慧旗艦站點，增加車容量與感應設備",
    "created_at": "2026-09-30T07:41:16.250823",
    "updated_at": "2026-09-30T07:41:16.272675",
    "status_text": "營運中",
    "available_rate": 70.0
  }
  ```

---

## 6. 局部修改場站資訊 (Update Partial - PATCH /api/v1/stations/{id})

* **HTTP Method**: `PATCH`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations/demo_ntub_001`
* **Request Headers**:
  ```http
  Content-Type: application/json
  Accept: application/json
  ```
* **Request Body**:
  ```json
  {
    "available_rent_bikes": 40,
    "available_return_bikes": 10,
    "notes": "尖峰時段調度車輛完成"
  }
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "id": 1809,
    "sno": "demo_ntub_001",
    "sna": "YouBike2.0_國立臺北商業大學(智慧校園旗艦站)",
    "sarea": "中正區",
    "ar": "台北市中正區濟南路一段321號行政大樓前",
    "snaen": "YouBike2.0_NTUB Smart Flagship Station",
    "sareaen": "Zhongzheng Dist.",
    "aren": "No.321, Sec. 1, Jinan Rd. (Admin Building)",
    "act": "1",
    "total_slots": 50,
    "available_rent_bikes": 40,
    "available_return_bikes": 10,
    "latitude": 25.0427,
    "longitude": 121.5253,
    "info_time": "2026-09-30 15:41:16",
    "notes": "尖峰時段調度車輛完成",
    "created_at": "2026-09-30T07:41:16.250823",
    "updated_at": "2026-09-30T07:41:16.283636",
    "status_text": "營運中",
    "available_rate": 80.0
  }
  ```

---

## 7. 經緯度半徑周邊場站查詢 (Nearby Geo Search)

以國立台北商業大學座標 (25.0427, 121.5253) 為中心，查詢半徑 1,000 公尺內之場站，依距離遞增排序。

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations/nearby?latitude=25.0427&longitude=121.5253&radius=1000&limit=2`
* **Request Headers**:
  ```http
  Accept: application/json
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  [
    {
      "id": 1809,
      "sno": "demo_ntub_001",
      "sna": "YouBike2.0_國立臺北商業大學(智慧校園旗艦站)",
      "sarea": "中正區",
      "ar": "台北市中正區濟南路一段321號行政大樓前",
      "act": "1",
      "total_slots": 50,
      "available_rent_bikes": 40,
      "available_return_bikes": 10,
      "latitude": 25.0427,
      "longitude": 121.5253,
      "distance_meters": 0.0,
      "status_text": "營運中",
      "available_rate": 80.0
    },
    {
      "id": 698,
      "sno": "500106127",
      "sna": "YouBike2.0_仁愛杭州南路口",
      "sarea": "中正區",
      "ar": "仁愛路一段30號前",
      "act": "1",
      "total_slots": 19,
      "available_rent_bikes": 8,
      "available_return_bikes": 11,
      "latitude": 25.03845,
      "longitude": 121.5262,
      "distance_meters": 481.5,
      "status_text": "營運中",
      "available_rate": 42.1
    }
  ]
  ```

---

## 8. 刪除場站資源 (Delete - DELETE /api/v1/stations/{id})

* **HTTP Method**: `DELETE`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations/demo_ntub_001`
* **Request Headers**:
  ```http
  Accept: application/json
  ```
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "success": true,
    "message": "場站 [demo_ntub_001] YouBike2.0_國立臺北商業大學(智慧校園旗艦站) 已成功刪除。",
    "data": {
      "sno": "demo_ntub_001",
      "sna": "YouBike2.0_國立臺北商業大學(智慧校園旗艦站)"
    }
  }
  ```

---

## 9. 驗證刪除後再次查詢 (404 Not Found)

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stations/demo_ntub_001`
* **Response Status**: `404 Not Found`
* **Response Body**:
  ```json
  {
    "detail": "找不到指定的場站 (ID/SNO: demo_ntub_001)"
  }
  ```

---

## 10. 全台北市營運總覽統計 (GET /api/v1/stats/overview)

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/api/v1/stats/overview`
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "total_stations": 1808,
    "active_stations": 1782,
    "suspended_stations": 26,
    "total_capacity": 43500,
    "total_available_bikes": 16420,
    "total_return_spaces": 27080,
    "districts_count": 12
  }
  ```

---

## 11. 行政區場站統計彙總 (GET /api/v1/districts)

* **HTTP Method**: `GET`
* **URL Path**: `http://127.0.0.1:8000/api/v1/districts`
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  [
    {
      "district": "大安區",
      "station_count": 217,
      "total_slots": 6681,
      "total_available_bikes": 1972,
      "total_return_spaces": 4577,
      "active_station_count": 213
    },
    {
      "district": "中山區",
      "station_count": 205,
      "total_slots": 5585,
      "total_available_bikes": 2166,
      "total_return_spaces": 3201,
      "active_station_count": 199
    }
  ]
  ```
