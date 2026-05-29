import os
import json
import requests

BASE_URL = "https://api.r6data.com"
API_KEY = "19aad1d4a7e1f98d88d4b4b5a5227a56e3a5cec775898443fa90695f25c4ed4ad93c0110c75ab98c42477aa5f3af8d172cea056daa7a2df04749bb4304dbfef0"
headers = {"api-key": API_KEY}

def main():
    username = "Amlenk"
    platform = "uplay"
    
    endpoints = [
        ("/api/stats", {"type": "accountInfo", "nameOnPlatform": username, "platformType": platform}),
        ("/api/stats", {"type": "stats", "nameOnPlatform": username, "platformType": platform, "platform_families": "pc"}),
        ("/api/stats", {"type": "seasonalStats", "nameOnPlatform": username, "platformType": platform}),
        ("/api/stats", {"type": "seasonsStats", "nameOnPlatform": username, "platformType": platform})
    ]
    
    for endpoint, params in endpoints:
        print(f"\n--- Calling {endpoint} with {params['type']} ---")
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", params=params, headers=headers, timeout=10)
            print(f"Status Code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                # Print keys
                if isinstance(data, dict):
                    print("Keys:", list(data.keys()))
                    # Look for stats or matches or win rate
                    for key in ["stats", "data", "statistics"]:
                        if key in data:
                            val = data[key]
                            if isinstance(val, dict):
                                print(f"Sub-keys for '{key}':", list(val.keys()))
                            elif isinstance(val, list) and val:
                                print(f"List length for '{key}':", len(val))
                                if isinstance(val[0], dict):
                                    print(f"First list item keys:", list(val[0].keys()))
                elif isinstance(data, list):
                    print(f"Response is a list of length {len(data)}")
                    if data and isinstance(data[0], dict):
                        print("First item keys:", list(data[0].keys()))
                
                # Save full response to scratch to inspect manually
                fn = f"scratch_{params['type']}.json"
                with open(fn, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Saved response to {fn}")
            else:
                print("Error Response:", resp.text[:500])
        except Exception as e:
            print("Request Exception:", e)

if __name__ == '__main__':
    main()
