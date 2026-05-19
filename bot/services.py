"""Bot-layer service helpers — thin wrappers that call assistant.services."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from assistant.services import (
    get_or_create_user,
    save_message,
    create_task,
    get_user_tasks,
    get_pending_tasks,
    mark_task_done,
    delete_task,
    create_reminder,
    get_user_stats,
    clear_user_history,
    save_weather,
)
from assistant.utils import get_motivational_quote, get_weather, parse_reminder_time
from assistant.models import TelegramUser, Task


def resolve_user(message) -> TelegramUser:
    return get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )


def handle_quote(message) -> str:
    user = resolve_user(message)
    response = get_motivational_quote()
    save_message(user, "/quote", response)
    return response


def handle_weather(message, city: str) -> str:
    user = resolve_user(message)
    if not city:
        response = "Please specify a city: /weather Almaty"
        save_message(user, message.text, response)
        return response

    data = get_weather(city)
    if data.get("error"):
        response = f"❌ {data['error']}"
    else:
        response = (
            f"🌍 Weather in {data['city']}, {data['country']}\n"
            f"{'─' * 28}\n"
            f"🌡  Temperature:  {data['temperature']}°C (feels like {data['feels_like']}°C)\n"
            f"☁️  Condition:    {data['condition']}\n"
            f"💧 Humidity:     {data['humidity']}%\n"
            f"💨 Wind speed:   {data['wind_speed']} m/s"
        )
        save_weather(
            user=user,
            city=data["city"],
            temperature=data["temperature"],
            condition=data["condition"],
            humidity=data["humidity"],
            wind_speed=data["wind_speed"],
        )
    save_message(user, message.text, response)
    return response


def handle_add_task(message, title: str) -> str:
    user = resolve_user(message)
    if not title:
        response = "Please specify a task: /addtask Buy textbooks"
        save_message(user, message.text, response)
        return response
    task = create_task(user, title)
    response = f"✅ Task #{task.id} added:\n\"{title}\""
    save_message(user, message.text, response)
    return response


def handle_list_tasks(message) -> str:
    user = resolve_user(message)
    tasks = get_user_tasks(user)
    if not tasks.exists():
        response = "📭 You have no tasks yet.\nUse /addtask <description> to create one."
    else:
        lines = ["📋 Your tasks:\n"]
        for task in tasks:
            icon = "✅" if task.status == Task.STATUS_DONE else "🔲"
            lines.append(f"{icon} #{task.id} {task.title}")
        response = "\n".join(lines)
    save_message(user, "/tasks", response)
    return response


def handle_done_task(message, task_id_str: str) -> str:
    user = resolve_user(message)
    try:
        task_id = int(task_id_str)
    except (ValueError, TypeError):
        response = "❌ Invalid task ID. Usage: /done 3"
        save_message(user, message.text, response)
        return response

    task = mark_task_done(user, task_id)
    if task:
        response = f"✅ Task #{task.id} marked as done!\n\"{task.title}\""
    else:
        response = f"❌ Task #{task_id} not found. Use /tasks to see your tasks."
    save_message(user, message.text, response)
    return response


def handle_delete_task(message, task_id_str: str) -> str:
    user = resolve_user(message)
    try:
        task_id = int(task_id_str)
    except (ValueError, TypeError):
        response = "❌ Invalid task ID. Usage: /delete 3"
        save_message(user, message.text, response)
        return response

    success = delete_task(user, task_id)
    if success:
        response = f"🗑 Task #{task_id} deleted."
    else:
        response = f"❌ Task #{task_id} not found."
    save_message(user, message.text, response)
    return response


def handle_remind(message, args: str) -> str:
    user = resolve_user(message)
    if not args:
        response = (
            "Usage: /remind <message> <time>\n\n"
            "Time formats:\n"
            "  HH:MM         → today at HH:MM\n"
            "  DD.MM HH:MM   → specific date\n"
            "  DD.MM.YYYY HH:MM\n\n"
            "Example: /remind Study for exam 18:30"
        )
        save_message(user, message.text, response)
        return response

    parts = args.rsplit(" ", 1)
    if len(parts) < 2:
        parts = args.rsplit(" ", 2)
        if len(parts) >= 2:
            time_part = parts[-2] + " " + parts[-1]
            text_part = " ".join(parts[:-2])
        else:
            response = "❌ Could not parse time. Example: /remind Study for exam 18:30"
            save_message(user, message.text, response)
            return response
    else:
        text_part = parts[0]
        time_part = parts[1]

    remind_time = parse_reminder_time(time_part)
    if remind_time is None:
        parts2 = args.rsplit(" ", 2)
        if len(parts2) >= 3:
            time_part = parts2[-2] + " " + parts2[-1]
            text_part = " ".join(parts2[:-2])
            remind_time = parse_reminder_time(time_part)

    if remind_time is None:
        response = (
            "❌ Could not parse time.\n\n"
            "Supported formats:\n"
            "  /remind Buy milk 14:30\n"
            "  /remind Call mom 25.12 10:00\n"
            "  /remind Submit project 31.12.2025 23:59"
        )
        save_message(user, message.text, response)
        return response

    from django.utils import timezone
    if remind_time <= timezone.now():
        response = "❌ Reminder time must be in the future."
        save_message(user, message.text, response)
        return response

    create_reminder(user, text_part.strip() or args, remind_time)
    formatted = remind_time.strftime("%d %b %Y at %H:%M")
    response = f"⏰ Reminder set!\n\n\"{text_part.strip() or args}\"\n📅 {formatted}"
    save_message(user, message.text, response)
    return response


def handle_stats(message) -> str:
    user = resolve_user(message)
    stats = get_user_stats(user)
    response = (
        f"📊 Your statistics\n"
        f"{'─' * 28}\n"
        f"💬 Total messages:   {stats['total_messages']}\n"
        f"📋 Total tasks:      {stats['total_tasks']}\n"
        f"✅ Completed tasks:  {stats['completed_tasks']}\n"
        f"🔲 Pending tasks:    {stats['pending_tasks']}\n"
        f"⏰ Reminders set:    {stats['reminders_count']}"
    )
    save_message(user, "/stats", response)
    return response


def handle_clear_history(message) -> str:
    user = resolve_user(message)
    count = clear_user_history(user)
    response = f"🧹 Deleted {count} message(s) from your history."
    save_message(user, "/clearhistory", response)
    return response
