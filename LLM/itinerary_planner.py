import json
from utils import call_llm, load_from_json, save_itinerary, logger
from datetime import datetime, timedelta

# System Prompt
system_prompt = """
你是一位專業的行程規劃顧問，專為親子家庭設計台中旅遊行程。請以繁體中文、友善熱情的語氣回應，並根據以下規則生成行程：
- 使用提供的景點資料，安排 1-3 天的行程。
- 每天行程結構：
  - 早上：1-2 個景點
  - 中午：1 間餐廳（提供簡短描述）
  - 下午：1-2 個景點
  - 晚餐：1 間餐廳或夜市商圈（提供簡短描述）
  - 晚餐後：0-1 個景點（例如夜景或輕鬆活動）
- 輸出格式：
  第X天 (日期)：
  (時間) (地點) (簡介)
  (地點1到地點2交通時間) (交通方式)
  (時間) (地點) (簡介)
  ...
- 交通時間和方式：根據常識估計（例如公車 20 分鐘），若無法估計，說明原因。
- 若需要餐廳或夜市建議，提供符合親子需求的選項（例如寬敞、兒童友善）。
- 確保行程合理，考慮親子家庭的體力和興趣。
"""

class ItineraryPlanner:
    def __init__(self, model="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
        self.model = model
        self.messages = [{"role": "system", "content": system_prompt}]

    def plan_itinerary(self, days=1):
        """根據儲存的景點生成行程"""
        attractions = load_from_json("recommended_attractions.json")
        if not attractions:
            return "尚未儲存任何景點，請先執行景點推薦。"
        attractions_text = json.dumps(attractions["response"], ensure_ascii=False)
        prompt = f"""
        請根據以下景點資料，安排 {days} 天的台中親子旅遊行程：
        {attractions_text}
        若景點不足，補充其他適合親子旅遊的台中景點，並說明理由。
        """
        self.messages.append({"role": "user", "content": prompt})
        response = call_llm(self.messages, self.model)
        if not response:
            return "抱歉，無法生成行程，請檢查網路或稍後重試。"
        self.messages.append({"role": "assistant", "content": response})
        itinerary = {
            "days": days,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "itinerary": response
        }
        save_itinerary(itinerary)
        return response

def main():
    print("🚀 行程規劃系統啟動！輸入 '退出' 以結束。")
    planner = ItineraryPlanner()
    while True:
        choice = input("\n是否需要規劃行程？（是/否/退出）：").strip().lower()
        if choice == "退出":
            print("感謝使用行程規劃系統！")
            break
        if choice == "否":
            print("好的，隨時輸入 '是' 開始規劃！")
            continue
        if choice != "是":
            print("請輸入有效選項：是/否/退出")
            continue
        try:
            days = int(input("請輸入行程天數（1-3 天）：").strip())
            if days < 1 or days > 3:
                print("天數必須在 1-3 天之間！")
                continue
        except ValueError:
            print("請輸入有效數字！")
            continue
        response = planner.plan_itinerary(days)
        print("\n### 行程規劃 ###")
        print(response)
        print("\n行程已儲存至 itinerary.json")

if __name__ == "__main__":
    main()