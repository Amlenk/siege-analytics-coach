import json
import requests

BASE_URL = "https://api.r6data.com"
API_KEY = "19aad1d4a7e1f98d88d4b4b5a5227a56e3a5cec775898443fa90695f25c4ed4ad93c0110c75ab98c42477aa5f3af8d172cea056daa7a2df04749bb4304dbfef0"
headers = {"api-key": API_KEY}

def main():
    username = "Amlenk"
    platform = "uplay"
    
    # Try different values for seasonYear parameter
    season_params = [41, "41", "Y11S1", "y11s1", "2026", "2026_season_41"]
    
    for s in season_params:
        print(f"\n--- Testing operatorStats with seasonYear = {s} ---")
        params = {
            "type": "operatorStats",
            "nameOnPlatform": username,
            "platformType": platform,
            "modes": "ranked",
            "seasonYear": s
        }
        try:
            resp = requests.get(f"{BASE_URL}/api/stats", params=params, headers=headers, timeout=10)
            print(f"Status Code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                # If it returns a dictionary, check if there's operators
                ops = []
                if isinstance(data, dict):
                    ops = data.get("operators", [])
                elif isinstance(data, list):
                    ops = data
                print(f"Returned {len(ops)} operators.")
                if ops:
                    # Print the first operator's roundsPlayed to see if it's seasonal or lifetime
                    # (In lifetime, Azami roundsPlayed is 697. In seasonal Y11S1, it's 45.)
                    op_sample = ops[0]
                    op_name = op_sample.get("operator", op_sample.get("name", "Unknown"))
                    rounds = op_sample.get("roundsPlayed", op_sample.get("rounds_played", 0))
                    print(f"First Op Sample: {op_name}, roundsPlayed: {rounds}")
            else:
                print("Error Response:", resp.text[:200])
        except Exception as e:
            print("Exception:", e)

if __name__ == '__main__':
    main()
