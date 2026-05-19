import telebot
from telebot import types
from bot.keyboards import main_menu_keyboard
import bot.services as svc
import logging

logger = logging.getLogger(__name__)

HELP_TEXT = """
🤖 Smart Student Assistant — Commands

📌 General
  /start        — Welcome message
  /help         — Show this list
  /about        — About the bot

📋 Task Manager
  /addtask <text>     — Add a new task
  /tasks              — Show all your tasks
  /done <id>          — Mark task as done
  /delete <id>        — Delete a task

🌤 Weather
  /weather <city>     — Current weather

💬 Motivation
  /quote              — Get a motivational quote

⏰ Reminders
  /remind <msg> <time> — Set a reminder
    Time: 14:30 | 25.12 14:30 | 25.12.2025 14:30

📊 Stats & History
  /stats              — Your usage statistics
  /clearhistory       — Delete message history
""".strip()

ABOUT_TEXT = """
🎓 Smart Student Assistant Bot

I help students stay productive:
• Manage tasks and to-do lists
• Check weather for any city
• Get daily motivational quotes
• Set timed reminders
• Track your activity stats

Built with Python, Django, pyTelegramBotAPI and APScheduler.

👨‍💻 Author: Shalkar Erik
""".strip()


def register_handlers(bot: telebot.TeleBot):

    @bot.message_handler(commands=["start"])
    def cmd_start(message: types.Message):
        name = message.from_user.first_name or "Student"
        text = (
            f"👋 Hello, {name}!\n\n"
            "I'm your Smart Student Assistant.\n"
            "I can help you manage tasks, check weather, set reminders, and more.\n\n"
            "Type /help to see all commands."
        )
        bot.send_message(message.chat.id, text, reply_markup=main_menu_keyboard())
        user = svc.resolve_user(message)
        from assistant.services import save_message
        save_message(user, "/start", text)

    @bot.message_handler(commands=["help"])
    def cmd_help(message: types.Message):
        bot.send_message(message.chat.id, HELP_TEXT)
        user = svc.resolve_user(message)
        from assistant.services import save_message
        save_message(user, "/help", HELP_TEXT)

    @bot.message_handler(commands=["about"])
    def cmd_about(message: types.Message):
        bot.send_message(message.chat.id, ABOUT_TEXT)
        user = svc.resolve_user(message)
        from assistant.services import save_message
        save_message(user, "/about", ABOUT_TEXT)

    @bot.message_handler(commands=["quote"])
    def cmd_quote(message: types.Message):
        bot.send_chat_action(message.chat.id, "typing")
        response = svc.handle_quote(message)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["weather"])
    def cmd_weather(message: types.Message):
        parts = message.text.split(maxsplit=1)
        city = parts[1].strip() if len(parts) > 1 else ""
        bot.send_chat_action(message.chat.id, "typing")
        response = svc.handle_weather(message, city)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["addtask"])
    def cmd_addtask(message: types.Message):
        parts = message.text.split(maxsplit=1)
        title = parts[1].strip() if len(parts) > 1 else ""
        response = svc.handle_add_task(message, title)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["tasks"])
    def cmd_tasks(message: types.Message):
        response = svc.handle_list_tasks(message)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["done"])
    def cmd_done(message: types.Message):
        parts = message.text.split(maxsplit=1)
        task_id = parts[1].strip() if len(parts) > 1 else ""
        response = svc.handle_done_task(message, task_id)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["delete"])
    def cmd_delete(message: types.Message):
        parts = message.text.split(maxsplit=1)
        task_id = parts[1].strip() if len(parts) > 1 else ""
        response = svc.handle_delete_task(message, task_id)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["remind"])
    def cmd_remind(message: types.Message):
        parts = message.text.split(maxsplit=1)
        args = parts[1].strip() if len(parts) > 1 else ""
        response = svc.handle_remind(message, args)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["stats"])
    def cmd_stats(message: types.Message):
        response = svc.handle_stats(message)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(commands=["clearhistory"])
    def cmd_clearhistory(message: types.Message):
        response = svc.handle_clear_history(message)
        bot.send_message(message.chat.id, response)

    # ── Keyboard button aliases ──────────────────────────────────────────────

    @bot.message_handler(func=lambda m: m.text == "📋 My Tasks")
    def kb_tasks(message: types.Message):
        response = svc.handle_list_tasks(message)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(func=lambda m: m.text == "💬 Quote")
    def kb_quote(message: types.Message):
        bot.send_chat_action(message.chat.id, "typing")
        response = svc.handle_quote(message)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(func=lambda m: m.text == "📊 Stats")
    def kb_stats(message: types.Message):
        response = svc.handle_stats(message)
        bot.send_message(message.chat.id, response)

    @bot.message_handler(func=lambda m: m.text == "❓ Help")
    def kb_help(message: types.Message):
        bot.send_message(message.chat.id, HELP_TEXT)

    @bot.message_handler(func=lambda m: m.text == "🌤 Weather")
    def kb_weather_prompt(message: types.Message):
        bot.send_message(message.chat.id, "🌍 Send: /weather <city>\nExample: /weather Almaty")

    @bot.message_handler(func=lambda m: m.text == "➕ Add Task")
    def kb_addtask_prompt(message: types.Message):
        bot.send_message(message.chat.id, "📝 Send: /addtask <task description>\nExample: /addtask Read chapter 5")

    @bot.message_handler(func=lambda m: m.text == "⏰ Reminders")
    def kb_remind_prompt(message: types.Message):
        bot.send_message(
            message.chat.id,
            "⏰ Send: /remind <message> <time>\nExample: /remind Study math 18:30"
        )

    # ── Unknown command fallback ─────────────────────────────────────────────

    @bot.message_handler(func=lambda m: m.text and m.text.startswith("/"))
    def unknown_command(message: types.Message):
        response = (
            f"❓ Unknown command: {message.text.split()[0]}\n\n"
            "Type /help to see all available commands."
        )
        bot.send_message(message.chat.id, response)
        try:
            user = svc.resolve_user(message)
            from assistant.services import save_message
            save_message(user, message.text, response)
        except Exception:
            pass

    # ── Free-text fallback ───────────────────────────────────────────────────

    @bot.message_handler(func=lambda m: True)
    def fallback_text(message: types.Message):
        response = (
            "I'm a command-based bot. Here's what I can do:\n\n"
            + HELP_TEXT
        )
        bot.send_message(message.chat.id, response)
        try:
            user = svc.resolve_user(message)
            from assistant.services import save_message
            save_message(user, message.text, response)
        except Exception:
            pass
