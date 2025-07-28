import os

# Configuration for the Product Cost Tracker


# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7675172119:AAFYBpcPJrvx3HItlJRSg769iUdsMNRe8G8')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '249722033')

# Load chat aliases from JSON file
import json
CHAT_ALIASES_FILE = os.path.join(os.path.dirname(__file__), 'chat_aliases.json')
CHAT_ALIASES = []
ALIAS_TO_ID = {}
ID_TO_ALIAS = {}
try:
    with open(CHAT_ALIASES_FILE, 'r', encoding='utf-8') as f:
        CHAT_ALIASES = json.load(f)
        for entry in CHAT_ALIASES:
            alias = entry['alias']
            chat_id = entry['chat_id']
            ALIAS_TO_ID[alias] = chat_id
            ID_TO_ALIAS[chat_id] = alias
except Exception as e:
    print(f"[WARN] Could not load chat_aliases.json: {e}")


# Whether to check alternate sites for best price
CHECK_ALTERNATE_SITES = True

# List of alternate sites to check (to be implemented)
ALTERNATE_SITES = [
    'https://www.amazon.in',
    'https://www.flipkart.com',
    # Add more as needed
]

# Scheduler settings
SCHEDULE_TIME = '09:00'  # 24-hour format, time to run daily
