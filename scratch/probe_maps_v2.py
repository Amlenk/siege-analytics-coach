"""
Probe tracker.gg maps page with and without season filter to compare actual page text.
Also try the TRN API endpoint for map segments.
"""
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_env():
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
    return env_vars

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# ---- Method 1: Try TRN API directly for map segments ----
def try_trn_api(username, platform, api_key):
    """Try the tracker.gg v3 API to see if it returns map data segments."""
    print("\n--- TRN API Probe ---")
    
    # Try the segments endpoint for maps
    headers = {
        "TRN-Api-Key": api_key,
        "Accept": "application/json"
    }
    
    # Standard overview segments  
    url = f"https://public-ubiservices.ubi.com/v1/spaces"
    
    # Try TRN internal API that the maps page might use
    api_urls = [
        f"https://api.tracker.gg/api/v2/r6siege/standard/profile/{platform}/{username}/segments/map",
        f"https://api.tracker.gg/api/v2/r6siege/standard/profile/{platform}/{username}/segments/map?season=41",
        f"https://api.tracker.gg/api/v2/r6siege/standard/profile/{platform}/{username}/segments/map?season=41&gamemode=pvp_ranked",
    ]
    
    for url in api_urls:
        print(f"\n  Trying: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                with open(f"scratch/trn_api_maps_response_{url.split('?')[-1].replace('&','_').replace('=','_') if '?' in url else 'default'}.json", "w") as f:
                    json.dump(data, f, indent=2)
                
                # Check what we got
                if isinstance(data, dict) and "data" in data:
                    segments = data["data"]
                    if isinstance(segments, list):
                        print(f"  Got {len(segments)} map segments!")
                        for seg in segments[:5]:
                            attrs = seg.get("attributes", {})
                            meta = seg.get("metadata", {})
                            stats = seg.get("stats", {})
                            map_name = meta.get("name", attrs.get("mapName", "?"))
                            matches = stats.get("matchesPlayed", {}).get("value", "?")
                            wr = stats.get("winPercentage", {}).get("displayValue", "?")
                            print(f"    {map_name}: {matches} matches, WR: {wr}")
                        if len(segments) > 5:
                            print(f"    ... and {len(segments)-5} more")
            elif resp.status_code == 403:
                print(f"  Forbidden (API key may not be valid for this endpoint)")
            else:
                print(f"  Response: {resp.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")

# ---- Method 2: Selenium network interception ----
def probe_with_selenium(username, platform):
    """Use Selenium to load the ranked Y11S1 maps page and capture the page text + network calls."""
    print("\n--- Selenium Probe (Ranked Y11S1) ---")
    
    # Try the seasonal ranked maps URL
    maps_url = f"https://r6.tracker.network/r6siege/profile/{platform}/{username}/maps?season=41&gamemode=pvp_ranked"
    print(f"Loading: {maps_url}")
    
    driver = create_driver()
    try:
        # Enable performance logging to capture network requests
        driver.get(maps_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v3-tabs__item"))
        )
        time.sleep(5)
        
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Save full page text
        with open(f"scratch/maps_page_text_seasonal_ranked.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        
        # Parse just the first few lines around "Map" header
        lines = [l.strip() for l in body_text.split('\n') if l.strip()]
        for idx in range(len(lines)-5):
            if lines[idx] == "Map" and lines[idx+1] == "Matches":
                print(f"\n  Found Map table header at line {idx}")
                # Print next 30 lines
                for i in range(idx, min(idx+40, len(lines))):
                    print(f"    [{i}] {lines[i]}")
                break
        else:
            print("  No 'Map' / 'Matches' header found in page text")
            # Show first 50 lines
            for i, l in enumerate(lines[:50]):
                print(f"    [{i}] {l}")
        
    finally:
        driver.quit()

    # Now try lifetime maps (no season filter)
    print(f"\n--- Selenium Probe (Lifetime All) ---")
    maps_url_lt = f"https://r6.tracker.network/r6siege/profile/{platform}/{username}/maps"
    print(f"Loading: {maps_url_lt}")
    
    driver = create_driver()
    try:
        driver.get(maps_url_lt)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v3-tabs__item"))
        )
        time.sleep(5)
        
        body_text = driver.find_element(By.TAG_NAME, "body").text
        with open(f"scratch/maps_page_text_lifetime.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        
        lines = [l.strip() for l in body_text.split('\n') if l.strip()]
        for idx in range(len(lines)-5):
            if lines[idx] == "Map" and lines[idx+1] == "Matches":
                print(f"\n  Found Map table header at line {idx}")
                for i in range(idx, min(idx+40, len(lines))):
                    print(f"    [{i}] {lines[i]}")
                break
        else:
            print("  No 'Map' / 'Matches' header found in page text")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    env = load_env()
    api_key = env.get("TRACKER_GG_API_KEY", "")
    
    # Test with Covetous_Demon
    username = "Covetous_Demon"
    platform = "ubi"
    
    try_trn_api(username, platform, api_key)
    probe_with_selenium(username, platform)
