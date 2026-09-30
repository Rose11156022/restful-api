"""
API 自動化端對端與整合測試 (pytest)
涵蓋 CRUD、分頁、搜尋、周邊座標、統計分析與異常邊界測試
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_stations" in data
    assert data["total_stations"] > 0

def test_list_stations_default():
    """測試預設場站列表查詢 (分頁第一頁，20筆)"""
    response = client.get("/api/v1/stations")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 20
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] > 1000

def test_list_stations_filter_by_district():
    """測試依行政區 (大安區) 篩選"""
    response = client.get("/api/v1/stations?district=大安區&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    for item in data["items"]:
        assert "大安區" in item["sarea"]

def test_list_stations_keyword_search():
    """測試站名關鍵字模糊搜尋 (捷運)"""
    response = client.get("/api/v1/stations?keyword=捷運&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    for item in data["items"]:
        assert ("捷運" in item["sna"] or "捷運" in item["ar"])

def test_list_stations_sorting():
    """測試欄位排序 (依 total_slots 遞減)"""
    response = client.get("/api/v1/stations?sort_by=total_slots&order=desc&page_size=10")
    assert response.status_code == 200
    items = response.json()["items"]
    slots = [item["total_slots"] for item in items]
    assert slots == sorted(slots, reverse=True)

def test_get_station_detail_by_id():
    """測試讀取單一場站詳細資料 (Read)"""
    # 先取得一筆現有資料
    list_resp = client.get("/api/v1/stations?page_size=1")
    target = list_resp.json()["items"][0]
    target_id = target["id"]

    response = client.get(f"/api/v1/stations/{target_id}")
    assert response.status_code == 200
    station = response.json()
    assert station["id"] == target_id
    assert station["sno"] == target["sno"]
    assert "status_text" in station
    assert "available_rate" in station

def test_get_station_not_found():
    """測試查詢不存在場站之 404 回應"""
    response = client.get("/api/v1/stations/99999999")
    assert response.status_code == 404
    assert "找不到" in response.json()["detail"]

def test_crud_lifecycle():
    """測試場站完整 CRUD 生命週期: Create -> Read -> PUT -> PATCH -> Delete -> Read 404"""
    # 1. CREATE 新增場站
    new_station_payload = {
        "sno": "test_station_9999",
        "sna": "YouBike2.0_測試國立台北商業大學站",
        "sarea": "中正區",
        "ar": "濟南路一段321號",
        "snaen": "YouBike2.0_NTUB Test Station",
        "sareaen": "Zhongzheng Dist.",
        "aren": "No.321, Sec. 1, Jinan Rd.",
        "act": "1",
        "total_slots": 30,
        "available_rent_bikes": 15,
        "available_return_bikes": 15,
        "latitude": 25.0423,
        "longitude": 121.5255,
        "notes": "自動化測試專用場站"
    }

    create_resp = client.post("/api/v1/stations", json=new_station_payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["sno"] == "test_station_9999"
    created_id = created_data["id"]

    # 2. READ 驗證新增成功
    read_resp = client.get(f"/api/v1/stations/{created_id}")
    assert read_resp.status_code == 200
    assert read_resp.json()["sna"] == "YouBike2.0_測試國立台北商業大學站"
    assert read_resp.json()["available_rate"] == 50.0

    # 3. PUT 完整更新
    update_payload = {
        "sna": "YouBike2.0_國立台北商業大學站(已改名)",
        "sarea": "中正區",
        "ar": "濟南路一段321號大門口",
        "snaen": "YouBike2.0_NTUB Main Gate",
        "sareaen": "Zhongzheng Dist.",
        "aren": "No.321, Sec. 1, Jinan Rd. Main Gate",
        "act": "1",
        "total_slots": 40,
        "available_rent_bikes": 20,
        "available_return_bikes": 20,
        "latitude": 25.0425,
        "longitude": 121.5256,
        "notes": "PUT 完整更新測試"
    }
    put_resp = client.put(f"/api/v1/stations/{created_id}", json=update_payload)
    assert put_resp.status_code == 200
    assert put_resp.json()["sna"] == "YouBike2.0_國立台北商業大學站(已改名)"
    assert put_resp.json()["total_slots"] == 40

    # 4. PATCH 局部修改 (僅修改車輛與備註)
    patch_payload = {
        "available_rent_bikes": 25,
        "available_return_bikes": 15,
        "notes": "PATCH 局部微調車位"
    }
    patch_resp = client.patch(f"/api/v1/stations/{created_id}", json=patch_payload)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["available_rent_bikes"] == 25
    assert patch_resp.json()["notes"] == "PATCH 局部微調車位"
    assert patch_resp.json()["total_slots"] == 40  # 原欄位未受影響

    # 5. DELETE 刪除場站
    del_resp = client.delete(f"/api/v1/stations/{created_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 6. READ 驗證刪除後已不存在 (404)
    after_del_resp = client.get(f"/api/v1/stations/{created_id}")
    assert after_del_resp.status_code == 404

def test_nearby_search():
    """測試經緯度周邊站點搜尋 (以台北車站經緯度為例)"""
    # 台北車站座標: 25.0478, 121.5170
    response = client.get("/api/v1/stations/nearby?latitude=25.0478&longitude=121.5170&radius=1000&limit=5")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert len(items) <= 5
    for item in items:
        assert "distance_meters" in item
        assert item["distance_meters"] <= 1000.0

def test_districts_summary():
    """測試行政區統計列表"""
    response = client.get("/api/v1/districts")
    assert response.status_code == 200
    districts = response.json()
    assert len(districts) >= 12  # 台北市有12個行政區
    first_district = districts[0]
    assert "district" in first_district
    assert "station_count" in first_district
    assert "total_available_bikes" in first_district

def test_overview_stats():
    """測試全市營運指標總覽"""
    response = client.get("/api/v1/stats/overview")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_stations"] > 0
    assert stats["active_stations"] > 0
    assert stats["total_capacity"] > 0
    assert stats["districts_count"] >= 12

def test_invalid_parameters():
    """測試無效參數 (422 Unprocessable Entity)"""
    # 測試無效的 act 參數 (只能是 0 或 1)
    response = client.get("/api/v1/stations?act=999")
    assert response.status_code == 422
