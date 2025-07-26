import os

# Configuration for the Product Cost Tracker

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7675172119:AAFYBpcPJrvx3HItlJRSg769iUdsMNRe8G8')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '249722033')


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
