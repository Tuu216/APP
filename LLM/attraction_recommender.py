from utils import call_llm, save_to_json, parse_response_to_df, logger
import json
from LLM_system import recommend_thinking_system, recommend_system


class AttractionRecommender:
    def __init__(self, model="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
        self.model = model
        self.thinking_messages = [{"role": "system", "content": recommend_thinking_system}]
        self.recommend_messages = [{"role": "system", "content": recommend_system}]

    def recommend_thinking(self, user_query):
        """分析使用者旅遊需求，生成結構化 JSON 結果，並等待確認"""
        self.thinking_messages.append({"role": "user", "content": user_query})
        response = call_llm(self.thinking_messages, self.model)
        if not response:
            return None
        try:
            # 假設 LLM 回應是 JSON 格式
            analysis = json.loads(response)
            # 打印分析結果
            print("\n### 需求分析結果 ###")
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
            # 等待使用者確認
            while True:
                confirm = input("\n是否確認儲存需求分析？（確認/取消）：").strip().lower()
                if confirm == "確認":
                    save_to_json(analysis, "demand_analysis.json")
                    self.thinking_messages.append({"role": "assistant", "content": response})
                    return analysis
                elif confirm == "取消":
                    print("已取消儲存，將重新分析。")
                    self.thinking_messages.pop()  # 移除失敗的查詢
                    return self.recommend_thinking(user_query)  # 重新分析
                else:
                    print("請輸入有效選項：確認/取消")
        except json.JSONDecodeError:
            logger.error("LLM 回應非有效 JSON 格式")
            return None

    def recommend(self, user_query):
        """根據需求分析生成景點推薦，並等待確認"""
        # 先進行需求分析
        analysis = self.recommend_thinking(user_query)
        if not analysis:
            return "抱歉，無法分析需求，請檢查網路或稍後重試。"
        
        # 將分析結果融入推薦提示詞
        analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2)
        prompt = f"""
        根據以下需求分析，推薦適合的景點：
        {analysis_text}
        原始查詢：{user_query}
        """
        self.recommend_messages.append({"role": "user", "content": prompt})
        response = call_llm(self.recommend_messages, self.model)
        if not response:
            return "抱歉，無法生成推薦，請檢查網路或稍後重試."
        
        # 打印推薦結果
        print("\n### 初步推薦結果 ###")
        print(response)
        df = parse_response_to_df(response)
        print("\n### 結構化推薦 ###")
        print(df)
        
        # 等待使用者確認
        while True:
            confirm = input("\n是否確認儲存推薦結果？（確認/取消）：").strip().lower()
            if confirm == "確認":
                save_to_json({"query": prompt, "response": response}, "recommended_attractions.json")
                self.recommend_messages.append({"role": "assistant", "content": response})
                return response
            elif confirm == "取消":
                print("已取消儲存，將進入反饋收集。")
                self.recommend_messages.pop()  # 移除失敗的查詢
                return self.get_user_feedback(response)  # 進入反饋收集
            else:
                print("請輸入有效選項：確認/取消")

    def get_user_feedback(self, response):
        """收集使用者反饋並根據反饋重新推薦"""
        while True:
            feedback = input("\n您對推薦結果滿意嗎？（滿意/不滿意/退出）：").strip().lower()
            if feedback == "滿意":
                return True
            elif feedback == "不滿意":
                user_feedback = input("請提供改進建議（例如：需要更多室內景點）：").strip()
                if user_feedback:
                    new_query = f"根據以下反饋改進推薦：{user_feedback}\n原始查詢：{self.recommend_messages[-2]['content']}"
                    self.recommend_messages.append({"role": "user", "content": new_query})
                    new_response = call_llm(self.recommend_messages, self.model)
                    if not new_response:
                        print("抱歉，無法生成新推薦，請稍後重試。")
                        return False
                    self.recommend_messages.append({"role": "assistant", "content": new_response})
                    print("\n### 新推薦結果 ###")
                    print(new_response)
                    df = parse_response_to_df(new_response)
                    print("\n### 結構化推薦 ###")
                    print(df)
                    # 等待確認新推薦
                    while True:
                        confirm = input("\n是否確認儲存新推薦結果？（確認/取消）：").strip().lower()
                        if confirm == "確認":
                            save_to_json({"query": new_query, "response": new_response}, "recommended_attractions.json")
                            return True
                        elif confirm == "取消":
                            print("已取消儲存新推薦，請繼續提供反饋。")
                            break
                        else:
                            print("請輸入有效選項：確認/取消")
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
        if not response or response.startswith("抱歉"):
            print(response)
            continue
        if not recommender.get_user_feedback(response):
            continue

if __name__ == "__main__":
    main()