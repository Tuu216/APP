import sqlite3

# 連接資料庫
conn = sqlite3.connect('taichung_places.db')
c = conn.cursor()

print("你想用什麼條件查找要修改的資料？")
print("1. 用名字 (name)")
print("2. 用 place_id")
choice = input("請輸入選項 (1或2)：")

if choice == '1':
    keyword = input("請輸入景點名字：")
    c.execute('SELECT * FROM places WHERE name = ?', (keyword,))
    result = c.fetchone()
elif choice == '2':
    keyword = input("請輸入 place_id：")
    c.execute('SELECT * FROM places WHERE place_id = ?', (keyword,))
    result = c.fetchone()
else:
    print("輸入錯誤，只能選 1 或 2 喔！")
    conn.close()
    exit()

if not result:
    print("找不到這筆資料喔！")
    conn.close()
    exit()

# 顯示目前資料
print("目前的資料如下：")
columns = [desc[0] for desc in c.description]
for col, val in zip(columns, result):
    print(f"{col}: {val}")

# 可修改欄位
editable_fields = ['name', 'address', 'phone', 'opening_hours', 'photo_url', 'rating', 'user_ratings_total', 'category']
print("\n可以修改的欄位：", ", ".join(editable_fields))
field = input("請輸入你想修改的欄位名稱：")

if field not in editable_fields:
    print("欄位名稱錯誤！")
    conn.close()
    exit()

new_value = input(f"請輸入新的 {field}：")

# 特殊處理 rating 與 user_ratings_total 型別
if field in ['rating']:
    new_value = float(new_value)
elif field in ['user_ratings_total']:
    new_value = int(new_value)

# 執行更新
if choice == '1':
    c.execute(f'UPDATE places SET {field} = ? WHERE name = ?', (new_value, keyword))
else:
    c.execute(f'UPDATE places SET {field} = ? WHERE place_id = ?', (new_value, keyword))

conn.commit()
print("資料更新成功！")

# 關閉連線
conn.close()
