from django.db import models


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name or 'Unknown'} (@{self.username or 'no_username'}) [{self.telegram_id}]"


class Task(models.Model):
    STATUS_PENDING = "pending"
    STATUS_DONE = "done"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_DONE, "Done"),
    ]

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="tasks")
    title = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.id}] {self.title[:50]} — {self.status}"


class Message(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="messages")
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Reminder(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="reminders")
    reminder_text = models.TextField()
    reminder_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reminder"
        verbose_name_plural = "Reminders"
        ordering = ["reminder_time"]

    def __str__(self):
        status = "✓ Sent" if self.is_sent else "⏳ Pending"
        return f"{self.user} | {self.reminder_time.strftime('%Y-%m-%d %H:%M')} | {status}"


class WeatherHistory(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="weather_requests")
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    condition = models.CharField(max_length=200)
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    request_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Weather History"
        verbose_name_plural = "Weather History"
        ordering = ["-request_time"]

    def __str__(self):
        return f"{self.user} | {self.city} | {self.temperature}°C | {self.request_time.strftime('%Y-%m-%d %H:%M')}"
