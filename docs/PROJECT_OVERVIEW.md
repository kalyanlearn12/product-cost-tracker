# Product Cost Tracker - Project Overview

## Intent
The Product Cost Tracker is a Python web application designed to help users monitor product prices on e-commerce sites, discover available coupon codes, and receive notifications when prices drop below a user-defined target. The app is built to be user-friendly, configurable, and leverages only free, prominent libraries.

## Key Features
- **Track Product Prices:** Monitor the price of a specific product on a given e-commerce URL.
- **Coupon Intelligence:** Automatically extract and display all active coupon codes or offers from the product page to help users get the best deal.
- **Telegram Notifications:** Instantly notify users via Telegram when the product price falls below their target price, including coupon details and the product URL.
- **Configurable Alternate Site Monitoring:** Optionally check alternate e-commerce sites for the same product (configurable by the user).
- **Web Interface:** Simple Flask-based web UI for entering product details and viewing results.
- **Scheduled Checks:** (To be implemented) Automatically check prices and send notifications every 4 hours.

## How It Works
1. **User Input:** The user enters the product URL, target price, and Telegram details via the web interface.
2. **Scraping:** The app uses Requests and BeautifulSoup to fetch the product page, extract the current price, and search for coupon codes or offers.
3. **Notification:** If the price is below the target, a Telegram message is sent to the user with all relevant details.
4. **Web Display:** The web UI displays the current price, all found coupons, the target price, and the product URL.
5. **Scheduling:** (Planned) The app will run the price check automatically every 4 hours and notify users as needed.

## Technology Stack
- **Python 3.x**
- **Flask** (web interface)
- **Requests & BeautifulSoup** (scraping)
- **python-telegram-bot** (Telegram integration)
- **unittest** (testing)

## File Structure
- `app.py`: Flask web application
- `tracker.py`: Core logic for scraping, coupon extraction, and notifications
- `config.py`: Configuration (tokens, chat IDs, alternate sites)
- `test_tracker.py`: Unit tests
- `templates/index.html`: Web UI template
- `requirements.txt`: Python dependencies
- `README.md`: User guide and documentation

## How the Goals Are Achieved
- **Free, Prominent Libraries:** Only widely-used, open-source Python libraries are used.
- **Coupon Intelligence:** Multiple strategies are used to extract coupon codes, including searching for keywords and parsing relevant HTML elements.
- **Configurable Monitoring:** Users can choose to monitor only the provided URL or also check alternate sites (configurable in `config.py`).
- **Scheduling:** (Planned) Will use a scheduler (e.g., APScheduler) to run checks every 4 hours.

---
