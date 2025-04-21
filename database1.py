import requests
import sqlite3
import time
import os

# API 設定
API_KEY = 'AIzaSyAU35K8XohOeEW7u8tiXfi3hwi5hzFCaCY'
BASE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'
QUERY = '台中小吃'

# 資料庫名稱
DB_NAME = 'placestest.db'


# 建立 SQLite 資料庫並創建表格
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            rating REAL,
            user_ratings_total INTEGER,
            place_id TEXT UNIQUE,
            types TEXT,
            business_status TEXT,
            latitude REAL,
            longitude REAL,
            price_level INTEGER,
            phone_number TEXT,
            opening_hours TEXT,
            photo_url TEXT,  -- 新增圖片 URL 欄位
            query TEXT
        )
    ''')
    conn.commit()
    conn.close()


# 獲取景點資料
def fetch_places(query):
    params = {
        'query': query,
        'key': API_KEY
    }
    all_results = []
    
    while True:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if response.status_code != 200 or 'results' not in data:
            print("API 請求失敗:", data.get('error_message', 'Unknown error'))
            break
        
        all_results.extend(data['results'])
        
        # 檢查是否有下一頁
        next_page_token = data.get('next_page_token')
        if next_page_token:
            print("獲取下一頁資料...")
            params['pagetoken'] = next_page_token
            time.sleep(2)  # 等待2秒，確保 token 生效
        else:
            break
    
    return all_results


# 獲取景點詳細資料
def fetch_place_details(place_id):
    params = {
        'place_id': place_id,
        'key': API_KEY,
        'fields': 'formatted_phone_number,opening_hours'
    }
    response = requests.get(DETAILS_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        result = data.get('result', {})
        return {
            'phone_number': result.get('formatted_phone_number', 'N/A'),
            'opening_hours': ', '.join(result.get('opening_hours', {}).get('weekday_text', [])) if result.get('opening_hours') else 'N/A'
        }
    return {'phone_number': 'N/A', 'opening_hours': 'N/A'}


# 獲取圖片 URL
def fetch_photo_url(photo_reference):
    if not photo_reference:
        return None
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_reference}&key={API_KEY}"


# 下載圖片到本地
def download_photo(photo_url, place_id):
    if not photo_url:
        return
    response = requests.get(photo_url, stream=True)
    if response.status_code == 200:
        os.makedirs("photos", exist_ok=True)
        file_path = f"photos/{place_id}.jpg"
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"圖片已下載: {file_path}")
    else:
        print(f"下載圖片失敗: {photo_url}")


# 儲存景點資料到資料庫
def save_to_db(places, query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for place in places:
        try:
            # 檢查 place_id 是否已存在，若已存在則不插入
            cursor.execute('''SELECT * FROM places WHERE place_id = ?''', (place.get('place_id'),))
            existing_place = cursor.fetchone()
            if existing_place is None:
                # 獲取詳細資料
                details = fetch_place_details(place.get('place_id'))
                
                # 獲取圖片 URL
                photo_reference = place.get('photos', [{}])[0].get('photo_reference', None)
                photo_url = fetch_photo_url(photo_reference)
                
                # 儲存圖片到本地
                download_photo(photo_url, place.get('place_id'))
                
                cursor.execute('''
                    INSERT OR IGNORE INTO places (
                        name, address, rating, user_ratings_total, place_id,
                        types, business_status, latitude, longitude, price_level,
                        phone_number, opening_hours, photo_url, query
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    place.get('name'),
                    place.get('formatted_address', 'N/A'),
                    float(place.get('rating')) if place.get('rating') is not None else None,
                    int(place.get('user_ratings_total')) if place.get('user_ratings_total') is not None else None,
                    place.get('place_id'),
                    ', '.join(place.get('types', [])) if 'types' in place else 'N/A',
                    place.get('business_status', 'N/A'),
                    place['geometry']['location']['lat'] if 'geometry' in place else None,
                    place['geometry']['location']['lng'] if 'geometry' in place else None,
                    place.get('price_level') if 'price_level' in place else None,
                    details['phone_number'],
                    details['opening_hours'],
                    photo_url,
                    query
                ))
        except sqlite3.IntegrityError as e:
            print("資料庫插入錯誤:", e)
        except Exception as e:
            print("發生錯誤:", e)
    conn.commit()
    conn.close()
    print("所有景點數據已成功儲存到資料庫中。")


# 主程式
def main():
    init_db()
    places = fetch_places(QUERY)
    if places:
        save_to_db(places, QUERY)
        print(f"成功存儲 {len(places)} 個資料到資料庫中！")
    else:
        print("未獲取到任何景點數據。")


if __name__ == '__main__':
    main()
