import json

d = json.load(open('data/stats_processed.json', 'r', encoding='utf-8'))
ops = d['y11s1']['operators']
for o in sorted(ops, key=lambda x: x['rounds_played'], reverse=True):
    print(f"{o['name']:20s} KD={o['kd_ratio']:.2f}  WR={o['win_rate']:6s}  Rnds={o['rounds_played']:4d}  K={o['kills']:3d} D={o['deaths']:3d}")
