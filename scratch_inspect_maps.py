import json
import requests

BASE_URL = "https://api.r6data.com"
API_KEY = "19aad1d4a7e1f98d88d4b4b5a5227a56e3a5cec775898443fa90695f25c4ed4ad93c0110c75ab98c42477aa5f3af8d172cea056daa7a2df04749bb4304dbfef0"
headers = {"api-key": API_KEY}

def main():
    username = "Amlenk"
    platform = "uplay"
    
    print("\n--- Fetching type = fullStats ---")
    params = {
        "type": "fullStats",
        "nameOnPlatform": username,
        "platformType": platform,
    }
    try:
        resp = requests.get(f"{BASE_URL}/api/stats", params=params, headers=headers, timeout=15)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Keys:", list(data.keys()))
            
            # Save it
            with open("scratch_fullStats.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Saved scratch_fullStats.json")
            
            # Look at "data"
            if "data" in data and isinstance(data["data"], dict):
                d = data["data"]
                print("data keys:", list(d.keys()))
                if "segments" in d:
                    seg = d["segments"]
                    print(f"Segments count: {len(seg)}")
                    types = {}
                    for s in seg:
                        t = s.get("type")
                        types[t] = types.get(t, 0) + 1
                    print("Segment types count:", types)
                    
                    # Print samples of non-overview, non-season segments
                    for s in seg:
                        if s.get("type") not in ["overview", "season", "gamemode"]:
                            print(f"Found non-standard segment type: {s.get('type')}")
                            print(json.dumps(s, indent=2)[:500])
                            break
        else:
            print("Error Response:", resp.text[:200])
    except Exception as e:
        print("Exception:", e)

if __name__ == '__main__':
    main()
