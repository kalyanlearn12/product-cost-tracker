from flask import Flask, render_template, request, redirect, url_for, flash
from product_tracker.tracker import track_product

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    
    target_price = None
    product_url = None
    phone_or_chat = []
    if request.method == 'POST':
        product_url = request.form['product_url']
        target_price = float(request.form['target_price'])
        notify_method = 'telegram'
        # check_alternates removed
        # Handle multi-select and custom chat ids
        chatid_pick = request.form.getlist('chatid_pick')
        custom_chatids = request.form.get('custom_chatids', '').strip()
        phone_or_chat = chatid_pick if chatid_pick else []
        if custom_chatids:
            # Split by comma, strip whitespace, ignore blanks
            phone_or_chat += [cid.strip() for cid in custom_chatids.split(',') if cid.strip()]
        if not phone_or_chat:
            phone_or_chat = ['249722033']
        schedule_tracking = 'schedule_tracking' in request.form
        schedule_interval = int(request.form.get('schedule_interval', 4)) if schedule_tracking else None

        # Call the tracker logic
        from product_tracker.tracker import scrape_price_and_coupons, schedule_product_tracking
        price, title, coupon = scrape_price_and_coupons(product_url)
        result = track_product(product_url, target_price, notify_method, phone_or_chat)

        scheduled_msg = None
        if schedule_tracking:
            # Only support Telegram for scheduled jobs
            schedule_product_tracking(product_url, target_price, None, phone_or_chat, schedule_interval)
            scheduled_msg = f'Product scheduled for automatic tracking every {schedule_interval} hours.'
        # Show both messages if both exist
        if scheduled_msg and result:
            flash(result)
            flash(scheduled_msg)
        elif scheduled_msg:
            flash(scheduled_msg)
        else:
            flash(result)
        # Always return form values to preserve them
        return render_template('index.html', target_price=target_price, product_url=product_url, phone_or_chat=phone_or_chat)
    # Always return a response for GET requests
    return render_template('index.html',  target_price=target_price, product_url=product_url, phone_or_chat=phone_or_chat)

# Route to view scheduled products
from product_tracker.tracker import scheduled_products
from flask import request, redirect
@app.route('/scheduled', methods=['GET', 'POST'])
def view_scheduled():
    from product_tracker.tracker import scheduled_products, delete_scheduled
    if request.method == 'POST':
        idx = int(request.form['delete_idx'])
        delete_scheduled(idx)
        return redirect(url_for('view_scheduled'))
    return render_template('scheduled.html', scheduled_products=scheduled_products)
    return render_template('index.html',  target_price=target_price, product_url=product_url)

if __name__ == '__main__':
    app.run(debug=True)
