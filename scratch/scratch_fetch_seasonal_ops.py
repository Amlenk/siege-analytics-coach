import json
import requests

BASE_URL = "https://api.r6data.com"
API_KEY = "19aad1d4a7e1f98d88d4b4b5a5227a56e3a5cec775898443fa90695f25c4ed4ad93c0110c75ab98c42477aa5f3af8d172cea056daa7a2df04749bb4304dbfef0"
headers = {"api-key": API_KEY}

def test_season(season_val):
    params = {
        "type": "operatorStats",
        "nameOnPlatform": "WamaiDoingThis",
        "platformType": "uplay",
        "modes": "ranked",
        "seasonYear": season_val
    }
    resp = requests.get(f"{BASE_URL}/api/stats", params=params, headers=headers, timeout=10)
    print(f"Season: {season_val}, Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        ops = data.get("operators", []) if isinstance(data, dict) else data
        print(f"  Total operators: {len(ops)}")
        if ops:
            print(f"  First op: {ops[0].get('operator')} - wins: {ops[0].get('wins')}, losses: {ops[0].get('losses')}, kills: {ops[0].get('kills')}, deaths: {ops[0].get('deaths')}, rounds: {ops[0].get('roundsPlayed')}")
        return ops
    return []

print("Fetching Season 41 (Y11S1)...")
ops_s41 = test_season("Y11S1")

print("\nFetching Season 42 (Y11S2)...")
ops_s42 = test_season("Y11S2")
