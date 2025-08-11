

from flask import Flask, render_template, request, redirect, url_for, flash
from product_tracker.tracker import track_product
import product_tracker.config as config
import json
import os


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
        # Handle new alias+chatid input
        new_alias = request.form.get('new_alias', '').strip()
        new_chatid = request.form.get('new_chatid', '').strip()
        # If both new alias and chatid are provided and not already present, add to chat_aliases.json
        if new_alias and new_chatid:
            if new_alias not in config.ALIAS_TO_ID and new_chatid not in config.ID_TO_ALIAS:
                # Append to chat_aliases.json
                alias_path = os.path.join(os.path.dirname(config.__file__), 'chat_aliases.json')
                try:
                    with open(alias_path, 'r', encoding='utf-8') as f:
                        aliases = json.load(f)
                except Exception:
                    aliases = []
                aliases.append({'alias': new_alias, 'chat_id': new_chatid})
                with open(alias_path, 'w', encoding='utf-8') as f:
                    json.dump(aliases, f, indent=2)
                # Update config in-memory
                config.ALIAS_TO_ID[new_alias] = new_chatid
                config.ID_TO_ALIAS[new_chatid] = new_alias
                chatid_pick.append(new_chatid)
        # Use selected chat IDs
        phone_or_chat = chatid_pick if chatid_pick else []
        # If no chat IDs, fallback to default
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
        # For display, show aliases if possible
        display_aliases = [config.ID_TO_ALIAS.get(cid, cid) for cid in phone_or_chat]
        return render_template('form.html', target_price=target_price, product_url=product_url, phone_or_chat=display_aliases, active_page='form', config=config)
    return render_template('form.html', target_price=target_price, product_url=product_url, phone_or_chat=phone_or_chat, active_page='form', config=config)

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
            # Accept aliases from the form, convert to chat IDs
            alias_str = request.form.get('edit_chat_aliases', '')
            aliases = [a.strip() for a in alias_str.split(',') if a.strip()]
            import product_tracker.config as config
            chat_ids = [config.ALIAS_TO_ID.get(alias, alias) for alias in aliases]
            schedule_interval = int(request.form['edit_schedule_interval'])
            start_time = request.form.get('edit_start_time', '00:00')
            night_mode = request.form.get('edit_night_mode') == 'true'
            
            item = scheduled_products[idx]
            item['target_price'] = target_price
            item['telegram_chat_ids'] = chat_ids
            item['schedule_interval'] = schedule_interval
            item['start_time'] = start_time
            
            # Handle night mode settings
            if night_mode:
                item['night_mode'] = True
                item['night_end'] = '09:00'  # Default night end time
            else:
                # Remove night mode settings if disabled
                item.pop('night_mode', None)
                item.pop('night_end', None)
            save_scheduled(scheduled_products)
        elif 'delete_idx' in request.form:
            idx = int(request.form['delete_idx'])
            delete_scheduled(idx)
        elif 'cancel_edit' in request.form:
            pass  # Just reload, no edit_idx
    import product_tracker.config as config
    return render_template('tracking.html', scheduled_products=scheduled_products, active_page='table', edit_idx=edit_idx, config=config)

@app.route('/chat', methods=['GET', 'POST'])
def chat_management():
    """Manage chat aliases and IDs"""
    import json
    import os
    from product_tracker.tracker import scheduled_products
    
    # Load current chat aliases
    aliases_file = os.path.join(os.path.dirname(__file__), 'product_tracker', 'chat_aliases.json')
    try:
        with open(aliases_file, 'r') as f:
            chat_aliases = json.load(f)
    except:
        chat_aliases = []
    
    # Calculate usage count for each chat ID
    usage_count = {}
    for product in scheduled_products:
        chat_ids = product.get('telegram_chat_ids', [])
        if isinstance(chat_ids, list):
            for chat_id in chat_ids:
                usage_count[chat_id] = usage_count.get(chat_id, 0) + 1
        elif product.get('telegram_chat_id'):  # Legacy single chat_id
            chat_id = product['telegram_chat_id']
            usage_count[chat_id] = usage_count.get(chat_id, 0) + 1
    
    edit_idx = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            # Add new alias
            new_alias = request.form.get('new_alias', '').strip()
            new_chat_id = request.form.get('new_chat_id', '').strip()
            
            if new_alias and new_chat_id:
                # Check if alias or chat_id already exists
                existing_alias = any(a['alias'].lower() == new_alias.lower() for a in chat_aliases)
                existing_chat_id = any(a['chat_id'] == new_chat_id for a in chat_aliases)
                
                if existing_alias:
                    flash(f'Alias "{new_alias}" already exists!', 'danger')
                elif existing_chat_id:
                    flash(f'Chat ID "{new_chat_id}" already exists!', 'danger')
                else:
                    chat_aliases.append({'alias': new_alias, 'chat_id': new_chat_id})
                    # Save to file
                    with open(aliases_file, 'w') as f:
                        json.dump(chat_aliases, f, indent=2)
                    flash(f'Added new alias "{new_alias}" successfully!', 'success')
                    
                    # Reload config to pick up new aliases
                    import product_tracker.config as config
                    config.load_chat_aliases()
            else:
                flash('Both alias and chat ID are required!', 'danger')
                
        elif action == 'edit':
            edit_idx = int(request.form.get('edit_idx', -1))
            
        elif action == 'save':
            # Save edited alias
            edit_idx_val = int(request.form.get('edit_idx', -1))
            if 0 <= edit_idx_val < len(chat_aliases):
                new_alias = request.form.get('edit_alias', '').strip()
                new_chat_id = request.form.get('edit_chat_id', '').strip()
                
                if new_alias and new_chat_id:
                    # Check for duplicates (excluding current item)
                    existing_alias = any(i != edit_idx_val and a['alias'].lower() == new_alias.lower() 
                                       for i, a in enumerate(chat_aliases))
                    existing_chat_id = any(i != edit_idx_val and a['chat_id'] == new_chat_id 
                                         for i, a in enumerate(chat_aliases))
                    
                    if existing_alias:
                        flash(f'Alias "{new_alias}" already exists!', 'danger')
                        edit_idx = edit_idx_val
                    elif existing_chat_id:
                        flash(f'Chat ID "{new_chat_id}" already exists!', 'danger')
                        edit_idx = edit_idx_val
                    else:
                        old_alias = chat_aliases[edit_idx_val]['alias']
                        chat_aliases[edit_idx_val] = {'alias': new_alias, 'chat_id': new_chat_id}
                        
                        # Save to file
                        with open(aliases_file, 'w') as f:
                            json.dump(chat_aliases, f, indent=2)
                        flash(f'Updated alias "{old_alias}" to "{new_alias}" successfully!', 'success')
                        
                        # Reload config
                        import product_tracker.config as config
                        config.load_chat_aliases()
                else:
                    flash('Both alias and chat ID are required!', 'danger')
                    edit_idx = edit_idx_val
                    
        elif action == 'cancel':
            pass  # Just clear edit mode
            
        elif action == 'delete':
            # Delete alias
            delete_idx = int(request.form.get('delete_idx', -1))
            if 0 <= delete_idx < len(chat_aliases):
                deleted_alias = chat_aliases[delete_idx]['alias']
                del chat_aliases[delete_idx]
                
                # Save to file
                with open(aliases_file, 'w') as f:
                    json.dump(chat_aliases, f, indent=2)
                flash(f'Deleted alias "{deleted_alias}" successfully!', 'success')
                
                # Reload config
                import product_tracker.config as config
                config.load_chat_aliases()
    
    return render_template('chat_management.html', 
                         chat_aliases=chat_aliases,
                         usage_count=usage_count,
                         edit_idx=edit_idx,
                         active_page='chat')

@app.route('/debug')
def debug_dashboard():
    """Main debug dashboard showing all products and debug links"""
    from datetime import datetime
    
    # Count unique chat IDs
    all_chat_ids = set()
    for product in scheduled_products:
        if product.get('telegram_chat_ids'):
            all_chat_ids.update(product['telegram_chat_ids'])
    
    return render_template('debug.html', 
                         products=scheduled_products,
                         total_chat_ids=len(all_chat_ids),
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         active_page='debug')

@app.route('/debug/scheduler')
def debug_scheduler():
    """Debug endpoint to check scheduler status"""
    from product_tracker.scheduler import get_scheduler_status, trigger_job_now
    
    # Get scheduler status
    status = get_scheduler_status()
    
    # Manual trigger if requested
    trigger_idx = request.args.get('trigger')
    trigger_result = None
    if trigger_idx is not None:
        try:
            trigger_result = trigger_job_now(int(trigger_idx))
        except:
            trigger_result = "Invalid trigger index"
    
    # Create HTML response
    html = f"""
    <html>
    <head><title>Scheduler Debug</title></head>
    <body style="font-family: Arial; margin: 20px;">
        <h1>🔍 Scheduler Debug Information</h1>
        
        <h2>Status: {status['status']}</h2>
        <p><strong>Total Jobs:</strong> {status['total_jobs']}</p>
        
        <h2>📋 Current Jobs</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Index</th>
                <th>Job ID</th>
                <th>Interval (hrs)</th>
                <th>Start Time</th>
                <th>Schedule Pattern</th>
                <th>Next Run</th>
                <th>Product URL</th>
                <th>Actions</th>
            </tr>
    """
    
    for job in status['jobs']:
        html += f"""
            <tr>
                <td>{job['idx']}</td>
                <td>{job['job_id']}</td>
                <td>{job.get('interval', 'N/A')}</td>
                <td>{job.get('start_time', 'N/A')}</td>
                <td style="font-family: monospace; font-size: 0.8em;">{job.get('schedule_pattern', 'N/A')}</td>
                <td>{job['next_run']}</td>
                <td style="max-width: 300px; word-break: break-all;">{job['product_url']}</td>
                <td><a href="?trigger={job['idx']}" style="background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Trigger Now</a></td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>📝 Scheduled Products</h2>
        <pre>
    """
    
    for i, product in enumerate(scheduled_products):
        html += f"[{i}] {product}\n"
    
    html += "</pre>"
    
    if trigger_result:
        html += f"""
        <h2>🚀 Manual Trigger Result</h2>
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;">
            {trigger_result}
        </div>
        """
    
    html += """
        <p><a href="/tracking">← Back to Tracking</a></p>
        <p><a href="/debug/scheduler/trigger-all">🚀 Trigger All Jobs Now (Test)</a></p>
    </body>
    </html>
    """
    
    return html

@app.route('/debug/trigger/<int:product_id>')
def debug_trigger_product(product_id):
    """Trigger a specific product job immediately"""
    from product_tracker.scheduler import trigger_job_now
    
    try:
        result = trigger_job_now(product_id)
        return f"""
        <html>
        <head>
            <title>Trigger Result</title>
            <meta http-equiv="refresh" content="3;url=/debug">
        </head>
        <body style="font-family: Arial; margin: 20px; text-align: center;">
            <h2>🚀 Manual Trigger Result</h2>
            <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 20px auto; max-width: 600px;">
                <strong>Product {product_id}:</strong> {result}
            </div>
            <p>Redirecting to debug dashboard in 3 seconds...</p>
            <p><a href="/debug">← Back to Debug Dashboard</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <head>
            <title>Trigger Error</title>
            <meta http-equiv="refresh" content="3;url=/debug">
        </head>
        <body style="font-family: Arial; margin: 20px; text-align: center;">
            <h2>❌ Trigger Error</h2>
            <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin: 20px auto; max-width: 600px;">
                <strong>Product {product_id}:</strong> Error - {str(e)}
            </div>
            <p>Redirecting to debug dashboard in 3 seconds...</p>
            <p><a href="/debug">← Back to Debug Dashboard</a></p>
        </body>
        </html>
        """

@app.route('/debug/scheduler/trigger-all')
def debug_trigger_all():
    """Trigger all scheduled jobs immediately for testing"""
    from product_tracker.scheduler import trigger_job_now
    
    results = []
    success_count = 0
    for i in range(len(scheduled_products)):
        try:
            result = trigger_job_now(i)
            results.append(f"Product {i}: ✅ {result}")
            success_count += 1
        except Exception as e:
            results.append(f"Product {i}: ❌ ERROR - {str(e)}")
    
    html = f"""
    <html>
    <head>
        <title>Trigger All Jobs</title>
        <meta http-equiv="refresh" content="5;url=/debug">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; text-align: center; }}
            .success {{ color: #28a745; }}
            .error {{ color: #dc3545; }}
            .results {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 800px; text-align: left; }}
        </style>
    </head>
    <body>
        <h1>🚀 Triggered All Jobs</h1>
        <div class="success">
            <h2>Successfully triggered {success_count}/{len(scheduled_products)} products</h2>
        </div>
        
        <div class="results">
            <h3>Detailed Results:</h3>
            <ul>
    """
    
    for result in results:
        html += f"<li>{result}</li>"
    
    html += """
            </ul>
        </div>
        <p>Redirecting to debug dashboard in 5 seconds...</p>
        <p><a href="/debug">← Back to Debug Dashboard</a></p>
    </body>
    </html>
    """
    
    return html



if __name__ == '__main__':
    app.run(debug=True)
