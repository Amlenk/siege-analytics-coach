import os
import json
import requests

def load_env():
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

def main():
    env = load_env()
    api_key = env.get('R6DATA_API_KEY', '')
    if not api_key:
        print("API key missing")
        return
        
    headers = {"api-key": api_key}
    url = "https://api.r6data.com/api/stats"
    params = {
        "type": "stats",
        "nameOnPlatform": "Amlenk",
        "platformType": "uplay",
        "platform_families": "pc"
    }
    
    resp = requests.get(url, headers=headers, params=params)
    print("Status code:", resp.status_code)
    try:
        data = resp.json()
        print("Response structure keys:", list(data.keys()) if isinstance(data, dict) else type(data))
        # Save to raw for offline viewing
        with open("scratch/stats_raw_amlenk.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("Saved raw response to scratch/stats_raw_amlenk.json")
    except Exception as e:
        print("Error:", e)
        print("Text response first 500 chars:", resp.text[:500])

if __name__ == '__main__':
    main()
