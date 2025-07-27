import re

def extract_myntra_price(soup):
    print(f"[extract_myntra_price] Called with: soup=<BeautifulSoup object>")
    price_tag = soup.find('span', {'class': 'pdp-price'})
    if price_tag:
        try:
            result = float(''.join(filter(str.isdigit, price_tag.text)))
            print(f"[extract_myntra_price] Returning: {result}")
            return result
        except Exception:
            print(f"[extract_myntra_price] Returning: None (exception)")
            return None
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        match = re.search(r'Rs\.?\s*([\d,]+)', meta_desc['content'])
        if match:
            try:
                result = float(match.group(1).replace(',', ''))
                print(f"[extract_myntra_price] Returning: {result}")
                return result
            except Exception:
                print(f"[extract_myntra_price] Returning: None (exception)")
                return None
    print(f"[extract_myntra_price] Returning: None (no price found)")
    return None



def extract_myntra_coupon(url):
    print(f"[extract_myntra_coupon] Called with: url={url}")
    try:
        coupon_info = {}  # Initialize coupon_info as an empty dictionary
        if not url:
            print('Selenium fallback: No URL provided, cannot proceed.')
            print(f"[extract_myntra_coupon] Returning: {coupon_info}")
            return coupon_info
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from bs4 import BeautifulSoup
        import time
        print(f"1")
        
        CHROMEDRIVER_PATH = 'chromedriver-win64/chromedriver.exe'
        options = Options()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=en-US')
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        print(f"2")
        driver.get(url)
        print(f"3")
        time.sleep(3)
        html = driver.page_source
        print(f"4")
        driver.quit()
        print(f"5")
        soup2 = BeautifulSoup(html, "html.parser")
        print(f"6")
        offer = soup2.find("div", class_="pdp-offers-offer")
        print(f"7")
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
            print(f"[extract_myntra_coupon] Returning: {coupon_info}")
            return coupon_info
        print(f"[extract_myntra_coupon] Returning: {coupon_info}")
        return coupon_info
    except Exception as e:
        print(f"Selenium fallback failed: {e}")
        print(f"[extract_myntra_coupon] Returning: {coupon_info}")
        return coupon_info