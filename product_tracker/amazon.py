from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

CHROMEDRIVER_PATH = 'chromedriver-win64/chromedriver.exe'

def get_amazon_price_selenium(url):
    print(f"[get_amazon_price_selenium] Called with: url={url}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=en-US')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(3)
    price = None
    try:
        selectors = [
            (By.ID, 'priceblock_ourprice'),
            (By.ID, 'priceblock_dealprice'),
            (By.ID, 'priceblock_saleprice'),
            (By.CSS_SELECTOR, 'span.a-price > span.a-offscreen'),
            (By.CSS_SELECTOR, 'span.a-price-whole'),
        ]
        for by, sel in selectors:
            try:
                elem = driver.find_element(by, sel)
                price_text = elem.text.strip().replace(',', '').replace('₹', '').replace('Rs.', '').strip()
                if price_text:
                    price = float(''.join(filter(lambda c: c.isdigit() or c=='.', price_text)))
                    break
            except Exception:
                continue
    finally:
        driver.quit()
    print(f"[get_amazon_price_selenium] Returning: {price}")
    return price
