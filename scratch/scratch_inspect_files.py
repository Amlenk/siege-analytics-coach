import json
import os

for f_name in ["WamaiDoingThis_y11s1_maps.json", "WamaiDoingThis_y11s2_maps.json", "y11s1_stats.json"]:
    path = os.path.join("data", "raw", f_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            print(f"{f_name}: list of length {len(data)}")
            if len(data) > 0:
                print(f"  First item: {data[0]}")
        elif isinstance(data, dict):
            print(f"{f_name}: dict with keys {list(data.keys())}")
            if "maps" in data:
                print(f"  Maps key length: {len(data['maps'])}")
                if len(data['maps']) > 0:
                    print(f"    First map: {data['maps'][0]}")
            if "operators" in data:
                print(f"  Operators key length: {len(data['operators'])}")
                if len(data['operators']) > 0:
                    print(f"    First op: {data['operators'][0]}")
