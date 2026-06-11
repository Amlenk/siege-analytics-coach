import json

with open("data/raw/WamaiDoingThis_seasons_history.json", "r") as f:
    data = json.load(f)

segments = data if isinstance(data, list) else data.get("data", {}).get("segments", [])
print(f"Total segments: {len(segments)}")
for s in segments:
    attr = s.get("attributes", {})
    if attr.get("gamemode") == "pvp_ranked":
        print(f"Season ID: {attr.get('season')}, Name: {s.get('metadata', {}).get('name')}, Matches: {s.get('stats', {}).get('matchesPlayed', {}).get('value')}")
