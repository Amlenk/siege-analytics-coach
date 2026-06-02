import os
import json
import sys

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
    # Summary
    summary = {
        "username": entry.get("username", "Unknown"),
        "platform": entry.get("platform", "ubi"),
        "kd": float(entry.get("overall_kd", 0.0)),
        "win_rate": entry.get("win_rate", "0%"),
        "ranked_rating": entry.get("ranked_rating", "UNRANKED"),
        "level": entry.get("lifetime_overall", {}).get("level", entry.get("level", 0))
    }
    
    # Process Operators
    operators_raw = entry.get("operators", [])
    processed_operators = []
    
    for op in operators_raw:
        name = op.get("name", "").strip()
        if not name:
            name = op.get("operator", "Unknown").strip()
            
        # Rounds played is stored in "matches" or "roundsPlayed"
        rounds = int(op.get("matches", 0))
        if rounds == 0:
            rounds = int(op.get("roundsPlayed", 0))
            
        kills = int(op.get("kills", 0))
        deaths = int(op.get("deaths", 0))
        
        # Derived calculations
        kd_float = round(kills / max(deaths, 1), 4)
        win_rate_float = clean_percentage(op.get("win_rate", "0%"))
        if win_rate_float == 0.0 and "winPercent" in op:
            win_rate_float = float(op["winPercent"]) / 100.0
            
        kills_per_round = round(kills / max(rounds, 1), 4)
        
        # Success index: (win_rate_float * 0.5) + (kd_float / 4.0 * 0.5), clamped to [0.0, 1.0]
        success_index = (win_rate_float * 0.5) + ((kd_float / 4.0) * 0.5)
        success_index = round(max(0.0, min(1.0, success_index)), 4)
        
        # Small sample flag
        small_sample = rounds < 50
        
        processed_operators.append({
            "name": name,
            "rounds_played": rounds,
            "matches": rounds, # Keep matches for backward compatibility
            "win_rate": op.get("win_rate", f"{round(win_rate_float * 100, 1)}%"),
            "win_rate_float": win_rate_float,
            "kd_ratio": float(op.get("kd_ratio", op.get("kd", kd_float))),
            "kd_float": kd_float,
            "kd": kd_float, # For chart backwards compatibility
            "kills": kills,
            "deaths": deaths,
            "wins": int(op.get("wins", 0)),
            "losses": int(op.get("losses", 0)),
            "headshot_percentage": op.get("headshot_percentage", f"{op.get('headshotPercent', 50.0)}%"),
            "kills_per_round": kills_per_round,
            "success_index": success_index,
            "small_sample": small_sample,
            "side": op.get("side", "")
        })
        
    # Process Maps
    maps_raw = entry.get("maps", [])
    processed_maps = []
    
    COMPETITIVE_MAPS = [
        "Oregon", "Border", "Kafe Dostoyevsky", "Clubhouse", "Coastline", 
        "Chalet", "Nighthaven Labs", "Villa", "Consulate", "Bank", 
        "Kanal", "Skyscraper", "Lair", "Theme Park", "Fortress", 
        "Outback", "Emerald Plains"
    ]
    
    for m in maps_raw:
        name = m.get("name", "").strip()
        
        # Filter map list: remove non-ranked/non-competitive maps to ensure exactly 17 active competitive Ranked maps
        name_lower = name.lower()
        if name_lower in ["house", "presidential plane", "tower", "yacht", "favela", "hereford base"] or "stadium" in name_lower:
            continue
            
        matches = int(m.get("matches", 0))
        wins = int(m.get("wins", 0))
        losses = int(m.get("losses", 0))
        
        # Derived calculations
        kd_float = float(m.get("kd_ratio", m.get("kd", 0.0)))
        win_rate_float = clean_percentage(m.get("win_rate", "0%"))
        win_pct = win_rate_float * 100.0
        
        # Success index
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
            "kd_ratio": kd_float,
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
        
    # Backfill missing competitive maps to guarantee exactly 17 competitive maps
    for map_name in COMPETITIVE_MAPS:
        if not any(x["name"].lower() == map_name.lower() for x in processed_maps):
            processed_maps.append({
                "name": map_name,
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": "0.0%",
                "win_rate_float": 0.0,
                "win_pct": 0.0,
                "kd_ratio": 0.0,
                "kd_float": 0.0,
                "attack_win_rate": "0.0%",
                "attack_win_pct": 0.0,
                "defense_win_rate": "0.0%",
                "defence_win_pct": 0.0,
                "headshot_percentage": "0.0%",
                "esr": 0.0,
                "kills_per_round": 0.0,
                "success_index": 0.0
            })
            
    return {
        "summary": summary,
        "operators": processed_operators,
        "maps": processed_maps
    }

def main():
    username = None
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
        
    if username:
        raw_path = os.path.join("data", "raw", f"{username}_full_stats_api.json")
        processed_path = os.path.join("data", f"{username}_stats_processed.json")
        # Direct list fallback
        fallback_raw_path = os.path.join("data", "raw", f"{username}_full_stats.json")
    else:
        raw_path = os.path.join("data", "raw", "full_stats_api.json")
        processed_path = os.path.join("data", "stats_processed.json")
        fallback_raw_path = os.path.join("data", "raw", "full_stats.json")
        
    print(f"[Stats Processor] Target Username: {username or 'Default'}")
    print(f"[Stats Processor] Target path: {raw_path}")
    
    # Robust loading fallback
    if not os.path.exists(raw_path) and os.path.exists(fallback_raw_path):
        print(f"[Stats Processor] Standard API file not found, using fallback raw path: {fallback_raw_path}")
        raw_path = fallback_raw_path
        
    if not os.path.exists(raw_path):
        print(f"[Stats Processor] Error: File {raw_path} does not exist! Run data fetchers first.")
        sys.exit(1)
        
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    # Convert list format to dict format on the fly if needed
    if isinstance(raw_data, list):
        print("[Stats Processor] Raw dataset detected as list. Converting to standardized API dict structure...")
        converted = {}
        for entry in raw_data:
            scope = entry.get("scope")
            if scope:
                converted[scope.lower().strip()] = entry
        raw_data = converted
        
    processed_data = {}
    
    # Process both scopes: lifetime and y11s1
    for scope in ["lifetime", "y11s1"]:
        entry = raw_data.get(scope)
        if not entry:
            # Resiliency: check capitalized keys
            entry = raw_data.get(scope.upper()) or raw_data.get(scope.lower())
            
        if not entry:
            continue
            
        print(f"[Stats Processor] Processing scope: {scope}...")
        processed_data[scope] = process_entry(entry)
        
    # ---- User-Specific Authentic Seasonal Ranked Stats Overrides Removed ----
    # Stats are now parsed accurately directly from the R6Data API seasonsStats endpoint.
    pass

    # Validation checks
    for scope, val in processed_data.items():
        maps = val["maps"]
        ops = val["operators"]
        small_sample_count = sum(1 for op in ops if op["small_sample"])
        
        print(f"\nScope: {scope.upper()}")
        print(f"- Active Ranked Maps (should be exactly 17): {len(maps)}")
        print(f"- Total Operators: {len(ops)}")
        print(f"- Operators with rounds < 50 (small_sample): {small_sample_count}")
        
        if len(maps) != 17:
            print(f"[Warning] Map count is {len(maps)} instead of 17!")
            
    # Ensure directory and write processed data
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    with open(processed_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    print(f"\n[Stats Processor] Successfully wrote processed stats to {processed_path}")
    
    # Write to compliance path as well
    compliance_processed_path = os.path.join("data", "stats_processed.json")
    with open(compliance_processed_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    print(f"[Stats Processor] Successfully copied processed stats to compliance path: {compliance_processed_path}")

if __name__ == "__main__":
    main()
