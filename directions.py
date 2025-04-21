import requests
from bs4 import BeautifulSoup

def get_directions(api_key, origin, destination, mode="transit"):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": api_key,
        "language": "zh-TW"  # 強制返回繁體中文指引
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    print("完整 API 回應:", data)  # 輸出完整回應，方便排錯
    
    if response.status_code == 200 and "routes" in data and data["routes"]:
        route = data["routes"][0]["legs"][0]
        print(f"從 {origin} 到 {destination} 的 {mode} 路線：")
        print(f"- 距離: {route['distance']['text']}")
        print(f"- 預計時間: {route['duration']['text']}")
        print("詳細導航指引：")
        for step in route["steps"]:
            # 使用 BeautifulSoup 去除 HTML 標籤
            instruction = BeautifulSoup(step["html_instructions"], "html.parser").get_text()
            print(f"  • {instruction}")
    else:
        print("獲取路線失敗:", data.get("error_message", "未知錯誤"))

# 測試範例（請填入你的 Google API 金鑰）
API_KEY = "AIzaSyAU35K8XohOeEW7u8tiXfi3hwi5hzFCaCY"
get_directions(API_KEY, "陽明交通大學", "新竹火車站", mode="transit")



# driving, walking, bicycling, transit