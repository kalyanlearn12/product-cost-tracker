import telegram
from product_tracker.config import TELEGRAM_BOT_TOKEN

import asyncio

def send_telegram_message(message, chat_id, parse_mode=None):
    async def send_async():
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)
    try:
        asyncio.run(send_async())
    except RuntimeError:
        # If already in an event loop (e.g., Flask debug), use create_task
        loop = asyncio.get_event_loop()
        loop.create_task(send_async())
