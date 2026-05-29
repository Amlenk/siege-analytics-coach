import json
import os

def inspect_player(username):
    print(f"\n================ INSPECTING {username.upper()} ================")
    raw_path = f"data/raw/{username}_r6data_account_raw.json"
    if not os.path.exists(raw_path):
        print(f"File not found: {raw_path}")
        return
        
    with open(raw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Seasons stats
    # Wait, in the raw file, does "seasonal" store seasonal rank history or did we fetch seasonsStats?
    # Let's check what is in "seasonal" key of the saved file
    seasonal = data.get("seasonal", {})
    s_data = seasonal.get("data", {})
    
    # Wait, in the actual r6data_fetch.py:
    # client.get_seasonal_stats(username, platform) was called and saved under {"seasonal": seasonal_raw}
    # Wait, did we fetch seasonsStats in r6data_fetch.py?
    # No, r6data_fetch.py did:
    # seasonal_raw = client.get_seasonal_stats(username, platform)
    # But it did NOT write seasons_history to data/raw!
    # Wait, let's see what keys are in the raw file:
    print("Raw file keys:", list(data.keys()))
    
    # Let's inspect the operators raw file
    ops_path = f"data/raw/{username}_r6data_ops_raw.json"
    if os.path.exists(ops_path):
        with open(ops_path, 'r', encoding='utf-8') as f:
            ops_raw = json.load(f)
        print(f"Ops raw is list/dict? {type(ops_raw)}")
        if isinstance(ops_raw, list):
            print(f"  Total operators: {len(ops_raw)}")
            if ops_raw:
                print("  First op sample:", ops_raw[0])
        elif isinstance(ops_raw, dict):
            print("  Keys:", list(ops_raw.keys()))

if __name__ == '__main__':
    for user in ["Amlenk", "Covetous_Demon", "WamaiDoingThis"]:
        inspect_player(user)
