"""
Probe the tracker.gg maps page to see what __INITIAL_STATE__ contains.
We need to understand the data structure for seasonal map stats.
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def probe_maps_page(username="Covetous_Demon", platform="ubi"):
    maps_url = f"https://r6.tracker.network/r6siege/profile/{platform}/{username}/maps"
    print(f"Loading: {maps_url}")
    
    driver = create_driver()
    try:
        driver.get(maps_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v3-tabs__item"))
        )
        time.sleep(3)
        
        # Try __INITIAL_STATE__
        state = driver.execute_script("return window.__INITIAL_STATE__;")
        if state:
            # Save full state for inspection
            with open("scratch/maps_initial_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print("Saved __INITIAL_STATE__ to scratch/maps_initial_state.json")
            
            # Check what segments exist
            profile = state.get("stats", {}).get("standardProfiles", [{}])[0]
            segments = profile.get("segments", [])
            print(f"\nFound {len(segments)} segments in maps page state")
            
            # Categorize segments
            for seg in segments:
                seg_type = seg.get("type", "?")
                attrs = seg.get("attributes", {})
                metadata = seg.get("metadata", {})
                stats = seg.get("stats", {})
                stat_keys = list(stats.keys())[:5]
                
                if seg_type == "map":
                    map_name = metadata.get("name", attrs.get("mapName", "?"))
                    season = attrs.get("season")
                    gamemode = attrs.get("gamemode", "?")
                    matches_val = stats.get("matchesPlayed", {}).get("value", "?")
                    wr_val = stats.get("winPercentage", {}).get("displayValue", "?")
                    print(f"  MAP: {map_name} | season={season} | mode={gamemode} | matches={matches_val} | WR={wr_val}")
                elif seg_type == "overview":
                    print(f"  OVERVIEW: season={attrs.get('season')} | mode={attrs.get('gamemode')} | keys={stat_keys}")
                else:
                    print(f"  {seg_type}: attrs={attrs} | keys={stat_keys}")
        else:
            print("No __INITIAL_STATE__ found!")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    probe_maps_page()
