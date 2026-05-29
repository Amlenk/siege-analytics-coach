import json

with open('data/raw/Amlenk_y11s1_maps.json') as f:
    amlenk_maps = json.load(f)

with open('data/raw/Covetous_Demon_y11s1_maps.json') as f:
    covetous_maps = json.load(f)

print(f"Amlenk seasonal maps count: {len(amlenk_maps)}")
print("Amlenk maps:")
for m in amlenk_maps:
    print(f"  - {m['name']}: {m['matches']} matches")

print(f"\nCovetous seasonal maps count: {len(covetous_maps)}")
print("Covetous maps:")
for m in covetous_maps:
    print(f"  - {m['name']}: {m['matches']} matches")
