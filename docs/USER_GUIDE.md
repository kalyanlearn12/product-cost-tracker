# Product Cost Tracker - User Guide

## Getting Started

### 1. Prerequisites
- Python 3.8+
- Install dependencies:
  ```powershell
  pip install -r requirements.txt
  ```
- Create a Telegram bot and get your bot token and chat ID (see below).

### 2. Telegram Setup
- [Create a Telegram bot](https://core.telegram.org/bots#6-botfather) via BotFather and get the token.
- To get your chat ID, start a chat with your bot and use a tool like [@userinfobot](https://t.me/userinfobot) or check updates via the Telegram API.
- Add your token and chat ID to `config.py` or enter them in the web UI.

### 3. Running the App
- Start the Flask app:
  ```powershell
  & ".venv\Scripts\python.exe" app.py
  ```
- Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Using the Web Interface
1. Enter the product URL (e.g., a Myntra product page).
2. Enter your target price (the price at which you want to be notified).
3. Enter your Telegram bot token and chat ID.
4. (Optional) Choose whether to check alternate sites (if enabled in config).
5. Click "Track Product".
6. The app will display the current price, all found coupons, your target price, and the product URL.
7. If the price is below your target, you will receive a Telegram notification.

## Example
- **Product URL:** `https://www.myntra.com/watches/tommy+hilfiger/tommy-hilfiger-women-pink-analogue-watch-th1781973/9846981/buy`
- **Target Price:** `5000`
- **Telegram Bot Token:** `bot token`
- **Telegram Chat ID:** `chat id`

## Scheduling (Automatic Checks)
- The app will (after next update) automatically check all tracked products every 4 hours and send notifications if the price drops below the target.
- No manual action is needed once scheduling is enabled.

## Troubleshooting
- **No Telegram message?**
  - Double-check your bot token and chat ID.
  - Make sure your bot is started and you have sent at least one message to it.
  - Check for errors in the app console.
- **Coupons not found?**
  - Some sites use JavaScript to render coupons. The app works best with static HTML coupons.

## Advanced Configuration
- Edit `config.py` to set default Telegram details, alternate sites, or other options.

## Support
- For issues, check the README or open an issue in your project repository.

---
