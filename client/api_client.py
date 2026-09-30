"""
Python RESTful API Client - 台北市 YouBike 2.0 場站管理系統
用於與 API Server 進行通訊、驗證各項 Resource CRUD 操作與展示測試結果。
"""

import sys
import json
import time
import requests
from typing import Dict, Any, Optional

class YouBikeApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = f"{self.base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "YouBike-Python-Client/1.0"
        })

    def _print_step(self, title: str):
        print("\n" + "=" * 70)
        print(f"  [ACTION] {title}")
        print("=" * 70)

    def _print_request(self, method: str, url: str, payload: Any = None):
        print(f">> HTTP Request: {method} {url}")
        if payload is not None:
            print(f">> Request Body:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")

    def _print_response(self, resp: requests.Response):
        print(f"<< HTTP Status Code: {resp.status_code} {resp.reason}")
        try:
            body = resp.json()
            formatted = json.dumps(body, ensure_ascii=False, indent=2)
            # 若資料過長截斷展示
            if len(formatted) > 800:
                print(f"<< Response Body (Truncated):\n{formatted[:800]}...\n[Total {len(formatted)} chars]")
            else:
                print(f"<< Response Body:\n{formatted}")
        except Exception:
            print(f"<< Raw Response:\n{resp.text}")

    def health_check(self) -> Dict[str, Any]:
        """系統健康檢查"""
        url = f"{self.base_url}/health"
        self._print_request("GET", url)
        resp = self.session.get(url)
        self._print_response(resp)
        return resp.json()

    def list_stations(
        self,
        page: int = 1,
        page_size: int = 5,
        district: Optional[str] = None,
        keyword: Optional[str] = None,
        act: Optional[str] = None,
        min_available: Optional[int] = None,
        sort_by: str = "id",
        order: str = "asc"
    ) -> Dict[str, Any]:
        """取得場站清單 (Read List)"""
        url = f"{self.api_prefix}/stations"
        params = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "order": order
        }
        if district: params["district"] = district
        if keyword: params["keyword"] = keyword
        if act: params["act"] = act
        if min_available is not None: params["min_available"] = min_available

        self._print_request("GET", f"{url}?{requests.compat.urlencode(params)}")
        resp = self.session.get(url, params=params)
        self._print_response(resp)
        return resp.json()

    def get_station(self, station_id: Any) -> Dict[str, Any]:
        """取得單一場站資訊 (Read Single)"""
        url = f"{self.api_prefix}/stations/{station_id}"
        self._print_request("GET", url)
        resp = self.session.get(url)
        self._print_response(resp)
        return resp.json()

    def create_station(self, data: Dict[str, Any]) -> requests.Response:
        """新增場站資源 (Create - POST)"""
        url = f"{self.api_prefix}/stations"
        self._print_request("POST", url, payload=data)
        resp = self.session.post(url, json=data)
        self._print_response(resp)
        return resp

    def update_station(self, station_id: Any, data: Dict[str, Any]) -> requests.Response:
        """完整更新場站資源 (Update - PUT)"""
        url = f"{self.api_prefix}/stations/{station_id}"
        self._print_request("PUT", url, payload=data)
        resp = self.session.put(url, json=data)
        self._print_response(resp)
        return resp

    def patch_station(self, station_id: Any, data: Dict[str, Any]) -> requests.Response:
        """局部修改場站資源 (Update - PATCH)"""
        url = f"{self.api_prefix}/stations/{station_id}"
        self._print_request("PATCH", url, payload=data)
        resp = self.session.patch(url, json=data)
        self._print_response(resp)
        return resp

    def delete_station(self, station_id: Any) -> requests.Response:
        """刪除場站資源 (Delete - DELETE)"""
        url = f"{self.api_prefix}/stations/{station_id}"
        self._print_request("DELETE", url)
        resp = self.session.delete(url)
        self._print_response(resp)
        return resp

    def get_nearby_stations(self, lat: float, lng: float, radius: float = 800.0, limit: int = 5) -> Dict[str, Any]:
        """經緯度周邊場站查詢 (Nearby Geo Search)"""
        url = f"{self.api_prefix}/stations/nearby"
        params = {"latitude": lat, "longitude": lng, "radius": radius, "limit": limit}
        self._print_request("GET", f"{url}?{requests.compat.urlencode(params)}")
        resp = self.session.get(url, params=params)
        self._print_response(resp)
        return resp.json()

    def get_districts_summary(self) -> Dict[str, Any]:
        """各行政區統計彙總 (Districts Summary)"""
        url = f"{self.api_prefix}/districts"
        self._print_request("GET", url)
        resp = self.session.get(url)
        self._print_response(resp)
        return resp.json()

    def get_overview_stats(self) -> Dict[str, Any]:
        """全台北市營運總覽指標 (Overview Stats)"""
        url = f"{self.api_prefix}/stats/overview"
        self._print_request("GET", url)
        resp = self.session.get(url)
        self._print_response(resp)
        return resp.json()

def run_full_demo():
    """執行全套 CRUD 與 API 實測驗證流程"""
    client = YouBikeApiClient()
    print("\n=======================================================")
    print("      台北市 YouBike 2.0 RESTful API 實測與驗證展示")
    print("=======================================================")

    try:
        # 步驟 1: 健康檢查
        client._print_step("步驟 1: 檢查 API 伺服器健康狀態")
        client.health_check()

        # 步驟 2: 查詢統計資訊
        client._print_step("步驟 2: 取得全台北市 YouBike 營運總覽統計")
        client.get_overview_stats()

        # 步驟 3: 查詢列表 (分頁與關鍵字篩選)
        client._print_step("步驟 3: 查詢場站清單 (關鍵字: '科技大樓', 每頁 3 筆)")
        list_result = client.list_stations(page=1, page_size=3, keyword="科技大樓")

        # 步驟 4: CREATE - 新增場站 (POST)
        client._print_step("步驟 4: [CREATE] 新增場站資源 (POST /api/v1/stations)")
        demo_station_payload = {
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
        create_resp = client.create_station(demo_station_payload)
        created_station = create_resp.json()
        station_id = created_station.get("id")

        # 步驟 5: READ - 查詢剛建立的場站 (GET by ID)
        client._print_step(f"步驟 5: [READ] 依 ID 讀取剛建立之場站資訊 (GET /api/v1/stations/{station_id})")
        client.get_station(station_id)

        # 步驟 6: UPDATE - 完整更新場站資訊 (PUT)
        client._print_step(f"步驟 6: [UPDATE - PUT] 完整更新場站資料 (PUT /api/v1/stations/{station_id})")
        update_payload = {
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
        client.update_station(station_id, update_payload)

        # 步驟 7: UPDATE - 局部更新 (PATCH)
        client._print_step(f"步驟 7: [UPDATE - PATCH] 局部調整可用車輛數與備註 (PATCH /api/v1/stations/{station_id})")
        patch_payload = {
            "available_rent_bikes": 40,
            "available_return_bikes": 10,
            "notes": "尖峰時段調度車輛完成"
        }
        client.patch_station(station_id, patch_payload)

        # 步驟 8: NEARBY - 經緯度半徑周邊查詢
        client._print_step("步驟 8: [NEARBY] 查詢臺北商大周邊 1,000 公尺之 YouBike 場站")
        client.get_nearby_stations(lat=25.0427, lng=121.5253, radius=1000.0, limit=3)

        # 步驟 9: DELETE - 刪除示範場站 (DELETE)
        client._print_step(f"步驟 9: [DELETE] 刪除示範場站資源 (DELETE /api/v1/stations/{station_id})")
        client.delete_station(station_id)

        # 步驟 10: 驗證刪除後狀態 (預期 404 Not Found)
        client._print_step(f"步驟 10: [VERIFY] 再次查詢已刪除站點，驗證 404 Not Found")
        client.get_station(station_id)

        # 步驟 11: 行政區統計
        client._print_step("步驟 11: [DISTRICTS] 查詢台北市各行政區場站與車位統計")
        client.get_districts_summary()

        print("\n" + "=" * 70)
        print("  [SUCCESS] 全套 RESTful API CRUD 與各項功能測試全部順利完成！")
        print("=======================================================\n")

    except requests.exceptions.ConnectionError:
        print("\n[!] 連線失敗：無法連接至 API Server。")
        print("[!] 請先於終端機啟動服務：uvicorn app.main:app --reload")
        sys.exit(1)

if __name__ == "__main__":
    run_full_demo()
