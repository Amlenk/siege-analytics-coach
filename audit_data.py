import json

with open('data/stats_processed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for scope in ['lifetime', 'y11s1']:
    s = data.get(scope, {})
    summ = s.get('summary', {})
    ops = s.get('operators', [])
    maps = s.get('maps', [])
    print('=== SCOPE:', scope.upper(), '===')
    print('Summary:', json.dumps(summ, indent=2))
    print('Operators:', len(ops), 'total')
    top5 = sorted(ops, key=lambda x: x.get('rounds_played',0), reverse=True)[:5]
    for o in top5:
        n = o['name'].strip()
        r = o['rounds_played']
        k = o['kd_ratio']
        w = o['win_rate']
        print('  ', n, r, 'rounds  kd=' + str(k), 'wr=' + w)
    print('Maps:', len(maps))
    if maps:
        print('First map:', json.dumps(maps[0], indent=2))
    print()

with open('data/raw/full_stats.json', 'r', encoding='utf-8') as f:
    fs = json.load(f)
print('=== FULL_STATS.JSON ===')
for entry in fs:
    lo = entry.get('lifetime_overall', {})
    print('scope=' + str(entry.get('scope')), 'user=' + str(entry.get('username')),
          'kd=' + str(entry.get('overall_kd')), 'wr=' + str(entry.get('win_rate')),
          'rank=' + str(entry.get('ranked_rating')))
    print('  level=' + str(lo.get('level')), 'matches=' + str(lo.get('matches')),
          'kills=' + str(lo.get('kills')), 'deaths=' + str(lo.get('deaths')))
