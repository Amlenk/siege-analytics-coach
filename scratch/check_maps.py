import os
import json

players = ['Amlenk', 'WamaiDoingThis', 'Covetous_Demon']
for p in players:
    lt_path = f'data/raw/{p}_maps.json'
    s_path = f'data/raw/{p}_y11s1_maps.json'
    lt_exists = os.path.exists(lt_path)
    s_exists = os.path.exists(s_path)
    print(f"=== {p} ===")
    print(f"  Lifetime maps exists: {lt_exists}")
    print(f"  Seasonal maps exists: {s_exists}")
    if lt_exists:
        with open(lt_path) as f:
            lt_data = json.load(f)
        print(f"  Lifetime maps count: {len(lt_data)}")
        if len(lt_data) > 0:
            first_few = [f"{m['name']}: {m['matches']}" for m in lt_data[:3]]
            print(f"  First few lifetime maps: {first_few}")
    if s_exists:
        with open(s_path) as f:
            s_data = json.load(f)
        print(f"  Seasonal maps count: {len(s_data)}")
        if len(s_data) > 0:
            first_few_s = [f"{m['name']}: {m['matches']}" for m in s_data[:3]]
            print(f"  First few seasonal maps: {first_few_s}")
