import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re

# 你的 Google Places API 金鑰
API_KEY = 'AIzaSyAU35K8XohOeEW7u8tiXfi3hwi5hzFCaCY'  # << 記得換成你自己的

# 要爬的網址
url = 'https://www.welcometw.com/%E5%8F%B0%E4%B8%AD%E6%99%AF%E9%BB%9E%E6%8E%A8%E8%96%A6%EF%BD%9C%E5%BF%85%E5%8E%BB%E6%89%93%E5%8D%A1%E6%99%AF%E9%BB%9E24%E9%81%B8/'

# 建立 SQLite 連線
conn = sqlite3.connect('taichung_places.db')
c = conn.cursor()

# 建立資料表
c.execute(''' 
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        place_id TEXT,
        address TEXT,
        phone TEXT,
        opening_hours TEXT,
        photo_url TEXT,
        rating REAL,
        user_ratings_total INTEGER,
        category TEXT
    )
''')
conn.commit()

# 讓使用者輸入類型
category = input("請輸入爬取的資料類型（如：景點、美食、住宿）：")

# 爬取網頁
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
h3_list = soup.find_all('h3')

place_names = []
for h3 in h3_list:
    text = h3.get_text(strip=True)
    text = re.sub(r'^\d+\.\s*', '', text)
    clean_name = re.sub(r'台中.*?–\s*', '', text)
    if "｜" in clean_name:
        clean_name = clean_name.split("｜")[-1]
    clean_name = clean_name.strip()
    if '？' not in clean_name and clean_name:
        place_names.append(clean_name)

print(f"總共找到 {len(place_names)} 個景點")
print(place_names)

# 查詢每個景點的資料
for name in place_names:
    print(f"搜尋景點：{name}")

    # 用 textsearch 搜尋，query 加上 "台中"
    search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': f"台中 {name}",
        'key': API_KEY,
        'language': 'zh-TW',
        'region': 'tw'
    }
    resp = requests.get(search_url, params=params)
    data = resp.json()

    if data['status'] != 'OK' or not data['results']:
        print(f"找不到 {name} 的 Google 資料")
        continue

    # 選擇在台中市的資料
    place = None
    for p in data['results']:
        if 'formatted_address' in p and '台中市' in p['formatted_address']:
            place = p
            break
    if not place:
        print(f"{name} 找到的不是台中市的店，跳過！")
        continue

    place_id = place['place_id']

    # 檢查是否已存在
    c.execute('SELECT place_id FROM places WHERE place_id = ?', (place_id,))
    if c.fetchone():
        print(f"景點 {name} 的資料已存在，跳過抓取！")
        continue

    # 抓詳細資料
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
    detail_params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,formatted_phone_number,opening_hours,photos,rating,user_ratings_total',
        'key': API_KEY,
        'language': 'zh-TW'
    }
    detail_resp = requests.get(details_url, params=detail_params)
    detail_data = detail_resp.json()

    if detail_data['status'] != 'OK':
        print(f"找不到 {name} 的詳細資料")
        continue

    place_details = detail_data['result']
    
    address = place_details.get('formatted_address', '無資料')
    phone = place_details.get('formatted_phone_number', '無資料')
    opening_hours = place_details.get('opening_hours', {}).get('weekday_text', '無資料')
    if isinstance(opening_hours, list):
        opening_hours = "\n".join(opening_hours)
    else:
        opening_hours = '無資料'
    photo_url = place_details.get('photos', [{}])[0].get('photo_reference', '無資料')
    rating = place_details.get('rating', '無資料')
    user_ratings_total = place_details.get('user_ratings_total', '無資料')

    photo_url_full = ""
    if photo_url != '無資料':
        photo_url_full = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_url}&key={API_KEY}"

    # 存入資料庫
    c.execute(''' 
        INSERT INTO places (name, place_id, address, phone, opening_hours, photo_url, rating, user_ratings_total, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, place_id, address, phone, opening_hours, photo_url_full, rating, user_ratings_total, category))

    conn.commit()
    print(f"{name} 的資料已儲存成功！")
    time.sleep(random.uniform(1, 2))

# 關閉資料庫連線
conn.close()
