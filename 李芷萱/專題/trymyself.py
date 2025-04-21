from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 請設置安全的密鑰
CORS(app)

# 初始化 SQLite 資料庫
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# 創建用戶表（含 createtime）
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    createtime DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 創建評分表（未來使用）
c.execute('''
CREATE TABLE IF NOT EXISTS user_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    place_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, place_id)
)
''')
conn.commit()

# 讀取 CSV 數據
taichung_places = pd.read_csv('taichung_places_data.csv')
user_ratings = pd.read_csv('user_place_ratings_taichung.csv')

# 創建用戶評分矩陣
user_vec = user_ratings.pivot_table(index='userId', columns='placeId', values='rating').fillna(0)

# 推薦系統方法
def recommend(user, similar_users, top_n=10):
    seen_places = np.unique(user_ratings.loc[user_ratings["userId"] == user, "placeId"].values)
    not_seen_cond = ~user_ratings["placeId"].isin(seen_places)
    similar_cond = user_ratings["userId"].isin(similar_users)
    not_seen_places_ratings = user_ratings[not_seen_cond & similar_cond][["placeId", "rating"]]

    average_ratings = not_seen_places_ratings.groupby("placeId").mean()
    average_ratings.reset_index(inplace=True)
    top_ratings = average_ratings.sort_values(by="rating", ascending=False).iloc[:top_n]
    top_ratings.reset_index(inplace=True, drop=True)
    top_ratings = pd.merge(top_ratings, taichung_places[['placeId', 'title', '地址', '聯絡方式', '評價', 'tags']], on="placeId", how="left")
    return top_ratings

def find_the_most_similar_users(user_id, num=10):
    user_vector = user_vec.loc[user_id].values.reshape(1, -1)
    similarity_scores = cosine_similarity(user_vec.values, user_vector)
    similar_users_idx = np.argsort(similarity_scores.flatten())[::-1][1:num+1]
    return user_vec.index[similar_users_idx].tolist()

# 註冊路由
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '請提供帳號和密碼'}), 400

    hashed_password = generate_password_hash(password)

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        # 查詢新用戶的 ID
        c.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({'message': '註冊成功，已自動登入'})
    except sqlite3.IntegrityError:
        return jsonify({'message': '此帳號已存在'}), 400

# 登入路由
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()

    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({'message': f'登入成功！歡迎你，{username}。'})
    else:
        return jsonify({'message': '帳號或密碼錯誤'}), 401

# 登出路由
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

# 主頁路由
@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    error = None

    if request.method == 'POST':
        if 'user_id' not in session:
            return render_template('trymyself.html', recommendations=recommendations, error='請先登入')
        
        try:
            user_id = int(request.form['user_id'])
            if user_id != session['user_id']:
                raise ValueError("請輸入正確的用戶ID！")
            if user_id not in user_vec.index:
                raise ValueError("用戶ID不存在於評分數據中！")

            similar_users = find_the_most_similar_users(user_id, num=10)
            top_ratings = recommend(user_id, similar_users, top_n=5)
            recommendations = top_ratings.to_dict(orient='records')
        except ValueError as e:
            error = str(e)

    return render_template('trymyself.html', recommendations=recommendations, error=error)

if __name__ == '__main__':
    app.run(debug=True)