from .scheduler import (
    schedule_product_tracking,
    delete_scheduled,
    scheduled_products
)
from bs4 import BeautifulSoup
import requests

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ALIAS_TO_ID, ID_TO_ALIAS

from .notifier import send_telegram_message
from .amazon import get_amazon_price_selenium
from .myntra import extract_myntra_price, extract_myntra_coupon

def track_product(product_url, target_price, notify_method, phone_or_chat):
    print(f"[track_product] Called with: product_url={product_url}, target_price={target_price}, notify_method={notify_method}, phone_or_chat={phone_or_chat}")
    # Scrape the main product page
    price, title, coupon = scrape_price_and_coupons(product_url)
    best_price = price
    best_url = product_url
    best_coupon = coupon

    # Convert aliases to chat IDs if needed
    chat_ids = []
    for entry in (phone_or_chat if isinstance(phone_or_chat, list) else [phone_or_chat]):
        if entry in ALIAS_TO_ID:
            chat_ids.append(ALIAS_TO_ID[entry])
        else:
            chat_ids.append(entry)

    # For display, show aliases if possible
    display_aliases = [ID_TO_ALIAS.get(cid, cid) for cid in chat_ids]

    if best_price and best_price <= target_price:
        message = (
            f"<b>🟢 Target Price Triggered!</b> <b>{title}</b>\n"
            f"<b>Price:</b> {best_price}\n<b>Target Price:</b> {target_price}\n"
            f"<b>Coupon:</b> {best_coupon}\n"
            f"<a href='{best_url}'>Product Link</a>"
        )
    else:
        message = (
            f"<b>🔴 Target Price Not Triggered Still!</b> <b>{title}</b>\n"
            f"<b>Price:</b> {best_price}\n<b>Target Price:</b> {target_price}\n"
            f"<b>Coupon:</b> {best_coupon}\n"
            f"<a href='{best_url}'>Product Link</a>"
        )

    if notify_method == 'telegram':
        for chat_id in chat_ids:
            send_telegram_message(message, chat_id, parse_mode='HTML')

    # BLINKDEAL logic for Myntra
    if 'myntra.' in product_url and best_coupon:
        if isinstance(best_coupon, dict) and best_coupon.get('coupon_code') and 'BLINKDEAL' in best_coupon.get('coupon_code', '').upper():
            blink_msg = 'BLINK DEAL is active'
            for chat_id in ['249722033', '258922383']:
                send_telegram_message(blink_msg, chat_id, parse_mode='HTML')

    if best_price and best_price <= target_price:
        result = f"Notification sent to: {', '.join(display_aliases)}! Best price: {best_price} \n | Coupon: {best_coupon} "
        print(f"[track_product] Returning: {result}")
        return result
    else:
        result = f"Notification sent to: {', '.join(display_aliases)}! Current best price: {best_price} \n | Coupon: {best_coupon} (Target not met)"
        print(f"[track_product] Returning: {result}")
        return result







def scrape_price_and_coupons(url):
    print(f"[scrape_price_and_coupons] Called with: url={url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string if soup.title else 'Product'
    price = None
    coupon = None

    # Amazon-specific logic
    if 'amazon.' in url:
        price = get_amazon_price_selenium(url)
        if price is not None:
            print(f"[scrape_price_and_coupons] Returning: price={price}, title={title}, coupon=None")
            return price, title, None

    # Myntra-specific logic
    if 'myntra.' in url:
        price = extract_myntra_price(soup)
        if price is not None:
            coupon = extract_myntra_coupon(url)
            print(f"[scrape_price_and_coupons] Returning: price={price}, title={title}, coupon={coupon}")
            return price, title, coupon

    # Generic logic: look for ₹ or Rs in visible text
    price = extract_generic_rupee_price(soup)
    print(f"[scrape_price_and_coupons] Returning: price={price}, title={title}, coupon=None")
    return price, title, None




def extract_generic_rupee_price(soup):
    print(f"[extract_generic_rupee_price] Called with: soup=<BeautifulSoup object>")
    import re
    # Look for ₹ or Rs followed by numbers in visible text
    text = soup.get_text(separator=' ', strip=True)
    match = re.search(r'(?:₹|Rs\.?)[ ]*([\d,]+)', text)
    if match:
        try:
            result = float(match.group(1).replace(',', ''))
            print(f"[extract_generic_rupee_price] Returning: {result}")
            return result
        except Exception:
            print(f"[extract_generic_rupee_price] Returning: None (exception)")
            return None
    print(f"[extract_generic_rupee_price] Returning: None (no match)")
    return None
