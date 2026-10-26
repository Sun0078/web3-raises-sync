import json
import os
import re
import urllib.request

TIER1_VCS = [
    "PARADIGM", "A16Z", "BINANCE LABS", "POLYCHAIN", "DRAGONFLY", 
    "COINBASE", "SEQUOIA", "PANTERA", "MULTICOIN", "HASHKEY", "WINTERMUTE", "JUMP"
]

def fetch_rss_feed():
    url = "https://cointelegraph.com/rss/tag/fundraising"
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    
    projects = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", content)
            if not titles:
                titles = re.findall(r"<title>(.*?)</title>", content)
                
            for title in titles[1:30]:
                match = re.search(r"([A-Z][a-zA-Z0-9_\s]{2,15})\s+(?:raises|secures|bags|closes)\s+(\$[\d\.]+[M|K|B]?)", title, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    amount = match.group(2).strip()
                    
                    upper_title = title.upper()
                    matched_vc = "Web3 VC"
                    is_t1 = 0
                    for vc in TIER1_VCS:
                        if vc in upper_title:
                            matched_vc = vc
                            is_t1 = 1
                            break
                    
                    projects.append({
                        "name": name.upper(),
                        "symbol": name.upper(),
                        "vc": matched_vc,
                        "t1": is_t1,
                        "round": f"融资 {amount}"
                    })
    except Exception as e:
        print(f"Fetch RSS warning: {e}")
        
    return projects

def main():
    history_file = "raises.json"
    existing_data = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            existing_data = []
            
    new_projects = fetch_rss_feed()
    
    merged_map = {item["name"]: item for item in existing_data}
    for p in new_projects:
        merged_map[p["name"]] = p
        
    final_list = list(merged_map.values())[:300]
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully synced {len(final_list)} projects.")

if __name__ == "__main__":
    main()
