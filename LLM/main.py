import requests
from config import TOGETHER_API_KEY, TOGETHER_API_URL, MODEL_NAME, set_model
from together import Together

client = Together() 
def get_recommendation(query):
    """向 Together AI API 發送請求，獲取 LLaMA 生成的推薦"""
    payload = {
        "model": MODEL_NAME,  # 使用 config.py 設定的模型
        "prompt": query,
        "max_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(TOGETHER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("text", "").strip()
    except Exception as e:
        return f"API 錯誤：{str(e)}"

if __name__ == "__main__":
    print("🚀 旅遊推薦系統啟動！")

    # ✅ 可動態切換模型
    #set_model("llama_3.3_70b")

    # 測試推薦系統
    user_query = "請推薦台中適合親子的景點，並說明推薦原因。"
    print("🎯 使用模型：", MODEL_NAME)
    print("🎯 API：", TOGETHER_API_KEY)
    print(get_recommendation(user_query))