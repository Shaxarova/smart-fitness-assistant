import requests
import os
from django.conf import settings
from django.utils import timezone
from datetime import datetime

FALLBACK_QUOTES = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Education is the most powerful weapon you can use to change the world.", "Nelson Mandela"),
    ("The beautiful thing about learning is that no one can take it away from you.", "B.B. King"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
]


def get_motivational_quote() -> str:
    try:
        response = requests.get(
            "https://zenquotes.io/api/random",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return f'"{quote}"\n\n— {author}'
    except Exception:
        import random
        text, author = random.choice(FALLBACK_QUOTES)
        return f'"{text}"\n\n— {author}'


def get_weather(city: str) -> dict:
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        return {"error": "OpenWeather API key is not configured. Set OPENWEATHER_API_KEY in .env"}

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "en",
        }
        response = requests.get(url, params=params, timeout=8)

        if response.status_code == 404:
            return {"error": f'City "{city}" not found. Check the spelling and try again.'}
        if response.status_code == 401:
            return {"error": "Invalid OpenWeather API key. Check your .env file."}

        response.raise_for_status()
        data = response.json()

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "condition": data["weather"][0]["description"].capitalize(),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {"error": "Weather service timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to weather service. Check your internet connection."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def parse_reminder_time(time_str: str):
    """
    Parse reminder time from string. Supports:
    - HH:MM (today at that time)
    - DD.MM HH:MM
    - DD.MM.YYYY HH:MM
    Returns aware datetime or None.
    """
    now = timezone.now()
    formats = [
        ("%d.%m.%Y %H:%M", True),
        ("%d.%m %H:%M", False),
        ("%H:%M", False),
    ]
    for fmt, has_year in formats:
        try:
            naive = datetime.strptime(time_str.strip(), fmt)
            if fmt == "%H:%M":
                naive = naive.replace(year=now.year, month=now.month, day=now.day)
            elif not has_year:
                naive = naive.replace(year=now.year)
            aware = timezone.make_aware(naive, timezone.get_current_timezone())
            return aware
        except ValueError:
            continue
    return None
