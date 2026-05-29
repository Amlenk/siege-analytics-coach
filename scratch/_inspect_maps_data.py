import json

data = json.load(open('data/Amlenk_stats_processed.json', 'r'))
maps = sorted(data.get('y11s1', data.get('lifetime', {})).get('maps', []), key=lambda x: x.get('win_pct', 0), reverse=True)

for m in maps:
    att = m.get('attack_win_pct', 0)
    defe = m.get('defence_win_pct', 0)
    gap = abs(defe - att)
    side = "DEF-heavy" if defe > att else "ATT-heavy"
    print(f"{m['name']:20s} | W:{m['win_rate']:>6s} | A:{m['attack_win_rate']:>6s} | D:{m['defense_win_rate']:>6s} | gap:{gap:5.1f}% {side:10s} | KD:{m['kd_ratio']:.2f} | M:{m['matches']:>3d} | ESR:{m.get('esr',0):.2f}")
