import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = None
_bot_instance = None


def check_and_send_reminders():
    try:
        from assistant.services import get_pending_reminders, mark_reminder_sent
        reminders = get_pending_reminders()
        for reminder in reminders:
            try:
                text = (
                    f"⏰ Reminder!\n\n"
                    f"{reminder.reminder_text}\n\n"
                    f"📅 Scheduled: {reminder.reminder_time.strftime('%d %b %Y at %H:%M')}"
                )
                _bot_instance.send_message(reminder.user.telegram_id, text)
                mark_reminder_sent(reminder)
                logger.info(f"Sent reminder #{reminder.id} to user {reminder.user.telegram_id}")
            except Exception as e:
                logger.error(f"Failed to send reminder #{reminder.id}: {e}")
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {e}")


def start_scheduler(bot):
    global _scheduler, _bot_instance
    _bot_instance = bot

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        check_and_send_reminders,
        trigger=IntervalTrigger(seconds=30),
        id="reminder_check",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — checking reminders every 30 seconds.")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
