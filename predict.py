import requests
import json
import os

# =====================================================================
# 1. 自動讀取 GitHub Secrets 保險箱密鑰
# =====================================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ODDS_API_KEY = os.environ.get("ODDS_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# =====================================================================
# 2. 智能雷達：只抓取真實賽事，無波寧願罷工
# =====================================================================
def get_international_odds():
    print("🔄 正在啟動智能雷達，搜尋今日真實賽事...")
    
    if not ODDS_API_KEY:
        print("❌ 錯誤：找不到 ODDS_API_KEY！請檢查 GitHub 保險箱設定。")
        return None

    # 📡 聯賽搜尋名單 (2026年6月正值世界盃黃金期，優先抓取)
    SPORTS_TO_TRY = [
        'soccer_fifa_world_cup',       # 世界盃
        'soccer_conmebol_copa_america',# 美洲盃
        'soccer_usa_mls',              # 美職聯
        'soccer_japan_j_league',       # 日職聯
        'soccer_epl'                   # 英超
    ]
    
    for sport in SPORTS_TO_TRY:
        print(f"🔍 正在尋找聯賽：{sport} ...")
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal",
            "dateFormat": "iso"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                match_list = response.json()
                if match_list and len(match_list) > 0:
                    match = match_list[0]
                    home_team = match.get("home_team", "主隊")
                    away_team = match.get("away_team", "客隊")
                    start_time = match.get("commence_time", "即將開賽")
                    
                    bookmaker = match['bookmakers'][0]
                    outcomes = bookmaker['markets'][0]['outcomes']
                    
                    h_odds, d_odds, a_odds = "0.00", "0.00", "0.00"
                    for outcome in outcomes:
                        if outcome['name'] == home_team: h_odds = str(outcome['price'])
                        elif outcome['name'] == away_team: a_odds = str(outcome['price'])
                        elif outcome['name'] == 'Draw': d_odds = str(outcome['price'])

                    print(f"🎯 成功鎖定真實賽事：{home_team} vs {away_team}")
                    return {
                        "match_name": f"{home_team} vs {away_team}",
                        "match_time": start_time,
                        "h_odds": h_odds,
                        "a_odds": a_odds,
                        "d_odds": d_odds,
                        "bookmaker": bookmaker['title']
                    }
        except Exception as e:
            print(f"⚠️ 嘗試 {sport} 時發生錯誤：{e}")
            continue 

    print("ℹ️ 今日雷達名單內的所有聯賽均無即將開賽的數據。")
    return None

# =====================================================================
# 3. 呼叫 最新 Gemini 3.5 Flash 大腦 (安全拆分網址版，絕不報錯)
# =====================================================================
def generate_report_with_gemini(match_info):
    if not match_info:
        return None
        
    print("🧠 正在啟動 Gemini 3.5 Flash 大腦進行即時深度分析...")
    
    if not GEMINI_API_KEY:
        print("❌ 錯誤：找不到 GEMINI_API_KEY！")
        return None

    # 🛠️ 拆散長網址，確保每行都極短，絕不引發 GitHub 網頁折行 bug
    part1 = "https://generativelanguage.googleapis.com"
    part2 = "/v1beta/models/gemini-3.5-flash:generateContent"
    url = f"{part1}{part2}?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""你現在是一位精通香港馬會波經的頂級足球分析師。
請根據以下提供的【真實賽事資料與國際莊家賠率】，撰寫今日的深度預測。

【真實賽事資料】：
球賽：{match_info['match_name']}
開賽時間：{match_info['match_time']}
莊家 ({match_info['bookmaker']}) 賠率：主勝 {match_info['h_odds']} | 客勝 {match_info['a_odds']} | 和局 {match_info['d_odds']}

⚠️ 【極度重要警告】：
你必須【絕對忠於】上方提供的【真實賽事資料】！
千萬不要憑空捏造對賽球隊，也不要拿歷史經典戰役（如2022世界盃）當作今日賽事。我給你什麼球隊，你就只能分析什麼！
如果球隊名是英文，請在分析時自動將其翻譯為香港球迷最熟悉的中文譯名（例如：Brazil 譯成 巴西，Japan 譯成 日本）。

⚠️ 嚴格核心要求：
1. 完全忽略多年前的歷史往績，將分析重心放在「球隊最新陣容磨合度」及「即時戰意/進攻意慾」。
2. 必須嚴格使用地道【香港足球術語】（波膽、大細球、受讓、讓球、上/下盤、派彩快、走印、針、半全場、熱門、爆冷）。
3. 必須嚴格按照以下「8大板塊」的順序輸出，每板塊加上清晰的 Emoji 標題，文字精煉吸睛，適合 Telegram 閱讀：

1. 預計首發陣容及理由（結合新人和傷停）
2. 近期狀態與戰術對決
3. 傷停情況、交手紀錄及背景動機（強調最新戰意）
4. 投注價值推薦（對比賠率，找出最穩健的選項）
5. 風險及冷門可能性
6. 全體預測
7. 預測比分（波膽）
8. 最終總結（加入溫馨提示：若半場形勢有暗湧，用家可自行決定使用馬會「派彩快」提早走印鎖定利潤）
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2
        }
    }
