import requests
import json
import os

# =====================================================================
# 1. 自動讀取 GitHub Secrets 保險箱密鑰（全新完全加密版）
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
                    # 成功抓到第一場有真實開盤嘅波
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
# 3. 呼叫 最新 Gemini 3.5 Flash 大腦 (加入極嚴格防發夢警告)
# =====================================================================
def generate_report_with_gemini(match_info):
    if not match_info:
        return None
        
    print("🧠 正在啟動 Gemini 3.5 Flash 大腦進行即時深度分析...")
    
    if not GEMINI_API_KEY:
        print("❌ 錯誤：找不到 GEMINI_API_KEY！")
        return None

    # 使用最新的 Gemini 3.5 Flash 官方 REST 端點網址
    url = f"
