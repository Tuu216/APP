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

# 預設使用的模型
MODEL_NAME = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

# 可用模型列表（方便動態切換）
#AVAILABLE_MODELS = {
#   "llama_3.1_8b": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
#   "llama_3.3_70b": "meta-llama/Meta-Llama-3.3-70B-Instruct",
#}

def set_model(model_key):
    """根據字典 key 切換不同的 LLaMA 模型"""
    global MODEL_NAME
    if model_key in AVAILABLE_MODELS:
        MODEL_NAME = AVAILABLE_MODELS[model_key]
        print(f"✅ 模型已切換為：{MODEL_NAME}")
    else:
        print("⚠️ 錯誤：無效的模型名稱，請選擇可用的模型！")