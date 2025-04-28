import sqlite3

# 連接資料庫
conn = sqlite3.connect('taichung_places.db')
c = conn.cursor()

# 選擇刪除方式
print("你想用什麼條件刪除資料？")
print("1. 用名字 (name)")
print("2. 用 place_id")
choice = input("請輸入選項 (1或2)：")

if choice == '1':
    keyword = input("請輸入要刪除的【名字】（精確一點喔）：")
    c.execute('SELECT * FROM places WHERE name = ?', (keyword,))
    result = c.fetchone()
    if result:
        print(f"找到資料：{result}")
        confirm = input("確定要刪除嗎？(y/n)：")
        if confirm.lower() == 'y':
            c.execute('DELETE FROM places WHERE name = ?', (keyword,))
            conn.commit()
            print(f"名字為「{keyword}」的資料已刪除！")
        else:
            print("取消刪除。")
    else:
        print("找不到這筆資料喔！")

elif choice == '2':
    keyword = input("請輸入要刪除的【place_id】：")
    c.execute('SELECT * FROM places WHERE place_id = ?', (keyword,))
    result = c.fetchone()
    if result:
        print(f"找到資料：{result}")
        confirm = input("確定要刪除嗎？(y/n)：")
        if confirm.lower() == 'y':
            c.execute('DELETE FROM places WHERE place_id = ?', (keyword,))
            conn.commit()
            print(f"place_id為「{keyword}」的資料已刪除！")
        else:
            print("取消刪除。")
    else:
        print("找不到這筆資料喔！")

else:
    print("輸入錯誤，只能選 1 或 2 喔！")

# 關閉連線
conn.close()
