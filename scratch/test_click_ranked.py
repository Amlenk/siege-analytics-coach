import time
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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    url = "https://r6.tracker.network/r6siege/profile/uplay/WamaiDoingThis/maps"
    driver.get(url)
    
    try:
        # Wait a bit for the page to load fully
        time.sleep(8)
        
        # Find the Ranked button/span
        spans = driver.find_elements(By.XPATH, "//span[text()='Ranked']")
        if spans:
            ranked_span = spans[0]
            print(f"[*] Found 'Ranked' span: tag={ranked_span.tag_name}, text='{ranked_span.text}'")
            # Let's get parent button
            parent = ranked_span.find_element(By.XPATH, "..")
            print(f"[*] Parent element tag={parent.tag_name}, class='{parent.get_attribute('class')}'")
            
            # Click parent or span
            print("[*] Clicking Ranked button...")
            driver.execute_script("arguments[0].click();", parent)
            time.sleep(5)
            
            # Extract maps
            body_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            
            header_idx = -1
            for idx, line in enumerate(lines):
                if idx < len(lines) - 2 and lines[idx] == "Map" and lines[idx+1] == "Matches" and lines[idx+2] == "Win %":
                    header_idx = idx
                    break
            
            if header_idx != -1:
                print(f"[*] Found map table header at line {header_idx}")
                # Print lines until we hit another section or run out of map lines
                for line in lines[header_idx:header_idx+60]:
                    print("  ", line)
            else:
                print("[!] Map header not found in body text after click!")
        else:
            print("[!] Ranked span not found!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
