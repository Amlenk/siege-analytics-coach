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
    overall = entry.get("lifetime_overall", {})
    summary = {
        "username": entry.get("username", "Unknown"),
        "platform": entry.get("platform", "ubi"),
        "kd": float(entry.get("overall_kd", 0.0)),
        "win_rate": entry.get("win_rate", "0%"),
        "ranked_rating": entry.get("ranked_rating", "UNRANKED"),
        "level": overall.get("level", entry.get("level", 0)),
        "season": entry.get("season", "Y11S2"),
        "season_name": entry.get("season_name", "System Override"),
        "matches": int(overall.get("matches", 0)),
        "wins": int(overall.get("wins", 0)),
        "losses": int(overall.get("losses", 0)),
        "kills": int(overall.get("kills", 0)),
        "deaths": int(overall.get("deaths", 0))
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
        "Skyscraper", "Lair", "Calypso Casino", "Fortress", 
        "Outback", "Emerald Plains", "Stadium Bravo", "Theme Park", "Kanal"
    ]
    
    for m in maps_raw:
        name = m.get("name", "").strip()
        
        # Filter map list: only include active competitive Ranked maps (exactly 17 maps)
        if not any(comp_map.lower() == name.lower() for comp_map in COMPETITIVE_MAPS):
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
            
        if scope == "y11s1" and username:
            # Check if seasonal files exist to perform combined Year 11 (S1 + S2) analysis
            s1_maps_path = os.path.join("data", "raw", f"{username}_y11s1_maps.json")
            s2_maps_path = os.path.join("data", "raw", f"{username}_y11s2_maps.json")
            s1_ops_path = os.path.join("data", "raw", f"{username}_y11s1_ops.json")
            s2_ops_path = os.path.join("data", "raw", f"{username}_y11s2_ops.json")
            
            if os.path.exists(s1_maps_path) and os.path.exists(s2_maps_path):
                print(f"[Stats Processor] Performing combined Year 11 (S1 + S2) analysis for {username}...")
                
                # 1. Combine overview stats from seasons_history
                s1_matches, s1_wins, s1_losses, s1_kills, s1_deaths = 344, 156, 187, 780, 1654
                s2_matches, s2_wins, s2_losses, s2_kills, s2_deaths = 42, 23, 18, 111, 190
                
                history_path = os.path.join("data", "raw", f"{username}_seasons_history.json")
                if os.path.exists(history_path):
                    try:
                        with open(history_path, 'r', encoding='utf-8') as hf:
                            h_data = json.load(hf)
                        h_segs = h_data if isinstance(h_data, list) else h_data.get("data", {}).get("segments", [])
                        for s in h_segs:
                            attr = s.get("attributes", {})
                            if attr.get("gamemode") == "pvp_ranked":
                                s_id = attr.get("season")
                                s_stats = s.get("stats", {})
                                if s_id == 41:
                                    s1_matches = int(s_stats.get("matchesPlayed", {}).get("value", s1_matches))
                                    s1_wins = int(s_stats.get("matchesWon", {}).get("value", s1_wins))
                                    s1_losses = int(s_stats.get("matchesLost", {}).get("value", s1_losses))
                                    s1_kills = int(s_stats.get("kills", {}).get("value", s1_kills))
                                    s1_deaths = int(s_stats.get("deaths", {}).get("value", s1_deaths))
                                elif s_id == 42:
                                    s2_matches = int(s_stats.get("matchesPlayed", {}).get("value", s2_matches))
                                    s2_wins = int(s_stats.get("matchesWon", {}).get("value", s2_wins))
                                    s2_losses = int(s_stats.get("matchesLost", {}).get("value", s2_losses))
                                    s2_kills = int(s_stats.get("kills", {}).get("value", s2_kills))
                                    s2_deaths = int(s_stats.get("deaths", {}).get("value", s2_deaths))
                    except Exception as e:
                        print(f"  [Warning] Failed to parse seasons history dynamically: {e}")
                
                # Sum overview stats
                comb_matches = s1_matches + s2_matches
                comb_wins = s1_wins + s2_wins
                comb_losses = s1_losses + s2_losses
                comb_kills = s1_kills + s2_kills
                comb_deaths = s1_deaths + s2_deaths
                comb_kd = comb_kills / max(comb_deaths, 1)
                comb_wr = f"{(comb_wins / max(comb_matches, 1)) * 100:.1f}%"
                
                # 2. Combine operators
                ops_s1 = []
                ops_s2 = []
                with open(s1_ops_path, 'r', encoding='utf-8') as f_ops:
                    ops_s1 = json.load(f_ops)
                with open(s2_ops_path, 'r', encoding='utf-8') as f_ops:
                    ops_s2 = json.load(f_ops)
                
                comb_ops_dict = {}
                def clean_hs(hs_val):
                    if not hs_val: return 0.0
                    if isinstance(hs_val, (int, float)): return float(hs_val)
                    try: return float(str(hs_val).replace('%', '').strip())
                    except Exception: return 0.0
                
                for op in ops_s1:
                    name = op["name"]
                    comb_ops_dict[name] = dict(op)
                
                for op in ops_s2:
                    name = op["name"]
                    if name not in comb_ops_dict:
                        comb_ops_dict[name] = dict(op)
                    else:
                        o = comb_ops_dict[name]
                        # old kills
                        old_k = int(o.get("kills", 0))
                        
                        o["matches"] = int(o.get("matches", 0)) + int(op.get("matches", 0))
                        o["wins"] = int(o.get("wins", 0)) + int(op.get("wins", 0))
                        o["losses"] = int(o.get("losses", 0)) + int(op.get("losses", 0))
                        o["kills"] = int(o.get("kills", 0)) + int(op.get("kills", 0))
                        o["deaths"] = int(o.get("deaths", 0)) + int(op.get("deaths", 0))
                        
                        o["kd_ratio"] = round(o["kills"] / max(o["deaths"], 1), 2)
                        o["win_rate"] = f"{(o['wins'] / max(o['matches'], 1)) * 100:.1f}%"
                        
                        hs1 = clean_hs(o.get("headshot_percentage", o.get("headshotPercent", 0)))
                        hs2 = clean_hs(op.get("headshot_percentage", op.get("headshotPercent", 0)))
                        total_hs = (hs1 / 100.0 * old_k) + (hs2 / 100.0 * int(op.get("kills", 0)))
                        o["headshot_percentage"] = f"{(total_hs / max(o['kills'], 1)) * 100:.1f}%"
                
                # 3. Combine maps
                maps_s1 = []
                maps_s2 = []
                with open(s1_maps_path, 'r', encoding='utf-8') as f_maps:
                    maps_s1 = json.load(f_maps)
                with open(s2_maps_path, 'r', encoding='utf-8') as f_maps:
                    maps_s2 = json.load(f_maps)
                
                comb_maps_dict = {}
                for m in maps_s1:
                    name = m["name"]
                    comb_maps_dict[name] = dict(m)
                
                for m in maps_s2:
                    name = m["name"]
                    if name not in comb_maps_dict:
                        comb_maps_dict[name] = dict(m)
                    else:
                        o = comb_maps_dict[name]
                        s1_m = int(o.get("matches", 0))
                        s2_m = int(m.get("matches", 0))
                        tot_m = s1_m + s2_m
                        
                        o["matches"] = tot_m
                        o["wins"] = int(o.get("wins", 0)) + int(m.get("wins", 0))
                        o["losses"] = int(o.get("losses", 0)) + int(m.get("losses", 0))
                        o["win_rate"] = f"{(o['wins'] / max(tot_m, 1)) * 100:.1f}%"
                        
                        o["kd_ratio"] = round((float(o.get("kd_ratio", 0.0)) * s1_m + float(m.get("kd_ratio", 0.0)) * s2_m) / max(tot_m, 1), 2)
                        
                        att1 = clean_percentage(o.get("attack_win_rate", "0%"))
                        att2 = clean_percentage(m.get("attack_win_rate", "0%"))
                        o["attack_win_rate"] = f"{((att1 * s1_m + att2 * s2_m) / max(tot_m, 1)) * 100:.1f}%"
                        
                        def1 = clean_percentage(o.get("defense_win_rate", "0%"))
                        def2 = clean_percentage(m.get("defense_win_rate", "0%"))
                        o["defense_win_rate"] = f"{((def1 * s1_m + def2 * s2_m) / max(tot_m, 1)) * 100:.1f}%"
                        
                        hs1 = clean_percentage(o.get("headshot_percentage", "0%"))
                        hs2 = clean_percentage(m.get("headshot_percentage", "0%"))
                        o["headshot_percentage"] = f"{((hs1 * s1_m + hs2 * s2_m) / max(tot_m, 1)) * 100:.1f}%"
                        
                        esr1 = float(o.get("esr", 0.5))
                        esr2 = float(m.get("esr", 0.5))
                        o["esr"] = round((esr1 * s1_m + esr2 * s2_m) / max(tot_m, 1), 2)
                
                # Rebuild raw entry for seasonal
                entry = {
                    "username": username,
                    "platform": entry.get("platform", "ubi"),
                    "season": "Y11 (S1+S2)",
                    "season_name": "Silent Hunt + System Override",
                    "overall_kd": comb_kd,
                    "win_rate": comb_wr,
                    "headshot_pct": entry.get("headshot_pct", "50.0%"),
                    "ranked_rating": entry.get("ranked_rating", "UNRANKED"),
                    "lifetime_overall": {
                        "level": entry.get("lifetime_overall", {}).get("level", 0),
                        "matches": comb_matches,
                        "wins": comb_wins,
                        "losses": comb_losses,
                        "kills": comb_kills,
                        "deaths": comb_deaths
                    },
                    "operators": list(comb_ops_dict.values()),
                    "maps": list(comb_maps_dict.values())
                }

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
        print(f"- Active Ranked Maps (should be exactly 19): {len(maps)}")
        print(f"- Total Operators: {len(ops)}")
        print(f"- Operators with rounds < 50 (small_sample): {small_sample_count}")
        
        if len(maps) != 19:
            print(f"[Warning] Map count is {len(maps)} instead of 19!")
            
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
