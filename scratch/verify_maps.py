import json
lt = json.load(open('data/raw/Covetous_Demon_maps.json'))
s = json.load(open('data/raw/Covetous_Demon_y11s1_maps.json'))
print('LIFETIME RANKED:')
for m in lt[:5]:
    print(f"  {m['name']}: {m['matches']} matches, WR: {m['win_rate']}")
print(f"\nY11S1 RANKED:")
for m in s[:5]:
    print(f"  {m['name']}: {m['matches']} matches, WR: {m['win_rate']}")
print(f"\nLifetime={len(lt)} maps, Y11S1={len(s)} maps")
print(f"Data differs: {lt != s}")
