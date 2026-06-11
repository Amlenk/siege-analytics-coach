import json
import requests

BASE_URL = "https://api.r6data.com"
API_KEY = "19aad1d4a7e1f98d88d4b4b5a5227a56e3a5cec775898443fa90695f25c4ed4ad93c0110c75ab98c42477aa5f3af8d172cea056daa7a2df04749bb4304dbfef0"
headers = {"api-key": API_KEY}

def parse_operator_stats_response(raw_resp):
    operators_raw = []
    if isinstance(raw_resp, list):
        operators_raw = raw_resp
    elif isinstance(raw_resp, dict):
        if "operators" in raw_resp:
            operators_raw = raw_resp["operators"]
        elif "data" in raw_resp:
            data = raw_resp["data"]
            if isinstance(data, list):
                operators_raw = data
            elif isinstance(data, dict) and "operators" in data:
                operators_raw = data["operators"]
    
    parsed = []
    for op in operators_raw:
        if not isinstance(op, dict):
            continue
        name = op.get("operator", op.get("name", ""))
        if not name:
            continue
        rounds_played = int(op.get("roundsPlayed", op.get("rounds_played", 0)))
        wins = int(op.get("wins", 0))
        losses = int(op.get("losses", 0))
        kills = int(op.get("kills", 0))
        deaths = int(op.get("deaths", 0))
        
        if "winPercent" in op:
            wr_raw = float(op["winPercent"])
            win_rate_str = f"{wr_raw:.1f}%"
        elif wins + losses > 0:
            wr_raw = (wins / (wins + losses)) * 100
            win_rate_str = f"{wr_raw:.1f}%"
        else:
            win_rate_str = "0.0%"

        kd = round(kills / max(deaths, 1), 2)
        hs_pct_raw = op.get("headshotPercent", op.get("headshot_percentage", 0.0))
        if isinstance(hs_pct_raw, str) and '%' in hs_pct_raw:
            hs_str = hs_pct_raw
        else:
            hs_str = f"{float(hs_pct_raw):.1f}%"

        side = op.get("side", "")
        # Fallback side detection
        if not side:
            ATTACKERS = {'Thatcher', 'Hibana', 'Maverick', 'Deimos', 'Blackbeard', 'Glaz', 'Jackal', 'Sledge', 'Grim', 'Ram', 'Sens', 'Striker', 'Rauora', 'Lion', 'Brava', 'Fuze', 'Blitz', 'Twitch', 'Osa', 'Thermite', 'Solid Snake', 'Ash', 'Dokkaebi', 'Gridlock', 'Ying', 'Capitão', 'Capito', 'Nøkk', 'Nkk', 'Zofia', 'Zero', 'Kali', 'IQ', 'Buck', 'Iana', 'Amaru', 'Montagne', 'Flores', 'Nomad', 'Ace'}
            side = "Attacker" if name in ATTACKERS else "Defender"

        if rounds_played > 0:
            parsed.append({
                "name": name,
                "matches": rounds_played,
                "win_rate": win_rate_str,
                "kd_ratio": kd,
                "kills": kills,
                "deaths": deaths,
                "wins": wins,
                "losses": losses,
                "headshot_percentage": hs_str,
                "side": side
            })
    return parsed

print("Fetching Y11S1 operator stats...")
params = {
    "type": "operatorStats",
    "nameOnPlatform": "WamaiDoingThis",
    "platformType": "uplay",
    "modes": "ranked",
    "seasonYear": "Y11S1"
}
resp = requests.get(f"{BASE_URL}/api/stats", params=params, headers=headers, timeout=10)
if resp.status_code == 200:
    parsed_ops = parse_operator_stats_response(resp.json())
    print(f"Parsed {len(parsed_ops)} operators for Y11S1.")
    with open("data/raw/WamaiDoingThis_y11s1_ops.json", "w", encoding="utf-8") as f:
        json.dump(parsed_ops, f, indent=2, ensure_ascii=False)
    print("Saved to data/raw/WamaiDoingThis_y11s1_ops.json")
else:
    print(f"Error fetching Y11S1 operators: {resp.status_code} - {resp.text}")
