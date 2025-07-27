def send_daily_tracking_summary():
    from product_tracker.tracker import scheduled_products
    from product_tracker.notifier import send_telegram_message
    if not scheduled_products:
        return
    msg = '<b>Daily Tracking Summary (8 AM)</b>\n\n'
    for item in scheduled_products:
        url = item.get('product_url', '-')
        price = item.get('target_price', '-')
        interval = item.get('schedule_interval', '-')
        start_time = item.get('start_time', '-')
        chat_ids_raw = item.get('telegram_chat_ids', [])
        chat_ids = []
        for cid in chat_ids_raw:
            if cid == '249722033':
                chat_ids.append('kalyan')
            elif cid == '258922383':
                chat_ids.append('uma')
            else:
                chat_ids.append(cid)
        chat_ids_str = ','.join(chat_ids)
        # Show full URL as plain text (not clickable)
        msg += f"<b>Target:</b> {price} | <b>Start:</b> {start_time}| <b>Freq(h):</b> {interval}  | <b>Messaing to:</b> {chat_ids_str} | {url}\n"
    for chat_id in ['249722033', '258922383']:
        send_telegram_message(msg, chat_id, parse_mode='HTML')
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json
import os

SCHEDULED_FILE = 'scheduled_products.json'

# Load scheduled products from file if exists
def load_scheduled():
    print(f"[load_scheduled] Called with no arguments")
    if os.path.exists(SCHEDULED_FILE):
        with open(SCHEDULED_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"[load_scheduled] Returning: [] (empty file)")
                return []
            result = json.loads(content)
            print(f"[load_scheduled] Returning: {result}")
            return result
    print(f"[load_scheduled] Returning: [] (file not found)")
    return []

def save_scheduled(scheduled_products):
    print(f"[save_scheduled] Called with: scheduled_products={scheduled_products}")
    print(f"[save_scheduled] Returning: None")
    with open(SCHEDULED_FILE, 'w', encoding='utf-8') as f:
        json.dump(scheduled_products, f, indent=2)

scheduled_products = load_scheduled()

_scheduler = None
_job_ids = {}

def _run_product_job(item):
    print(f"[_run_product_job] Called with: item={item}")
    from product_tracker.tracker import track_product
    track_product(
        item['product_url'],
        item['target_price'],
        'telegram',
        item['telegram_chat_ids']
    )

def _add_job_for_product(idx, item):
    print(f"[_add_job_for_product] Called with: idx={idx}, item={item}")
    global _scheduler, _job_ids
    job_id = f"product_{idx}_{uuid.uuid4()}"
    interval = item.get('schedule_interval', 4)
    start_time = item.get('start_time', '00:00')
    hour, minute = 0, 0
    if start_time:
        try:
            hour, minute = map(int, start_time.split(':'))
        except Exception:
            hour, minute = 0, 0
    job = _scheduler.add_job(
        lambda i=item: _run_product_job(i),
        'interval',
        hours=interval,
        next_run_time=None,
        id=job_id,
        replace_existing=True
    )
    # Set next_run_time to the next occurrence of the specified start_time
    from datetime import datetime, timedelta
    now = datetime.now()
    first_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if first_run < now:
        first_run += timedelta(hours=interval)
    job.modify(next_run_time=first_run)
    _job_ids[idx] = job_id

def _remove_job_for_product(idx):
    print(f"[_remove_job_for_product] Called with: idx={idx}")
    global _scheduler, _job_ids
    job_id = _job_ids.get(idx)
    if job_id and _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
    _job_ids.pop(idx, None)

def _refresh_all_jobs():
    print(f"[_refresh_all_jobs] Called with no arguments")
    global _scheduler, _job_ids
    # Remove all jobs
    for job_id in list(_job_ids.values()):
        if _scheduler.get_job(job_id):
            _scheduler.remove_job(job_id)
    _job_ids.clear()
    # Add jobs for all products
    for idx, item in enumerate(scheduled_products):
        _add_job_for_product(idx, item)

def schedule_product_tracking(product_url, target_price, telegram_token, telegram_chat_id, schedule_interval=4):
    print(f"[schedule_product_tracking] Called with: product_url={product_url}, target_price={target_price}, telegram_token={telegram_token}, telegram_chat_id={telegram_chat_id}, schedule_interval={schedule_interval}")
    print(f"[schedule_product_tracking] Returning: None")
    chat_ids = telegram_chat_id if isinstance(telegram_chat_id, list) else [telegram_chat_id]
def schedule_product_tracking(product_url, target_price, telegram_token, telegram_chat_id, schedule_interval=4, start_time='00:00'):
    chat_ids = telegram_chat_id if isinstance(telegram_chat_id, list) else [telegram_chat_id]
    scheduled_products.append({
        'product_url': product_url,
        'target_price': target_price,
        'telegram_token': telegram_token,
        'telegram_chat_ids': chat_ids,
        'schedule_interval': schedule_interval,
        'start_time': start_time
    })
    save_scheduled(scheduled_products)
    _refresh_all_jobs()

def delete_scheduled(idx):
    print(f"[delete_scheduled] Called with: idx={idx}")
    print(f"[delete_scheduled] Returning: None")
    if 0 <= idx < len(scheduled_products):
        _remove_job_for_product(idx)
        scheduled_products.pop(idx)
        save_scheduled(scheduled_products)
        _refresh_all_jobs()

def start_scheduler():
    global _scheduler
    # Schedule daily summary at 8am
    print(f"[start_scheduler] Called with no arguments")
    print(f"[start_scheduler] Returning: None")
    _scheduler = BackgroundScheduler()
    _scheduler.start()
    _scheduler.add_job(send_daily_tracking_summary, 'cron', hour=8 , minute=0 , id='daily_summary', replace_existing=True)
    atexit.register(lambda: _scheduler.shutdown())
    _refresh_all_jobs()

start_scheduler()
