from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, Task, Message, Reminder, WeatherHistory


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "first_name", "username", "created_at", "task_count", "message_count")
    search_fields = ("telegram_id", "username", "first_name")
    readonly_fields = ("telegram_id", "username", "first_name", "created_at")
    ordering = ("-created_at",)

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = "Tasks"

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_title", "colored_status", "status", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "user__username", "user__first_name")
    readonly_fields = ("created_at",)
    list_editable = ("status",)
    ordering = ("-created_at",)

    def short_title(self, obj):
        return obj.title[:60] + "..." if len(obj.title) > 60 else obj.title
    short_title.short_description = "Title"

    def colored_status(self, obj):
        color = "#28a745" if obj.status == Task.STATUS_DONE else "#ffc107"
        label = "Done" if obj.status == Task.STATUS_DONE else "Pending"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    colored_status.short_description = "Status"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_user_msg", "short_bot_response", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("user_message", "bot_response", "user__username")
    readonly_fields = ("user", "user_message", "bot_response", "timestamp")
    ordering = ("-timestamp",)

    def short_user_msg(self, obj):
        return obj.user_message[:60] + "..." if len(obj.user_message) > 60 else obj.user_message
    short_user_msg.short_description = "User Message"

    def short_bot_response(self, obj):
        return obj.bot_response[:60] + "..." if len(obj.bot_response) > 60 else obj.bot_response
    short_bot_response.short_description = "Bot Response"


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_text", "reminder_time", "sent_badge", "created_at")
    list_filter = ("is_sent", "reminder_time")
    search_fields = ("reminder_text", "user__username")
    readonly_fields = ("created_at",)
    ordering = ("reminder_time",)

    def short_text(self, obj):
        return obj.reminder_text[:60] + "..." if len(obj.reminder_text) > 60 else obj.reminder_text
    short_text.short_description = "Reminder"

    def sent_badge(self, obj):
        if obj.is_sent:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Sent</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">⏳ Pending</span>')
    sent_badge.short_description = "Status"


@admin.register(WeatherHistory)
class WeatherHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "temperature_display", "condition", "humidity", "wind_speed", "request_time")
    list_filter = ("city", "request_time")
    search_fields = ("city", "user__username")
    readonly_fields = ("user", "city", "temperature", "condition", "humidity", "wind_speed", "request_time")
    ordering = ("-request_time",)

    def temperature_display(self, obj):
        return f"{obj.temperature}°C"
    temperature_display.short_description = "Temperature"


admin.site.site_header = "Smart Student Assistant — Admin Panel"
admin.site.site_title = "Student Bot Admin"
admin.site.index_title = "Dashboard"
