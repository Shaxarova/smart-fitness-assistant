# Smart Student Assistant — Telegram Bot

**Author:** Shalkar Erik

A fully functional Telegram bot that helps students manage tasks, check weather, set reminders, and stay motivated — backed by a Django admin panel and SQLite database.

---

## Features

| Feature | Description |
|---|---|
| Task Manager | Add, list, complete, and delete personal tasks |
| Weather | Real-time weather for any city via OpenWeather API |
| Motivational Quotes | Daily quotes from ZenQuotes API with fallback |
| Reminders | Schedule reminders that the bot sends automatically |
| Statistics | Personal usage dashboard |
| Message History | Every conversation saved; clearable on demand |
| Django Admin | Full admin panel to view/edit all data |
| Keyboard Menu | Tap buttons instead of typing commands |
| Error Handling | Graceful handling of bad input, API failures, DB errors |

---

## Technologies

- **Python 3.12**
- **Django 4.2** — ORM + admin panel
- **pyTelegramBotAPI 4.x** — Telegram Bot API wrapper
- **APScheduler 3.x** — background job for reminders
- **SQLite** — zero-config file database
- **requests** — HTTP calls to weather and quote APIs
- **python-dotenv** — environment variable management

---

## Project Structure

```
student_bot/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── bot.log               (created at runtime)
├── db.sqlite3            (created after migrate)
│
├── core/                 Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── bot/                  Telegram bot logic
│   ├── bot.py            Entry point
│   ├── handlers.py       Command & message handlers
│   ├── services.py       Bot-layer business logic
│   ├── keyboards.py      Reply keyboard layouts
│   └── scheduler.py      APScheduler reminder job
│
└── assistant/            Django app
    ├── models.py         ORM models
    ├── admin.py          Admin panel config
    ├── services.py       DB service functions
    ├── utils.py          API helpers (weather, quotes)
    └── migrations/
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourname/student_bot.git
cd student_bot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
DJANGO_SECRET_KEY=your_django_secret_key_here
DJANGO_DEBUG=True
```

### How to get a Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts (choose a name and username)
4. BotFather will give you a token like `1234567890:ABCDEFabcdef...`
5. Paste it as `TELEGRAM_BOT_TOKEN` in `.env`

### How to get an OpenWeather API Key

1. Register at https://openweathermap.org/api
2. Go to **My API keys** in your profile
3. Copy the default key (or create a new one)
4. Paste it as `OPENWEATHER_API_KEY` in `.env`
5. Free tier is sufficient (1000 calls/day)

---

## Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Create Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

---

## Run the Bot

```bash
python bot/bot.py
```

The bot starts polling for messages. The scheduler checks for due reminders every 30 seconds.

---

## Run the Admin Panel

In a separate terminal:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ and log in with your superuser credentials.

---

## Bot Commands

```
/start              — Welcome message + keyboard menu
/help               — Show all commands
/about              — Bot description

/addtask <text>     — Add a new task
/tasks              — List all your tasks
/done <id>          — Mark task as completed
/delete <id>        — Delete a task

/weather <city>     — Show weather for a city
/quote              — Get a motivational quote

/remind <msg> <time> — Set a reminder
                       Time formats:
                       18:30            (today)
                       25.12 18:30      (date this year)
                       25.12.2025 18:30 (full date)

/stats              — Show your usage statistics
/clearhistory       — Delete your message history
```

### Example Usage

```
/weather Almaty
/addtask Prepare presentation for CS class
/tasks
/done 1
/delete 2
/remind Submit homework 23:59
/stats
```

---

## Screenshots

> Admin panel — Users list
> ![Users](screenshots/admin_users.png)

> Admin panel — Tasks
> ![Tasks](screenshots/admin_tasks.png)

> Bot chat — Weather
> ![Weather](screenshots/bot_weather.png)

> Bot chat — Tasks
> ![Tasks chat](screenshots/bot_tasks.png)

---

## Notes

- The bot uses long-polling (no webhook needed for local/university deployment)
- All times use the `Asia/Almaty` timezone (configurable in `core/settings.py`)
- Reminders are checked every 30 seconds by the background scheduler
- The ZenQuotes API is free and requires no key; a local fallback list is included
