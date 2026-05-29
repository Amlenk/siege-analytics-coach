import os
import json

def clean_percentage(pct_str):
    if pct_str is None:
        return 0.0
    if isinstance(pct_str, (int, float)):
        return float(pct_str)
    try:
        return float(str(pct_str).replace('%', '').strip()) / 100.0
    except Exception:
        return 0.0

def process_entry(entry):
    summary = {
        "username": entry.get("username", "Unknown"),
        "platform": entry.get("platform", "ubi"),
        "kd": float(entry.get("overall_kd", 0.0)),
        "win_rate": entry.get("win_rate", "0%"),
        "ranked_rating": entry.get("ranked_rating", "UNRANKED")
    }
    
    # Process Operators
    operators_raw = entry.get("operators", [])
    processed_operators = []
    
    for op in operators_raw:
        name = op.get("name", "").strip()
        if not name:
            name = op.get("operator", "Unknown").strip()
            
        rounds = int(op.get("matches", 0))
        if rounds == 0:
            rounds = int(op.get("roundsPlayed", 0))
            
        kills = int(op.get("kills", 0))
        deaths = int(op.get("deaths", 0))
        
        kd_float = round(kills / max(deaths, 1), 4)
        win_rate_float = clean_percentage(op.get("win_rate", "0%"))
        if win_rate_float == 0.0 and "winPercent" in op:
            win_rate_float = float(op["winPercent"]) / 100.0
            
        kills_per_round = round(kills / max(rounds, 1), 4)
        
        # Success index
        success_index = (win_rate_float * 0.5) + ((kd_float / 4.0) * 0.5)
        success_index = round(max(0.0, min(1.0, success_index)), 4)
        
        small_sample = rounds < 50
        
        processed_operators.append({
            "name": name,
            "rounds_played": rounds,
            "matches": rounds,
            "win_rate": op.get("win_rate", f"{round(win_rate_float * 100, 1)}%"),
            "win_rate_float": win_rate_float,
            "kd_ratio": float(op.get("kd_ratio", op.get("kd", kd_float))),
            "kd_float": kd_float,
            "kd": kd_float,
            "kills": kills,
            "deaths": deaths,
            "wins": int(op.get("wins", 0)),
            "losses": int(op.get("losses", 0)),
            "headshot_percentage": op.get("headshot_percentage", f"{op.get('headshotPercent', 50.0)}%"),
            "kills_per_round": kills_per_round,
            "success_index": success_index,
            "small_sample": small_sample
        })
        
    # Process Maps
    maps_raw = entry.get("maps", [])
    processed_maps = []
    
    for m in maps_raw:
        name = m.get("name", "").strip()
        name_lower = name.lower()
        # Filter map list: remove any map named "House", "Presidential Plane", "Tower", or containing "Stadium"
        if name_lower in ["house", "presidential plane", "tower"] or "stadium" in name_lower:
            continue
            
        matches = int(m.get("matches", 0))
        wins = int(m.get("wins", 0))
        losses = int(m.get("losses", 0))
        
        kd_float = float(m.get("kd_ratio", m.get("kd", 0.0)))
        win_rate_float = clean_percentage(m.get("win_rate", "0%"))
        win_pct = win_rate_float * 100.0
        
        success_index = (win_rate_float * 0.5) + ((kd_float / 4.0) * 0.5)
        success_index = round(max(0.0, min(1.0, success_index)), 4)
        
        processed_maps.append({
            "name": name,
            "matches": matches,
            "wins": wins,
            "losses": losses,
            "win_rate": m.get("win_rate", "0%"),
            "win_rate_float": win_rate_float,
            "win_pct": win_pct,
            "kd_ratio": float(m.get("kd_ratio", 0.0)),
            "kd_float": kd_float,
            "attack_win_rate": m.get("attack_win_rate", "0%"),
            "attack_win_pct": clean_percentage(m.get("attack_win_rate", "0%")) * 100.0,
            "defense_win_rate": m.get("defense_win_rate", "0%"),
            "defence_win_pct": clean_percentage(m.get("defense_win_rate", "0%")) * 100.0,
            "headshot_percentage": m.get("headshot_percentage", "0%"),
            "esr": float(m.get("esr", 0.0)),
            "kills_per_round": 0.0,
            "success_index": success_index
        })
        
    return {
        "summary": summary,
        "operators": processed_operators,
        "maps": processed_maps
    }

def main():
    raw_path = os.path.join("data", "raw", "full_stats_api.json")
    processed_path = os.path.join("data", "stats_processed.json")
    
    print(f"[r6data.eu Parser] Loading raw full stats from {raw_path}...")
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} does not exist! Run fetch_stats.py first.")
        return
        
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    processed_data = {}
    
    # Process both scopes: lifetime and y11s1
    for scope in ["lifetime", "y11s1"]:
        entry = raw_data.get(scope)
        if not entry:
            continue
            
        print(f"[r6data.eu Parser] Processing scope: {scope}...")
        processed_data[scope] = process_entry(entry)
        
    # Validation checks
    for scope, val in processed_data.items():
        maps = val["maps"]
        ops = val["operators"]
        small_sample_count = sum(1 for op in ops if op["small_sample"])
        
        print(f"\nScope: {scope.upper()}")
        print(f"- Active Ranked Maps (should be 17): {len(maps)}")
        print(f"- Total Operators (should be > 15): {len(ops)}")
        print(f"- Operators with rounds < 50 (small_sample): {small_sample_count}")
        
        if len(maps) != 17:
            print(f"[Warning] Map count is {len(maps)} instead of 17!")
            
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    with open(processed_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    print(f"\n[r6data.eu Parser] Successfully wrote unified stats to {processed_path}")

if __name__ == "__main__":
    main()
