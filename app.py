
from flask import Flask, render_template, request, redirect, url_for, flash
from product_tracker.tracker import track_product


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# --- New Multi-Page Navigation ---
@app.route('/')
def about():
    return render_template('about.html', active_page='about')

@app.route('/form', methods=['GET', 'POST'])
def form_page():
    target_price = None
    product_url = None
    phone_or_chat = []
    if request.method == 'POST':
        product_url = request.form['product_url']
        target_price = float(request.form['target_price'])
        notify_method = 'telegram'
        chatid_pick = request.form.getlist('chatid_pick')
        custom_chatids = request.form.get('custom_chatids', '').strip()
        phone_or_chat = chatid_pick if chatid_pick else []
        if custom_chatids:
            phone_or_chat += [cid.strip() for cid in custom_chatids.split(',') if cid.strip()]
        if not phone_or_chat:
            phone_or_chat = ['249722033']
        schedule_tracking = 'schedule_tracking' in request.form
        schedule_interval = int(request.form.get('schedule_interval', 4)) if schedule_tracking else None
        start_time = request.form.get('start_time', '00:00') if schedule_tracking else None
        from product_tracker.tracker import scrape_price_and_coupons, schedule_product_tracking
        result = track_product(product_url, target_price, notify_method, phone_or_chat)
        scheduled_msg = None
        if schedule_tracking:
            schedule_product_tracking(product_url, target_price, None, phone_or_chat, schedule_interval, start_time)
            scheduled_msg = f'Product scheduled for automatic tracking every {schedule_interval} hours starting at {start_time}.'
        if scheduled_msg and result:
            flash(result)
            flash(scheduled_msg)
        elif scheduled_msg:
            flash(scheduled_msg)
        else:
            flash(result)
        return render_template('form.html', target_price=target_price, product_url=product_url, phone_or_chat=phone_or_chat, active_page='form')
    return render_template('form.html', target_price=target_price, product_url=product_url, phone_or_chat=phone_or_chat, active_page='form')

from product_tracker.tracker import scheduled_products

from product_tracker.scheduler import save_scheduled, delete_scheduled
@app.route('/tracking', methods=['GET', 'POST'])
def tracking_table():
    edit_idx = None
    if request.method == 'POST':
        if 'edit_idx' in request.form:
            # Enter edit mode for the given index
            edit_idx = int(request.form['edit_idx'])
        elif 'save_idx' in request.form:
            idx = int(request.form['save_idx'])
            # Update the scheduled product
            target_price = float(request.form['edit_target_price'])
            chat_ids = [cid.strip() for cid in request.form['edit_chat_ids'].split(',') if cid.strip()]
            schedule_interval = int(request.form['edit_schedule_interval'])
            start_time = request.form.get('edit_start_time', '00:00')
            item = scheduled_products[idx]
            item['target_price'] = target_price
            item['telegram_chat_ids'] = chat_ids
            item['schedule_interval'] = schedule_interval
            item['start_time'] = start_time
            save_scheduled(scheduled_products)
        elif 'delete_idx' in request.form:
            idx = int(request.form['delete_idx'])
            delete_scheduled(idx)
        elif 'cancel_edit' in request.form:
            pass  # Just reload, no edit_idx
    return render_template('tracking.html', scheduled_products=scheduled_products, active_page='table', edit_idx=edit_idx)



if __name__ == '__main__':
    app.run(debug=True)
