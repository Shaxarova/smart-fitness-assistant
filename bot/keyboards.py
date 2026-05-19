import telebot
from telebot import types


def main_menu_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📋 My Tasks"),
        types.KeyboardButton("➕ Add Task"),
        types.KeyboardButton("🌤 Weather"),
        types.KeyboardButton("💬 Quote"),
        types.KeyboardButton("📊 Stats"),
        types.KeyboardButton("⏰ Reminders"),
        types.KeyboardButton("❓ Help"),
    )
    return markup


def remove_keyboard() -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()
