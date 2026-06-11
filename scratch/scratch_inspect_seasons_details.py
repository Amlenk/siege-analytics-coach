import json

with open("data/raw/WamaiDoingThis_seasons_history.json", "r") as f:
    data = json.load(f)

segments = data if isinstance(data, list) else data.get("data", {}).get("segments", [])
for s in segments:
    attr = s.get("attributes", {})
    if attr.get("gamemode") == "pvp_ranked" and attr.get("season") in [41, 42]:
        print(f"Season ID: {attr.get('season')} ({s.get('metadata', {}).get('name')})")
        stats = s.get("stats", {})
        for k, v in stats.items():
            if "value" in v or "displayValue" in v:
                print(f"  {k}: {v.get('value')} ({v.get('displayValue')})")
