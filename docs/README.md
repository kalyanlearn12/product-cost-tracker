
# Product Cost Tracker

A professional, user-friendly Python web application to track product prices, discover coupons, and send Telegram notifications when deals are found. Built with Flask, BeautifulSoup, Requests, APScheduler, and python-telegram-bot.

## Features
- Track product prices on e-commerce sites
- Extract and display active coupon codes
- Send Telegram notifications when price drops below target
- Per-product scheduling: run checks every 1 min, 2/4/8/16/24 hours
- Configurable alternate site checking
- Web UI: input on left, results on right
- Persistent scheduled products (survive restarts)
- Delete scheduled products from UI
- Professional, clean codebase

## Quick Start
1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Configure Telegram bot:**
   - Create a bot via [BotFather](https://core.telegram.org/bots#6-botfather)
   - Add your bot token to `config.py` (or use the web UI)
   - Get your chat ID (see User Guide)
3. **Run the app:**
   ```powershell
   & ".venv\Scripts\python.exe" app.py
   ```
4. **Open** [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Testing
Run all tests:
```powershell
& ".venv\Scripts\python.exe" -m unittest test_tracker.py
```

## Documentation
- See `USER_GUIDE.md` for detailed usage
- See `BLOG.md` for the project journey

---
