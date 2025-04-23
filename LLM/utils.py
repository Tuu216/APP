import os
import json
import logging
import pandas as pd
import requests
from config import TOGETHER_API_KEY, TOGETHER_API_URL
from together import Together
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化 Together AI 客戶端
client = Together(api_key=TOGETHER_API_KEY)

def call_llm(messages, model="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
    """呼叫 Together AI LLM API"""
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
        )
        return chat_completion.choices[0].message.content
    except requests.exceptions.RequestException as e:
        logger.error(f"網路錯誤: {str(e)}")
        return None
    except Exception as e:
        if "429" in str(e):
            logger.error("API 配額超限")
            return None
        logger.error(f"API 呼叫失敗: {str(e)}")
        return None

def save_to_json(data, filename):
    """儲存資料到 JSON 檔案"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"資料已儲存至 {filename}")
    except Exception as e:
        logger.error(f"儲存 JSON 失敗: {str(e)}")

def load_from_json(filename):
    """從 JSON 檔案載入資料"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"從 {filename} 載入資料")
            return data
        except Exception as e:
            logger.error(f"載入 JSON 失敗: {str(e)}")
            return None
    return None

def parse_response_to_df(response):
    """將 LLM 回應解析為 Pandas DataFrame"""
    lines = response.split('\n')
    data = []
    current_place = {}
    for line in lines:
        line = line.strip()
        if line.startswith('- 名稱:'):
            if current_place:
                data.append(current_place)
            current_place = {'名稱': line.replace('- 名稱:', '').strip()}
        elif line.startswith('- 描述:'):
            current_place['描述'] = line.replace('- 描述:', '').strip()
        elif line.startswith('- 適合親子的原因:'):
            current_place['適合親子的原因'] = line.replace('- 適合親子的原因:', '').strip()
        elif line.startswith('- 交通方式:'):
            current_place['交通方式'] = line.replace('- 交通方式:', '').strip()
    if current_place:
        data.append(current_place)
    df = pd.DataFrame(data)
    try:
        df.to_csv('attractions.csv', index=False, encoding='utf-8')
        logger.info("景點資料已儲存至 attractions.csv")
    except Exception as e:
        logger.error(f"儲存 CSV 失敗: {str(e)}")
    return df

def save_itinerary(itinerary, filename="itinerary.json"):
    """儲存行程到 JSON"""
    save_to_json(itinerary, filename)