import json
import os

def main():
    path = "data/raw/WamaiDoingThis_full_stats_api.json"
    if not os.path.exists(path):
        print(f"File {path} does not exist.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for scope in ["lifetime", "y11s1"]:
        entry = data.get(scope)
        if entry:
            print(f"\n=== Scope: {scope} ===")
            print("Username:", entry.get("username"))
            print("Platform:", entry.get("platform"))
            print("Overall K/D:", entry.get("overall_kd"))
            print("Win Rate:", entry.get("win_rate"))
            print("Ranked Rating:", entry.get("ranked_rating"))
            print("Season:", entry.get("season"))
            print("Lifetime Overall:")
            for k, v in entry.get("lifetime_overall", {}).items():
                print(f"  {k}: {v}")
            print(f"Operators count: {len(entry.get('operators', []))}")
            print(f"Maps count: {len(entry.get('maps', []))}")

if __name__ == '__main__':
    main()
