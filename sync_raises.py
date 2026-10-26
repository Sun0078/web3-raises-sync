import json
import os
import re
import urllib.request

TIER1_VCS = [
    "PARADIGM", "A16Z", "BINANCE LABS", "POLYCHAIN", "DRAGONFLY", 
    "COINBASE", "SEQUOIA", "PANTERA", "MULTICOIN", "HASHKEY", "WINTERMUTE", "JUMP"
]

# 初始内置的活跃真实项目库（防止首次抓取为空）
INITIAL_BASE_PROJECTS = [
    {"name": "EIGENLAYER", "symbol": "EIGEN", "vc": "BINANCE LABS", "t1": 1, "round": "融资 $100M"},
    {"name": "ETHENA", "symbol": "ENA", "vc": "DRAGONFLY", "t1": 1, "round": "融资 $14M"},
    {"name": "MONAD", "symbol": "MONAD", "vc": "PARADIGM", "t1": 1, "round": "融资 $225M"},
    {"name": "BERACHAIN", "symbol": "BERA", "vc": "PARADIGM", "t1": 1, "round": "融资 $100M"},
    {"name": "STORY PROTOCOL", "symbol": "IP", "vc": "A16Z", "t1": 1, "round": "融资 $80M"},
    {"name": "BABYLON", "symbol": "BBN", "vc": "PARADIGM", "t1": 1, "round": "融资 $70M"},
    {"name": "MOVEMENT", "symbol": "MOVE", "vc": "POLYCHAIN", "t1": 1, "round": "融资 $38M"},
    {"name": "INITIA", "symbol": "INIT", "vc": "BINANCE LABS", "t1": 1, "round": "融资 $14M"},
    {"name": "ECLIPSE", "symbol": "ECLIPSE", "vc": "POLYCHAIN", "t1": 1, "round": "融资 $50M"},
    {"name": "SAKAI VAULT", "symbol": "SAKAI", "vc": "WEB3 VC", "t1": 0, "round": "融资 社区"}
]

def fetch_rss_feed():
    urls = [
        "https://cointelegraph.com/rss/tag/fundraising",
        "https://coindesk.com/arc/outboundfeeds/rss/?outputType=xml"
    ]
    
    projects = []
    for url in urls:
        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
                titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", content)
                if not titles:
                    titles = re.findall(r"<title>(.*?)</title>", content)
                    
                for title in titles[1:25]:
                    match = re.search(r"([A-Za-z0-9_\s]{2,15})\s+(?:raises|secures|bags|closes|gets)\s+(\$[\d\.]+[M|K|B]?)", title, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip().upper()
                        amount = match.group(2).strip()
                        
                        upper_title = title.upper()
                        matched_vc = "WEB3 VC"
                        is_t1 = 0
                        for vc in TIER1_VCS:
                            if vc in upper_title:
                                matched_vc = vc
                                is_t1 = 1
                                break
                        
                        projects.append({
                            "name": name,
                            "symbol": name,
                            "vc": matched_vc,
                            "t1": is_t1,
                            "round": f"融资 {amount}"
                        })
        except Exception as e:
            print(f"Fetch {url} warning: {e}")
            
    return projects

def main():
    history_file = "raises.json"
    existing_data = []
    
    # 1. 尝试读取历史数据
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            existing_data = []
            
    # 2. 如果历史是空的，注入底座数据
    if not existing_data:
        existing_data = INITIAL_BASE_PROJECTS
        
    # 3. 抓取最新新闻
    new_projects = fetch_rss_feed()
    
    # 4. 去重合并
    merged_map = {item["name"]: item for item in existing_data}
    for p in new_projects:
        merged_map[p["name"]] = p
        
    final_list = list(merged_map.values())[:300]
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully synced {len(final_list)} projects.")

if __name__ == "__main__":
    main()
