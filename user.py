from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Initialize DB and tables
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create ratings table (for future use)
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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return '請提供帳號和密碼', 400

    hashed_password = generate_password_hash(password)

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return '註冊成功'
    except sqlite3.IntegrityError:
        return '此帳號已存在', 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()

    if user and check_password_hash(user[1], password):
        return f'登入成功！歡迎你，{username}。'
    else:
        return '帳號或密碼錯誤', 401

if __name__ == '__main__':
    app.run(debug=True)
