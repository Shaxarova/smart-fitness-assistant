# Smart Student Assistant — Presentation Slides

---

## Slide 1 — Project Title

**Smart Student Assistant**
Telegram Bot with Django Admin Panel

> A productivity tool for university students

- Developer: Shalkar Erik
- Course: Python Programming — Final Project
- Year: 2026

---

## Slide 2 — Problem Solved

**The Problem**

Students struggle to:
- Keep track of assignments and deadlines
- Remember important reminders
- Stay motivated during exam season
- Access quick information (weather, quotes) without leaving their phone

**The Solution**

A Telegram bot they already have open — no extra app needed.

Key pain points addressed:
- Scattered task management → centralized to-do list in the bot
- Missed deadlines → automated reminders sent directly to Telegram
- Manual weather checking → instant weather by city
- Low motivation → on-demand motivational quotes

---

## Slide 3 — Technologies

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.12 | Core runtime |
| Bot Framework | pyTelegramBotAPI | Telegram API communication |
| Web Framework | Django 4.2 | ORM, admin panel, settings |
| Database | SQLite | Persistent data storage |
| Scheduler | APScheduler | Automatic reminder delivery |
| HTTP Client | requests | Weather and quote APIs |
| Config | python-dotenv | Secure key management |

**External APIs:**
- OpenWeatherMap API — real-time weather
- ZenQuotes API — motivational quotes (free, no key)

---

## Slide 4 — Architecture

```
User (Telegram)
       │  Telegram API (HTTPS polling)
       ▼
  bot/bot.py  ──────────────────────────────┐
  bot/handlers.py (15+ commands)            │
  bot/services.py (business logic)          │ APScheduler
       │                                    │ (every 30s)
       ▼                                    │
  assistant/services.py (DB layer)          │
  assistant/models.py (ORM)                 │
       │                                    │
       ▼                                    ▼
  db.sqlite3 ◄──────── Django ORM ──────► Reminder check
       │
       ▼
  Django Admin (manage.py runserver)
  http://127.0.0.1:8000/admin/
```

**Data Flow:**
1. User sends command → Telegram delivers to bot via polling
2. Handler parses command → service function executes logic
3. Django ORM reads/writes SQLite → response sent back to user
4. Scheduler runs in background → checks due reminders → sends messages

---

## Slide 5 — Features

**Bot Commands (15+)**

| Command | Description |
|---|---|
| /start | Welcome + keyboard menu |
| /help | All commands |
| /about | Bot info |
| /addtask | Create task |
| /tasks | List tasks |
| /done | Complete task |
| /delete | Remove task |
| /weather | Real weather data |
| /quote | Motivational quote |
| /remind | Schedule reminder |
| /stats | Usage dashboard |
| /clearhistory | Erase history |
| Keyboard buttons | Tap-based navigation |
| Unknown command | Graceful error |
| Free text | Help redirect |

**Admin Panel**
- View all users and their activity
- Manage tasks (inline status edit)
- Browse full message history
- Monitor reminders and weather requests

---

## Slide 6 — Demo

**Live Demo Steps:**

1. Start bot → `/start` → keyboard menu appears
2. Add tasks → `/addtask Study for Python exam`
3. List tasks → `/tasks`
4. Complete task → `/done 1`
5. Check weather → `/weather Almaty`
6. Get quote → `/quote`
7. Set reminder → `/remind Submit project 23:59`
8. View stats → `/stats`
9. Admin panel → show users, tasks, message history

**Sample Output — /weather Almaty:**
```
🌍 Weather in Almaty, KZ
────────────────────────────
🌡  Temperature:  18.3°C (feels like 16.1°C)
☁️  Condition:    Partly cloudy
💧 Humidity:     52%
💨 Wind speed:   3.2 m/s
```

**Sample Output — /tasks:**
```
📋 Your tasks:

✅ #1 Study for Python exam
🔲 #2 Submit lab assignment
🔲 #3 Read chapter 5
```

---

## Slide 7 — Conclusion

**Results:**

- Fully working Telegram bot with 15+ commands
- Persistent SQLite database via Django ORM
- Professional admin panel for data management
- Background scheduler for automatic reminders
- Two real external API integrations
- Clean, modular architecture

**What I learned:**

- Django ORM and admin customization
- Telegram Bot API and long-polling
- Background scheduling with APScheduler
- REST API consumption and error handling
- Clean Python project architecture
- Environment-based configuration with dotenv

**Possible Enhancements:**

- Add webhook deployment (Heroku, Railway)
- Integrate GPT for smart Q&A
- Add study timer (Pomodoro)
- Multi-language support
- Grade tracker module

---

*Thank you for your attention!*
