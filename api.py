from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import random

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 設定 API Key
API_KEY = "apikey123"

# 資料庫名稱
DB_NAME = 'placestest.db'

@app.route('/api/data', methods=['GET'])
def get_data():
    # 獲取請求中的 API Key
    key = request.args.get('api_key')

    # 驗證 API Key
    if key != API_KEY:
        return jsonify({"error": "Invalid API Key"}), 403  # 403 錯誤（API Key 錯誤）

    # 從資料庫中隨機獲取 10 筆資料
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 先獲取總資料筆數
        cursor.execute('SELECT COUNT(*) FROM places')
        total_records = cursor.fetchone()[0]
        
        # 如果資料筆數大於 10，隨機選擇 10 筆
        if total_records > 10:
            offset = random.randint(0, total_records - 10)
            cursor.execute('SELECT * FROM places LIMIT 10 OFFSET ?', (offset,))
        else:
            cursor.execute('SELECT * FROM places')
        
        places = cursor.fetchall()
        conn.close()

        # 將資料轉換為字典格式
        data = []
        for place in places:
            data.append({
                "id": place[0],
                "name": place[1],
                "address": place[2],
                "rating": place[3],
                "user_ratings_total": place[4],
                "place_id": place[5],
                "types": place[6],
                "business_status": place[7],
                "latitude": place[8],
                "longitude": place[9],
                "price_level": place[10],
                "phone_number": place[11],
                "opening_hours": place[12],
                "photo_url": place[13],
                "query": place[14]
            })

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 錯誤（伺服器內部錯誤）

if __name__ == '__main__':
    app.run(debug=True)