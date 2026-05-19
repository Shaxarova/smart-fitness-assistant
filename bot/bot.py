# Smart Student Assistant Telegram Bot
# Author: Shalkar Erik

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import telebot
from django.conf import settings
from bot.handlers import register_handlers
from bot.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN is not set. Add it to your .env file and restart.")
        sys.exit(1)

    bot = telebot.TeleBot(token, parse_mode=None)
    register_handlers(bot)
    start_scheduler(bot)

    logger.info("Bot is starting in polling mode...")
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
    finally:
        stop_scheduler()


if __name__ == "__main__":
    main()
