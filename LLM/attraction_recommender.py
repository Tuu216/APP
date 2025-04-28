from utils import call_llm, save_to_json, parse_response_to_df, logger
from LLM_roel import recommender_system

# System Prompt
system_prompt = recommender_system

class AttractionRecommender:
    def __init__(self, model="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
        self.model = model
        self.messages = [{"role": "system", "content": system_prompt}]

    def recommend(self, user_query):
        """根據使用者查詢生成景點推薦"""
        self.messages.append({"role": "user", "content": user_query})
        response = call_llm(self.messages, self.model)
        if not response:
            return "抱歉，無法生成推薦，請檢查網路或稍後重試。"
        self.messages.append({"role": "assistant", "content": response})
        return response

    def get_user_feedback(self, response):
        """收集使用者反饋並根據反饋重新推薦"""
        print("\n### 推薦結果 ###")
        print(response)
        df = parse_response_to_df(response)
        print("\n### 結構化推薦 ###")
        print(df)
        while True:
            feedback = input("\n您對推薦結果滿意嗎？（滿意/不滿意/退出）：").strip().lower()
            if feedback == "滿意":
                save_to_json({"query": self.messages[-2]["content"], "response": response}, "recommended_attractions.json")
                return True
            elif feedback == "不滿意":
                user_feedback = input("請提供改進建議（例如：需要更多室內景點）：").strip()
                if user_feedback:
                    new_query = f"根據以下反饋改進推薦：{user_feedback}\n原始查詢：{self.messages[-2]['content']}"
                    self.messages.append({"role": "user", "content": new_query})
                    response = call_llm(self.messages, self.model)
                    if not response:
                        print("抱歉，無法生成新推薦，請稍後重試。")
                        return False
                    self.messages.append({"role": "assistant", "content": response})
                    print("\n### 新推薦結果 ###")
                    print(response)
                    df = parse_response_to_df(response)
                    print("\n### 結構化推薦 ###")
                    print(df)
                else:
                    print("反饋不能為空，請重新輸入。")
            elif feedback == "退出":
                return False
            else:
                print("請輸入有效選項：滿意/不滿意/退出")

def main():
    print("🚀 景點推薦系統啟動！輸入 '退出' 以結束。")
    recommender = AttractionRecommender()
    while True:
        user_query = input("請輸入您的旅遊查詢（例如：台中親子景點）：").strip()
        if user_query.lower() in ['退出', 'exit', 'quit']:
            print("感謝使用景點推薦系統！")
            break
        if not user_query:
            print("輸入不能為空，請重新輸入！")
            continue
        response = recommender.recommend(user_query)
        if not recommender.get_user_feedback(response):
            continue

if __name__ == "__main__":
    main()