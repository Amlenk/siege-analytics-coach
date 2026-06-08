import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    
    print("[*] Launching headless browser...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    url = "https://r6.tracker.network/r6siege/profile/uplay/WamaiDoingThis/maps"
    print(f"[*] Navigating to: {url}")
    driver.get(url)
    
    try:
        # Wait for tabs to load
        print("[*] Waiting for tabs to appear...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v3-tabs__item"))
        )
        
        # Print all tabs
        tabs = driver.find_elements(By.CLASS_NAME, "v3-tabs__item")
        print(f"[*] Found {len(tabs)} tabs:")
        ranked_tab = None
        for t in tabs:
            text = t.text.strip()
            print(f"  - Tab text: '{text}'")
            if "ranked" in text.lower():
                ranked_tab = t
        
        if ranked_tab:
            print(f"[*] Clicking on tab: '{ranked_tab.text}'")
            driver.execute_script("arguments[0].click();", ranked_tab)
            print("[*] Clicked! Waiting 5 seconds for table to update...")
            time.sleep(5)
            
            # Print body text lines to verify if Hereford, House, etc are gone
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            
            # Find the Map header
            header_idx = -1
            for idx, line in enumerate(lines):
                if idx < len(lines) - 2 and lines[idx] == "Map" and lines[idx+1] == "Matches" and lines[idx+2] == "Win %":
                    header_idx = idx
                    break
            
            if header_idx != -1:
                print(f"[*] Found map table header at line {header_idx}")
                # Print next 30 lines
                print("[*] Printing next 50 lines of parsed map data:")
                for line in lines[header_idx:header_idx+50]:
                    print("  ", line)
            else:
                print("[!] Could not find map table header in text!")
        else:
            print("[!] Ranked tab not found!")
            
    except Exception as e:
        print(f"[!] Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
