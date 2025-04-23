import os
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()
# 嘗試載入 .env 檔案
dotenv_loaded = load_dotenv()

# 檢查是否成功載入
if not dotenv_loaded:
    print("❌ .env 檔案載入失敗！請確認檔案存在並格式正確。")
else:
    print("✅ .env 檔案載入成功！")

# 從 .env 取得 API 金鑰
TOGETHER_API_KEY =os.getenv("TOGETHER_API_KEY")
print(TOGETHER_API_KEY)
# 檢查是否有設定 API 金鑰
if not TOGETHER_API_KEY:
    raise ValueError("❌ 未找到 API 金鑰，請在 .env 檔案內設定 TOGETHER_API_KEY")

# API 端點
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"