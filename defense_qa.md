# Defense Q&A — 20 Professor Questions & Strong Answers
**Author: Shalkar Erik**

---

## 1. Why did you choose Django instead of Flask or FastAPI?

**Answer:**
Django was chosen primarily for its built-in admin panel. Creating a professional data management interface in Flask would require writing it from scratch or using Flask-Admin, which is much less polished. Django's ORM is also more mature for relational data with multiple related models. Since this project doesn't need high-performance async endpoints, Django's synchronous model is completely adequate. Flask would add flexibility we don't need; FastAPI would add async complexity without benefit here.

---

## 2. Why SQLite and not PostgreSQL or MySQL?

**Answer:**
SQLite is a perfect fit for a project of this scale. It requires zero configuration — no server process, no credentials, no installation. The database is a single file (`db.sqlite3`) which makes the project fully portable. Django supports SQLite natively. For a university project or a single-user bot, SQLite handles thousands of rows with no performance issues. Migrating to PostgreSQL later requires only a one-line change in `settings.py` — the ORM abstracts the database engine completely.

---

## 3. How does the Telegram Bot API work?

**Answer:**
The Telegram Bot API is a REST HTTP interface hosted by Telegram. Our bot uses **long-polling**: it repeatedly calls `getUpdates` with a 20-second timeout. Telegram holds the connection open until a new message arrives, then returns it immediately. `pyTelegramBotAPI` wraps this loop in `infinity_polling()`, which handles reconnection and exceptions automatically. The alternative is webhooks (Telegram pushes updates to our HTTPS endpoint), which requires a public server with SSL — long-polling is simpler for local/university deployment.

---

## 4. How does APScheduler work in your project?

**Answer:**
APScheduler runs a `BackgroundScheduler` — a separate daemon thread inside the same Python process as the bot. We register a job (`check_and_send_reminders`) with an `IntervalTrigger` of 30 seconds. Every 30 seconds, the job queries the database for `Reminder` records where `is_sent=False` and `reminder_time <= now()`. For each due reminder, it calls `bot.send_message()` to the user's Telegram ID, then marks the reminder as sent. This approach requires no extra process or cron daemon.

---

## 5. How does the Django ORM work?

**Answer:**
Django ORM is a Python abstraction layer over SQL. We define models as Python classes inheriting from `django.db.models.Model`. Each class attribute becomes a database column. Django generates SQL `CREATE TABLE` statements from these models via migrations. Queries are expressed in Python (e.g., `Task.objects.filter(user=user, status='pending')`) — Django translates them to `SELECT ... WHERE ...` SQL. Relationships between models (ForeignKey) become JOIN operations. We never write raw SQL, which prevents SQL injection by default.

---

## 6. Explain your project's architecture.

**Answer:**
The project has three layers:

1. **Bot layer** (`bot/`) — Telegram-facing. Handlers receive messages, parse commands, and call service functions. This layer knows about Telegram but nothing about the database directly.
2. **Service layer** (`assistant/services.py`, `bot/services.py`) — Business logic. Orchestrates DB calls and API calls. Testable independently of Telegram.
3. **Data layer** (`assistant/models.py`) — Django ORM models and migrations. All database access goes through here.

This separation means we can change the database without touching bot logic, and vice versa.

---

## 7. How do you handle errors so the bot never crashes?

**Answer:**
Several strategies:

- `infinity_polling()` from `pyTelegramBotAPI` catches network exceptions and reconnects automatically.
- Every handler has explicit validation: missing arguments return a help message instead of raising an exception.
- API calls (`requests.get`) are wrapped in `try/except` with specific handling for `Timeout`, `ConnectionError`, 404, and 401 status codes.
- Database operations use `try/except` around `Task.DoesNotExist` and similar lookups.
- The scheduler job has its own `try/except` per reminder so one failed send doesn't stop others.
- Unknown commands and free-text messages are caught by catch-all handlers at the bottom of the handler list.

---

## 8. How do you store and retrieve reminders?

**Answer:**
Reminders are stored in the `Reminder` table with fields: `user`, `reminder_text`, `reminder_time` (timezone-aware datetime), `is_sent` (boolean). When `/remind` is called, we parse the time string using `strptime` with multiple format patterns, convert to an aware datetime using `django.utils.timezone.make_aware()`, and save the record. The APScheduler job queries `Reminder.objects.filter(is_sent=False, reminder_time__lte=timezone.now())` every 30 seconds and sends due reminders.

---

## 9. How does the weather API integration work?

**Answer:**
We call `https://api.openweathermap.org/data/2.5/weather` with the city name, API key, and `units=metric`. The response JSON contains temperature, feels-like, weather description, humidity, and wind speed. We check the HTTP status code: 404 means the city wasn't found, 401 means invalid API key, other errors raise exceptions. The result is formatted into a readable multi-line message and sent to the user. Every successful request is also saved to `WeatherHistory` for admin review.

---

## 10. How does the quote API work, and what if it fails?

**Answer:**
We call `https://zenquotes.io/api/random` — a free public API that returns a JSON array with `q` (quote) and `a` (author). The entire call is inside a `try/except`: if the API is down, returns an error, or times out (5-second timeout), we catch the exception and return a random quote from a hardcoded list of 8 fallback quotes. The user always gets a quote — the bot never shows an error for this command.

---

## 11. What is a Django migration and why do we need it?

**Answer:**
A migration is an auto-generated Python file that describes a schema change (create table, add column, etc.) in a version-controlled, reversible way. When we run `makemigrations`, Django inspects our models and generates the migration. When we run `migrate`, Django applies it to the database. This means the database schema always stays in sync with the code. Migrations also allow rollbacks and team collaboration — every developer applies the same migrations in sequence and gets an identical database.

---

## 12. How do you prevent SQL injection?

**Answer:**
We don't write any raw SQL — all queries go through Django ORM. Django parameterizes all queries internally, so user-supplied values (like a city name or task title) are never interpolated directly into SQL strings. For example, `Task.objects.filter(title=user_input)` becomes a prepared statement. Even if a user types `'; DROP TABLE tasks; --` as their task, it's stored safely as a literal string.

---

## 13. How does the Django admin panel work?

**Answer:**
Django's admin is auto-generated from model definitions. By registering a model with `admin.site.register()` or using the `@admin.register()` decorator with a `ModelAdmin` subclass, we get a complete CRUD interface. We customized it with `list_display` (which columns to show), `list_filter` (sidebar filters), `search_fields` (search box), `readonly_fields` (prevent editing key fields), and `list_editable` (inline editing). We also added custom methods like `colored_status()` that use `format_html` to render colored HTML badges in the task list.

---

## 14. Explain the ForeignKey relationship in your models.

**Answer:**
A `ForeignKey` creates a many-to-one relationship. For example, `Task.user = ForeignKey(TelegramUser, on_delete=CASCADE)` means many tasks can belong to one user. In the database, `Task` gets a `user_id` integer column that references `TelegramUser.id`. `on_delete=CASCADE` means if a user is deleted, all their tasks are deleted automatically. We access related tasks via `user.tasks.all()` (the reverse accessor Django creates automatically). In SQL terms, this becomes `SELECT * FROM task WHERE user_id = ?`.

---

## 15. How does the reminder time parsing work?

**Answer:**
The `parse_reminder_time()` function tries three `datetime.strptime` format strings in order: `%H:%M`, `%d.%m %H:%M`, and `%d.%m.%Y %H:%M`. For each format, it attempts to parse the string and catches `ValueError` if it fails. For time-only format, it substitutes today's year, month, and day. For date-without-year format, it substitutes the current year. The resulting naive datetime is converted to a timezone-aware datetime using Django's `timezone.make_aware()` with the configured timezone. If all formats fail, the function returns `None` and the handler tells the user the correct format.

---

## 16. Why do you use `python-dotenv` and what problem does it solve?

**Answer:**
Sensitive credentials (bot token, API keys, secret key) must not be hardcoded in source code — if the code is shared or uploaded to GitHub, those keys get exposed. `python-dotenv` loads a `.env` file into `os.environ` at startup. The `.env` file is excluded from version control via `.gitignore`. The `.env.example` file (committed) shows which variables are needed without revealing actual values. In production, environment variables are typically set directly on the server, and `python-dotenv` falls back gracefully when no `.env` file is present.

---

## 17. How would you deploy this bot to a server?

**Answer:**
1. Rent a VPS (DigitalOcean, Hetzner, etc.) with Python 3.12 installed.
2. Clone the repository and install requirements in a virtualenv.
3. Copy `.env.example` to `.env` and set production values.
4. Run `python manage.py migrate` and `python manage.py createsuperuser`.
5. Run `python bot/bot.py` as a background service using `systemd` or `supervisor`.
6. Run `gunicorn core.wsgi` behind Nginx for the admin panel with a domain and SSL.
7. Alternatively, switch to webhooks and point Telegram to the Nginx endpoint for better reliability.

---

## 18. How do you ensure the bot handles concurrent users correctly?

**Answer:**
Telegram delivers each user's messages in order, and `infinity_polling()` processes them sequentially. For a university-scale bot (tens to hundreds of users), this is sufficient. Django ORM uses SQLite's built-in write locking — concurrent writes are serialized automatically. If we needed to scale to thousands of concurrent users, we would switch to PostgreSQL (which handles concurrent connections properly) and run the bot with multiple workers behind a message queue (Celery + Redis), but that's overkill for this project's scope.

---

## 19. What is the difference between `get_or_create` and `get` in the ORM?

**Answer:**
`Model.objects.get(field=value)` raises `Model.DoesNotExist` if no record is found, and `MultipleObjectsReturned` if more than one matches. It's used when you're certain the record exists. `get_or_create(field=value, defaults={...})` atomically gets the record if it exists or creates it with the `defaults` if it doesn't — it returns `(instance, created)` where `created` is a boolean. We use `get_or_create` for `TelegramUser` because the first time a user interacts with the bot, there's no record yet — but on every subsequent message, we just fetch the existing one.

---

## 20. What would you improve if you had more time?

**Answer:**
Several meaningful improvements:

1. **Webhook mode** — more efficient than polling, required for production deployment.
2. **PostgreSQL** — better for concurrent writes and production reliability.
3. **Async bot** — use `asyncio`-based `aiogram` library for higher throughput.
4. **User authentication** — link Telegram accounts to university student IDs.
5. **Grade tracker** — store subjects and grades, calculate GPA.
6. **Study timer** — Pomodoro timer with Telegram notifications.
7. **NLP intent detection** — let users type naturally ("remind me tomorrow at 9") instead of strict command format.
8. **Unit tests** — pytest test suite for all service functions.
9. **Docker Compose** — containerize bot + admin for one-command deployment.
10. **Rate limiting** — prevent abuse from single users flooding the bot.
