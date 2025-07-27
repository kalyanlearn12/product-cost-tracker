from .scheduler import (
    schedule_product_tracking,
    delete_scheduled,
    scheduled_products
)
from bs4 import BeautifulSoup
import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CHECK_ALTERNATE_SITES, ALTERNATE_SITES
from .notifier import send_telegram_message

def track_product(product_url, target_price, notify_method, phone_or_chat, check_alternates):
    # Scrape the main product page
    price, title = scrape_price(product_url)
    best_price = price
    best_url = product_url
    
    
    # Optionally check alternate sites
    if check_alternates and CHECK_ALTERNATE_SITES:
        for site in ALTERNATE_SITES:
            alt_url = find_alternate_url(site, title)
            if alt_url:
                alt_price, _ = scrape_price(alt_url)
                if alt_price and alt_price < best_price:
                    best_price = alt_price
                    best_url = alt_url
                    
    
    # If price is at or below target, notify
    if best_price and best_price <= target_price:
        message = (
            f"<b>🟢 Target Price Triggered!</b> <b>{title}</b>\n"
            f"<b>Price:</b> {best_price}\n<b>Target Price:</b> {target_price}\n"
            f"<a href='{best_url}'>Product Link</a>"
        )
    else:
        message = (
            f"<b>🔴 Target Price Not Triggered Still!</b> <b>{title}</b>\n"
            f"<b>Price:</b> {best_price}\n<b>Target Price:</b> {target_price}\n"
            f"<a href='{best_url}'>Product Link</a>"
        )

    if notify_method == 'telegram':
        # phone_or_chat is a list of chat ids
        chat_ids = phone_or_chat if isinstance(phone_or_chat, list) else [phone_or_chat]
        for chat_id in chat_ids:
            send_telegram_message(message, chat_id, parse_mode='HTML')


    if best_price and best_price <= target_price:
        return f"Notification sent! Best price: {best_price}"
    else:
        return f"No deal found. Current best price: {best_price}"

def scrape_price(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string if soup.title else 'Product'
    price = None
    
    import re

    # Myntra-specific logic
    price = extract_myntra_price(soup)
    if price is not None:
        return price, title

    # Generic logic: look for ₹ or Rs in visible text
    price = extract_generic_rupee_price(soup)
    return price, title

def extract_myntra_price(soup):
    import re
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

def extract_generic_rupee_price(soup):
    import re
    # Look for ₹ or Rs followed by numbers in visible text
    text = soup.get_text(separator=' ', strip=True)
    match = re.search(r'(?:₹|Rs\.?)[ ]*([\d,]+)', text)
    if match:
        try:
            return float(match.group(1).replace(',', ''))
        except Exception:
            return None
    return None

   
    return price, title

def find_alternate_url(site, product_title):
    # Placeholder: In real use, search the site for the product
    return None

    # send_telegram_message is now imported from notifier.py

