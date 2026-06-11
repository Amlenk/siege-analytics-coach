import json
import os

with open("data/raw/WamaiDoingThis_y11s1_maps.json", "r", encoding="utf-8") as f:
    maps_s1 = json.load(f)

with open("data/raw/WamaiDoingThis_y11s2_maps.json", "r", encoding="utf-8") as f:
    maps_s2 = json.load(f)

# Combine them by map name
combined = {}

for m in maps_s1:
    name = m["name"]
    combined[name] = {
        "name": name,
        "matches": m["matches"],
        "wins": m["wins"],
        "losses": m["losses"],
        "kills": m.get("kills", 0), # if present
        "deaths": m.get("deaths", 0), # if present
        "kd_ratio": m.get("kd_ratio", 0.0),
        "attack_win_rate": m.get("attack_win_rate", "0%"),
        "defense_win_rate": m.get("defense_win_rate", "0%"),
        "headshot_percentage": m.get("headshot_percentage", "0%"),
        "esr": m.get("esr", 0.50)
    }

for m in maps_s2:
    name = m["name"]
    if name not in combined:
        combined[name] = {
            "name": name,
            "matches": 0,
            "wins": 0,
            "losses": 0,
            "kills": 0,
            "deaths": 0,
            "kd_ratio": 0.0,
            "attack_win_rate": "0%",
            "defense_win_rate": "0%",
            "headshot_percentage": "0%",
            "esr": 0.50
        }
    
    c = combined[name]
    c["matches"] += m["matches"]
    c["wins"] += m["wins"]
    c["losses"] += m["losses"]
    
    # Simple average or weighted average of K/D, win rates, etc.
    # To do it properly, we should calculate from kills/deaths, but since we only have rate strings and matches:
    # Let's check if we can estimate the weights.
    # We will write a proper weight calculation function.

print(f"Total maps combined: {len(combined)}")
for name, c in sorted(combined.items(), key=lambda x: x[1]["matches"], reverse=True):
    print(f"Map: {name}, Combined Matches: {c['matches']}, Wins: {c['wins']}, Losses: {c['losses']}")
