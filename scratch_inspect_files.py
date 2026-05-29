import json

def main():
    print("=== INSPECTING SCRATCH STATS ===")
    with open('scratch_stats.json', 'r') as f:
        stats = json.load(f)
    print("stats.json Keys:", list(stats.keys()))
    if 'platform_families_full_profiles' in stats:
        pf = stats['platform_families_full_profiles']
        print("pf is a list of length:", len(pf))
        if pf:
            first_profile = pf[0]
            print("First profile keys:", list(first_profile.keys()))
            if 'segments' in first_profile:
                segments = first_profile['segments']
                print(f"  Segments count: {len(segments)}")
                for s in segments:
                    print(f"    Segment type: {s.get('type')}, gamemode: {s.get('attributes', {}).get('gamemode')}")
                    # If it's overall or ranked, print some stats
                    if s.get('type') == 'overview' or s.get('attributes', {}).get('gamemode') == 'pvp_ranked':
                        print("      Stats keys:", list(s.get('stats', {}).keys()))
                        print("      Sample KD:", s.get('stats', {}).get('kdRatio', {}))
                        print("      Sample Win%:", s.get('stats', {}).get('winPercentage', {}))

    print("\n=== INSPECTING SCRATCH SEASONSSTATS ===")
    with open('scratch_seasonsStats.json', 'r') as f:
        seasons = json.load(f)
    print("seasonsStats Keys:", list(seasons.keys()))
    if 'data' in seasons:
        d = seasons['data']
        print("data Keys:", list(d.keys()))
        if 'segments' in d:
            seg = d['segments']
            print(f"Segments count: {len(seg)}")
            if seg:
                print("First segment keys:", list(seg[0].keys()))
                print("First segment metadata:", seg[0].get('metadata'))
                print("First segment attributes:", seg[0].get('attributes'))
                # Print stats of the first segment
                print("First segment stats sample:", list(seg[0].get('stats', {}).keys()))
                # Let's list some seasons represented in seg
                seasons_found = []
                for s in seg:
                    attr = s.get('attributes', {})
                    meta = s.get('metadata', {})
                    seasons_found.append(f"{attr.get('season') or '?'}: {meta.get('name') or '?'}")
                print("Seasons found in segments:", seasons_found[:5])
                
                # Let's check stats for the first season segment
                first_seg_stats = seg[0].get('stats', {})
                print("First segment stats values:")
                for k, v in first_seg_stats.items():
                    print(f"  {k}: {v}")

if __name__ == '__main__':
    main()
