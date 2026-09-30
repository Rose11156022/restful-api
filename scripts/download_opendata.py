"""
下載並儲存台北市 YouBike 2.0 Open Data 為單一資料檔案
資料來源: 台北市政府開放資料平台 / 交通局 YouBike 2.0 即時資訊
URL: https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json
"""

import os
import json
import urllib.request
from datetime import datetime

DATA_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "youbike_raw.json")

def download_open_data():
    print(f"[*] 正在從來源下載 YouBike 2.0 Open Data...")
    print(f"[*] 資料來源 URL: {DATA_URL}")
    
    req = urllib.request.Request(
        DATA_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        raw_bytes = response.read()
        raw_text = raw_bytes.decode("utf-8")
        data = json.loads(raw_text)

    total_records = len(data)
    print(f"[+] 下載成功！共取得 {total_records} 筆場站資料。")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # 寫入單一資料檔案，保留排版以利檢視
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    file_size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"[+] 資料已儲存至單一檔案: {OUTPUT_FILE}")
    print(f"[+] 檔案大小: {file_size_kb:.2f} KB")
    print(f"[+] 下載時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return OUTPUT_FILE

if __name__ == "__main__":
    download_open_data()
