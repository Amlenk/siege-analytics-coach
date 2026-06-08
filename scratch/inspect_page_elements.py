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
        
        # Look for elements containing "Ranked" or "Casual"
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Ranked') or contains(text(), 'ranked')]")
        print(f"Found {len(elements)} elements containing 'Ranked':")
        for i, el in enumerate(elements[:20]):
            try:
                tag = el.tag_name
                text = el.text.strip()
                parent_class = el.find_element(By.XPATH, "..").get_attribute("class")
                classes = el.get_attribute("class")
                print(f"  [{i}] Tag: <{tag}>, Class: '{classes}', Parent Class: '{parent_class}', Text: '{text}'")
            except Exception as e:
                print(f"  [{i}] Error: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
