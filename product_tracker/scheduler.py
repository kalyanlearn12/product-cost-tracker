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
    try:
        from product_tracker.tracker import track_product
        print(f"[_run_product_job] Starting tracking for {item['product_url']}")
        result = track_product(
            item['product_url'],
            item['target_price'],
            'telegram',
            item['telegram_chat_ids']
        )
        print(f"[_run_product_job] Tracking completed successfully: {result}")
        return result
    except Exception as e:
        print(f"[_run_product_job] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        # Send error notification
        from product_tracker.notifier import send_telegram_message
        error_msg = f"🚨 Scheduled job failed!\n\nURL: {item['product_url']}\nError: {str(e)}"
        for chat_id in item['telegram_chat_ids']:
            try:
                send_telegram_message(error_msg, chat_id)
            except:
                pass

def _add_job_for_product(idx, item):
    print(f"[_add_job_for_product] Called with: idx={idx}, item={item}")
    global _scheduler, _job_ids
    
    if _scheduler is None:
        print(f"[_add_job_for_product] Scheduler not initialized!")
        return
        
    job_id = f"product_{idx}_{uuid.uuid4().hex[:8]}"
    interval = item.get('schedule_interval', 4)
    start_time = item.get('start_time', '00:00')
    
    hour, minute = 0, 0
    if start_time:
        try:
            hour, minute = map(int, start_time.split(':'))
        except Exception as e:
            print(f"[_add_job_for_product] Invalid start_time format: {start_time}, using 00:00")
            hour, minute = 0, 0
    
    try:
        # Check if this is a night-mode job (runs only during specified night hours)
        night_mode = item.get('night_mode', False)
        night_end = item.get('night_end', '09:00')
        
        if night_mode:
            # Parse night end time
            try:
                night_end_hour, night_end_minute = map(int, night_end.split(':'))
            except:
                night_end_hour, night_end_minute = 9, 0
            
            # Calculate night hours: from start_time to night_end (crossing midnight)
            run_hours = []
            current_hour = hour
            
            # Generate hours from start_time until midnight
            while current_hour < 24:
                run_hours.append(current_hour)
                current_hour += interval
            
            # Generate hours from midnight until night_end
            current_hour = 0
            while current_hour <= night_end_hour:
                if current_hour not in run_hours:  # Avoid duplicates
                    run_hours.append(current_hour)
                current_hour += interval
                if current_hour > night_end_hour:
                    break
            
            # Sort the hours for better readability
            run_hours.sort()
            print(f"[_add_job_for_product] Night mode - Run hours: {run_hours} (from {start_time} to {night_end})")
        else:
            # Calculate all the hours when the job should run based on start_time and interval (regular mode)
            run_hours = []
            current_hour = hour
            
            # Generate all run hours for a 24-hour period
            while len(run_hours) < 24 // interval:
                run_hours.append(current_hour % 24)
                current_hour += interval
                if current_hour >= 24 and current_hour % 24 in run_hours:
                    break
        
        print(f"[_add_job_for_product] Calculated run hours: {run_hours}")
        
        # Use cron scheduling to run at specific hours
        if len(run_hours) == 1:
            # Single run per day
            job = _scheduler.add_job(
                lambda i=item: _run_product_job(i),
                'cron',
                hour=run_hours[0],
                minute=minute,
                id=job_id,
                replace_existing=True,
                coalesce=True,
                max_instances=1
            )
        else:
            # Multiple runs per day - use comma-separated hours
            hours_str = ','.join(map(str, run_hours))
            job = _scheduler.add_job(
                lambda i=item: _run_product_job(i),
                'cron',
                hour=hours_str,
                minute=minute,
                id=job_id,
                replace_existing=True,
                coalesce=True,
                max_instances=1
            )
        
        _job_ids[idx] = job_id
        print(f"[_add_job_for_product] Job {job_id} scheduled successfully with cron pattern")
        print(f"[_add_job_for_product] Run hours: {run_hours} at minute: {minute}")
        print(f"[_add_job_for_product] Next run: {job.next_run_time}")
        
    except Exception as e:
        print(f"[_add_job_for_product] ERROR adding job: {str(e)}")
        import traceback
        traceback.print_exc()

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

def get_scheduler_status():
    """Get current scheduler status and job information"""
    global _scheduler, _job_ids
    
    if _scheduler is None:
        return {"status": "not_initialized", "jobs": []}
    
    status = {
        "status": "running" if _scheduler.running else "stopped",
        "jobs": [],
        "total_jobs": len(_job_ids)
    }
    
    for idx, job_id in _job_ids.items():
        job = _scheduler.get_job(job_id)
        if job:
            # Get schedule pattern info
            trigger_info = str(job.trigger)
            schedule_pattern = "Unknown"
            
            if hasattr(job.trigger, 'fields'):
                try:
                    hour_field = job.trigger.fields[1]  # hour field
                    minute_field = job.trigger.fields[0]  # minute field
                    schedule_pattern = f"Hours: {hour_field}, Minutes: {minute_field}"
                except:
                    schedule_pattern = trigger_info
            
            status["jobs"].append({
                "idx": idx,
                "job_id": job_id,
                "next_run": str(job.next_run_time) if job.next_run_time else "None",
                "schedule_pattern": schedule_pattern,
                "interval": scheduled_products[idx]['schedule_interval'] if idx < len(scheduled_products) else "Unknown",
                "start_time": scheduled_products[idx]['start_time'] if idx < len(scheduled_products) else "Unknown",
                "product_url": scheduled_products[idx]['product_url'] if idx < len(scheduled_products) else "Unknown"
            })
        else:
            status["jobs"].append({
                "idx": idx,
                "job_id": job_id,
                "next_run": "Job not found!",
                "schedule_pattern": "Error",
                "interval": "Unknown",
                "start_time": "Unknown",
                "product_url": "Unknown"
            })
    
    return status

def trigger_job_now(idx):
    """Manually trigger a specific job for testing"""
    global _scheduler, _job_ids
    
    if idx >= len(scheduled_products):
        return f"Invalid index: {idx}"
    
    item = scheduled_products[idx]
    try:
        print(f"[trigger_job_now] Manually triggering job for idx={idx}")
        result = _run_product_job(item)
        return f"Job triggered successfully: {result}"
    except Exception as e:
        return f"Job failed: {str(e)}"

def start_scheduler():
    global _scheduler
    print(f"[start_scheduler] Called with no arguments")
    
    if _scheduler is not None:
        print(f"[start_scheduler] Scheduler already running, skipping...")
        return
        
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.executors.pool import ThreadPoolExecutor
    
    # Configure scheduler with better settings  
    executors = {
        'default': ThreadPoolExecutor(20),
    }
    
    job_defaults = {
        'coalesce': True,  # Combine missed executions
        'max_instances': 3,  # Allow up to 3 instances of same job
        'misfire_grace_time': 60  # Grace period for missed jobs (60 seconds)
    }
    
    _scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
    _scheduler.start()
    
    # Schedule daily summary at 8am
    _scheduler.add_job(
        send_daily_tracking_summary, 
        'cron', 
        hour=8, 
        minute=0, 
        id='daily_summary', 
        replace_existing=True
    )
    
    print(f"[start_scheduler] Scheduler started successfully")
    print(f"[start_scheduler] Returning: None")
    
    atexit.register(lambda: _scheduler.shutdown())
    _refresh_all_jobs()
    
    # Add logging for job events
    import logging
    logging.basicConfig(level=logging.INFO)
    _scheduler._logger.setLevel(logging.DEBUG)

start_scheduler()
