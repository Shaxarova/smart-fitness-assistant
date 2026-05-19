import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.utils import timezone
from .models import TelegramUser, Task, Message, Reminder, WeatherHistory


def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> TelegramUser:
    user, _ = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"username": username, "first_name": first_name},
    )
    if not _:
        changed = False
        if username and user.username != username:
            user.username = username
            changed = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if changed:
            user.save()
    return user


def save_message(user: TelegramUser, user_text: str, bot_text: str) -> Message:
    return Message.objects.create(user=user, user_message=user_text, bot_response=bot_text)


def create_task(user: TelegramUser, title: str) -> Task:
    return Task.objects.create(user=user, title=title)


def get_user_tasks(user: TelegramUser):
    return Task.objects.filter(user=user).order_by("-created_at")


def get_pending_tasks(user: TelegramUser):
    return Task.objects.filter(user=user, status=Task.STATUS_PENDING).order_by("-created_at")


def mark_task_done(user: TelegramUser, task_id: int):
    try:
        task = Task.objects.get(id=task_id, user=user)
        task.status = Task.STATUS_DONE
        task.completed_at = timezone.now()
        task.save()
        return task
    except Task.DoesNotExist:
        return None


def delete_task(user: TelegramUser, task_id: int) -> bool:
    try:
        task = Task.objects.get(id=task_id, user=user)
        task.delete()
        return True
    except Task.DoesNotExist:
        return False


def create_reminder(user: TelegramUser, text: str, remind_time) -> Reminder:
    return Reminder.objects.create(user=user, reminder_text=text, reminder_time=remind_time)


def get_pending_reminders():
    return Reminder.objects.filter(is_sent=False, reminder_time__lte=timezone.now())


def mark_reminder_sent(reminder: Reminder):
    reminder.is_sent = True
    reminder.save()


def save_weather(user: TelegramUser, city: str, temperature: float,
                 condition: str, humidity: int, wind_speed: float) -> WeatherHistory:
    return WeatherHistory.objects.create(
        user=user,
        city=city,
        temperature=temperature,
        condition=condition,
        humidity=humidity,
        wind_speed=wind_speed,
    )


def get_user_stats(user: TelegramUser) -> dict:
    total_messages = Message.objects.filter(user=user).count()
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status=Task.STATUS_DONE).count()
    pending_tasks = Task.objects.filter(user=user, status=Task.STATUS_PENDING).count()
    reminders_count = Reminder.objects.filter(user=user).count()
    return {
        "total_messages": total_messages,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "reminders_count": reminders_count,
    }


def clear_user_history(user: TelegramUser) -> int:
    count, _ = Message.objects.filter(user=user).delete()
    return count
