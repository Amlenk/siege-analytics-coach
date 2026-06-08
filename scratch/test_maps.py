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
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def test_url(url):
    print(f"\nLoading URL: {url}")
    driver = None
    try:
        driver = create_driver()
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v3-tabs__item"))
        )
        time.sleep(5)
        text = driver.find_element(By.TAG_NAME, "body").text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for House, Plane, Calypso Casino, Stadium
        found_non_ranked = []
        for line in lines:
            if line.lower() in ["house", "presidential plane", "tower", "favela", "hereford base", "calypso casino", "stadium alpha", "stadium bravo"]:
                found_non_ranked.append(line)
        print("Found non-ranked maps on page:", list(set(found_non_ranked)))
        
        # Print total matches sum
        header_idx = -1
        for idx in range(len(lines) - 5):
            if lines[idx] == "Map" and lines[idx+1] == "Matches" and lines[idx+2] == "Win %":
                header_idx = idx
                break
        if header_idx != -1:
            total_matches = 0
            i = header_idx + 10
            while i <= len(lines) - 10:
                try:
                    map_name = lines[i]
                    matches = int(lines[i+1].replace(",", ""))
                    if not map_name.replace(".", "").isdigit() and "%" in lines[i+2]:
                        total_matches += matches
                        i += 10
                        continue
                except:
                    pass
                i += 1
            print("Total matches parsed on page:", total_matches)
    except Exception as e:
        print("Error:", e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    base = "https://r6.tracker.network/r6siege/profile/ubi/WamaiDoingThis/maps"
    test_url(f"{base}?gamemode=pvp_ranked")
    test_url(f"{base}?playlist=ranked")
    test_url(f"{base}")
