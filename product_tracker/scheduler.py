import uuid
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

def save_scheduled(scheduled_products):
    with open(SCHEDULED_FILE, 'w', encoding='utf-8') as f:
        json.dump(scheduled_products, f, indent=2)

scheduled_products = load_scheduled()

_scheduler = None
_job_ids = {}

def _run_product_job(item):
    from product_tracker.tracker import track_product
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
    chat_ids = telegram_chat_id if isinstance(telegram_chat_id, list) else [telegram_chat_id]
    scheduled_products.append({
        'product_url': product_url,
        'target_price': target_price,
        'telegram_token': telegram_token,
        'telegram_chat_ids': chat_ids,
        'check_alternate_sites': check_alternate_sites,
        'schedule_interval': schedule_interval
    })
    save_scheduled(scheduled_products)
    _refresh_all_jobs()

def delete_scheduled(idx):
    if 0 <= idx < len(scheduled_products):
        _remove_job_for_product(idx)
        scheduled_products.pop(idx)
        save_scheduled(scheduled_products)
        _refresh_all_jobs()

def start_scheduler():
    global _scheduler
    _scheduler = BackgroundScheduler()
    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown())
    _refresh_all_jobs()

start_scheduler()
