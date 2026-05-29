"""Quick script to inspect the actual map data state for all players."""
import json, os

players = ["Amlenk", "WamaiDoingThis", "Covetous_Demon"]

for p in players:
    print(f"\n{'='*60}")
    print(f"PLAYER: {p}")
    print(f"{'='*60}")
    
    # Check the full_stats_api file for both lifetime and y11s1 maps
    api_path = f"data/raw/{p}_full_stats_api.json"
    if os.path.exists(api_path):
        with open(api_path, 'r') as f:
            data = json.load(f)
        
        lt_maps = data.get("lifetime", {}).get("maps", [])
        y11_maps = data.get("y11s1", {}).get("maps", [])
        
        print(f"\n  Lifetime maps: {len(lt_maps)}")
        for m in lt_maps[:5]:
            print(f"    {m['name']}: {m['matches']} matches, WR: {m['win_rate']}")
        if len(lt_maps) > 5:
            print(f"    ... and {len(lt_maps)-5} more")
        
        print(f"\n  Y11S1 maps: {len(y11_maps)}")
        for m in y11_maps[:5]:
            print(f"    {m['name']}: {m['matches']} matches, WR: {m['win_rate']}")
        if len(y11_maps) > 5:
            print(f"    ... and {len(y11_maps)-5} more")
        
        # Check if they're identical
        if lt_maps == y11_maps:
            print(f"\n  *** PROBLEM: Lifetime and Y11S1 maps are IDENTICAL! ***")
        else:
            print(f"\n  OK: Lifetime and Y11S1 maps differ")
    else:
        print(f"  No API file found at {api_path}")
    
    # Also check processed data
    proc_path = f"data/{p}_stats_processed.json"
    if os.path.exists(proc_path):
        with open(proc_path, 'r') as f:
            proc = json.load(f)
        
        lt_proc_maps = proc.get("lifetime", {}).get("maps", [])
        y11_proc_maps = proc.get("y11s1", {}).get("maps", [])
        
        print(f"\n  Processed lifetime maps: {len(lt_proc_maps)}")
        print(f"  Processed Y11S1 maps: {len(y11_proc_maps)}")
        
        if lt_proc_maps == y11_proc_maps:
            print(f"  *** PROBLEM: Processed maps are also IDENTICAL! ***")
