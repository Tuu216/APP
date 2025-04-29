from attraction_recommender import AttractionRecommender
from itinerary_planner import ItineraryPlanner
from utils import logger

def main():
    print("🚀 親子旅遊推薦與規劃系統啟動！輸入 '退出' 以結束。")
    
    while True:
        # 景點推薦階段
        print("\n=== 景點推薦 ===")
        recommender = AttractionRecommender()
        user_query = input("請輸入您的旅遊查詢（例如：台中親子景點）：").strip()
        if user_query.lower() in ['退出', 'exit', 'quit']:
            print("感謝使用旅遊推薦與規劃系統！")
            break
        if not user_query:
            print("輸入不能為空，請重新輸入！")
            continue
        
        response = recommender.recommend(user_query)
        if response.startswith("抱歉"):
            print(response)
            continue
        
        # 收集反饋
        if not recommender.get_user_feedback(response):
            continue
        
        # 行程規劃階段
        while True:
            choice = input("\n是否需要規劃行程？（是/否/退出）：").strip().lower()
            if choice == "退出":
                print("感謝使用旅遊推薦與規劃系統！")
                return
            if choice == "否":
                break  # 返回景點推薦
            if choice != "是":
                print("請輸入有效選項：是/否/退出")
                continue
            
            try:
                days = int(input("請輸入行程天數：").strip())
            except ValueError:
                print("請輸入有效數字！")
                continue
            
            planner = ItineraryPlanner()
            response = planner.plan_itinerary(days)
            print("\n### 行程規劃 ###")
            print(response)
            print("\n行程已儲存至 itinerary.json")
            break  # 完成行程規劃後返回景點推薦

if __name__ == "__main__":
    main()