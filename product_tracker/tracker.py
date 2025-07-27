from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json
import os
SCHEDULED_FILE = 'scheduled_products.json'

# Load scheduled products from file if exists
def load_scheduled():
    if os.path.exists(SCHEDULED_FILE):
        with open(SCHEDULED_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []

def save_scheduled():
    with open(SCHEDULED_FILE, 'w', encoding='utf-8') as f:
        json.dump(scheduled_products, f, indent=2)

scheduled_products = load_scheduled()


# Per-product job management
import uuid
_scheduler = None
_job_ids = {}

def _run_product_job(item):
    track_product(
        item['product_url'],
        item['target_price'],
        'telegram',
        item['telegram_chat_ids'],
        item['check_alternate_sites']
    )

def _add_job_for_product(idx, item):
    global _scheduler, _job_ids
    job_id = f"product_{idx}_{uuid.uuid4()}"
    interval = item.get('schedule_interval', 4)
    if interval == 1:
        job = _scheduler.add_job(
            lambda i=item: _run_product_job(i),
            'interval',
            minutes=1,
            id=job_id,
            replace_existing=True
        )
    else:
        job = _scheduler.add_job(
            lambda i=item: _run_product_job(i),
            'interval',
            hours=interval,
            id=job_id,
            replace_existing=True
        )
    _job_ids[idx] = job_id

def _remove_job_for_product(idx):
    global _scheduler, _job_ids
    job_id = _job_ids.get(idx)
    if job_id and _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
    _job_ids.pop(idx, None)

def _refresh_all_jobs():
    global _scheduler, _job_ids
    # Remove all jobs
    for job_id in list(_job_ids.values()):
        if _scheduler.get_job(job_id):
            _scheduler.remove_job(job_id)
    _job_ids.clear()
    # Add jobs for all products
    for idx, item in enumerate(scheduled_products):
        _add_job_for_product(idx, item)

def schedule_product_tracking(product_url, target_price, telegram_token, telegram_chat_id, check_alternate_sites=False, schedule_interval=4):
    # Accepts telegram_chat_id as a list
    chat_ids = telegram_chat_id if isinstance(telegram_chat_id, list) else [telegram_chat_id]
    scheduled_products.append({
        'product_url': product_url,
        'target_price': target_price,
        'telegram_token': telegram_token,
        'telegram_chat_ids': chat_ids,
        'check_alternate_sites': check_alternate_sites,
        'schedule_interval': schedule_interval
    })
    save_scheduled()
    _refresh_all_jobs()

def delete_scheduled(idx):
    if 0 <= idx < len(scheduled_products):
        _remove_job_for_product(idx)
        scheduled_products.pop(idx)
        save_scheduled()
        _refresh_all_jobs()

def start_scheduler():
    global _scheduler
    _scheduler = BackgroundScheduler()
    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown())
    _refresh_all_jobs()

start_scheduler()
from bs4 import BeautifulSoup
import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CHECK_ALTERNATE_SITES, ALTERNATE_SITES
import telegram

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
        message = f"Price Alert! {title}\nPrice: {best_price}\nTarget Price: {target_price}\nURL: {best_url}"
        if notify_method == 'telegram':
            # phone_or_chat is a list of chat ids
            chat_ids = phone_or_chat if isinstance(phone_or_chat, list) else [phone_or_chat]
            for chat_id in chat_ids:
                send_telegram_message(message, chat_id)
        return f"Notification sent! Best price: {best_price}"
    return f"No deal found. Current best price: {best_price}"

def scrape_price(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string if soup.title else 'Product'
    price = None
    
    import re

    # Myntra-specific price extraction
    price_tag = soup.find('span', {'class': 'pdp-price'})
    if price_tag:
        price = float(''.join(filter(str.isdigit, price_tag.text)))
    else:
        # Try to extract price from meta description (for Myntra)
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            match = re.search(r'Rs\.?\s*([\d,]+)', meta_desc['content'])
            if match:
                price = float(match.group(1).replace(',', ''))

   
    return price, title

def find_alternate_url(site, product_title):
    # Placeholder: In real use, search the site for the product
    return None

def send_telegram_message(message, chat_id):
    import asyncio
    async def send_async():
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)
    try:
        asyncio.run(send_async())
    except RuntimeError:
        # If already in an event loop (e.g., Flask debug), use create_task
        loop = asyncio.get_event_loop()
        loop.create_task(send_async())

