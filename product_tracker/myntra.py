import re

def extract_myntra_price(soup):
    price_tag = soup.find('span', {'class': 'pdp-price'})
    if price_tag:
        try:
            return float(''.join(filter(str.isdigit, price_tag.text)))
        except Exception:
            return None
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        match = re.search(r'Rs\.?\s*([\d,]+)', meta_desc['content'])
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except Exception:
                return None
    return None



def extract_myntra_coupon(url):
    try:
        coupon_info = {}  # Initialize coupon_info as an empty dictionary
        if not url:
            print('Selenium fallback: No URL provided, cannot proceed.')
            driver.quit()
            return coupon_info
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from bs4 import BeautifulSoup
        import time
        CHROMEDRIVER_PATH = 'chromedriver-win64/chromedriver.exe'
        options = Options()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=en-US')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(10)
        html = driver.page_source
        driver.quit()
        soup2 = BeautifulSoup(html, "html.parser")
        offer = soup2.find("div", class_="pdp-offers-offer")
        if offer:
            price_span = offer.find("span", class_="pdp-offers-price")
            if price_span:
                coupon_info["best_price"] = price_span.get_text(strip=True).replace("Rs. ", "").replace("Rs.", "")
            desc_items = offer.find_all("div", class_="pdp-offers-labelMarkup")
            for item in desc_items:
                text = item.get_text(" ", strip=True)
                if "Applicable on:" in text:
                    span = item.find("span")
                    if span:
                        coupon_info["applicable_on"] = span.get_text(strip=True)
                elif "Coupon code:" in text:
                    span = item.find("span", class_="pdp-offers-boldText")
                    if span:
                        coupon_info["coupon_code"] = span.get_text(strip=True)
                elif "Coupon Discount:" in text:
                    span = item.find("span")
                    if span:
                        coupon_info["coupon_discount"] = span.get_text(strip=True)
            return coupon_info
    except Exception as e:
        print(f"Selenium fallback failed: {e}")
    return coupon_info