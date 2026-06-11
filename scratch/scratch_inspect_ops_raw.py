import json

with open("data/raw/WamaiDoingThis_r6data_ops_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Season Year: {data.get('seasonYear')}")
print(f"Season Number: {data.get('seasonNumber')}")
print(f"Total ops: {len(data.get('operators', []))}")
if len(data.get('operators', [])) > 0:
    print(f"First op: {data['operators'][0]}")
