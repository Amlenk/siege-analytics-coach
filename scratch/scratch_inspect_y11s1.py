import json

with open("data/raw/WamaiDoingThis_y11s1_stats.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Keys: {list(data.keys())}")
print(f"Season: {data.get('season')}")
print(f"Matches: {data.get('lifetime_overall', {}).get('matches')}")
print(f"Wins: {data.get('lifetime_overall', {}).get('wins')}")
print(f"Losses: {data.get('lifetime_overall', {}).get('losses')}")
print(f"Kills: {data.get('lifetime_overall', {}).get('kills')}")
print(f"Deaths: {data.get('lifetime_overall', {}).get('deaths')}")

if "maps" in data:
    print(f"Maps: {len(data['maps'])}")
    if len(data['maps']) > 0:
        print(f"  First map: {data['maps'][0]}")
if "operators" in data:
    print(f"Operators: {len(data['operators'])}")
    if len(data['operators']) > 0:
        print(f"  First operator: {data['operators'][0]}")
