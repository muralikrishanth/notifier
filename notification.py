import os
import requests
from datetime import datetime, date

# --- Telegram Bot Setup ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    """Send formatted message to Telegram (HTML style)."""
    if not TOKEN or not CHAT_ID:
        raise ValueError("Missing Telegram credentials")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True  # optional: prevents link previews
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        print("❌ Telegram API error:", response.text)

# --- Weather Section ---
def get_weather():
    WEATHER_URL = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=47.999&longitude=7.842"
        "&hourly=temperature_2m,precipitation_probability,rain"
        "&timezone=Europe/Berlin"
    )
    try:
        res = requests.get(WEATHER_URL).json()
        idx = -1
        temp = res["hourly"]["temperature_2m"][idx]
        rain = res["hourly"]["rain"][idx]
        precip = res["hourly"]["precipitation_probability"][idx]
        time = res["hourly"]["time"][idx]
        return (
            f"🌤 Weather in Freiburg\n"
            f"Temperature: {temp}°C\n"
            f"Precipitation: {precip}%"
        )
    except Exception as e:
        return f"⚠️ Could not fetch weather ({e})"

# --- Headlines Section ---
def translate_to_english(text):
    """Translate German text to English using MyMemory API (free)."""
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": "de|en"}
        res = requests.get(url, params=params, timeout=20).json()
        return res["responseData"]["translatedText"]
    except Exception as e:
        print("Translation error:", e)
        return text  # fallback to original German if translation fails

def get_headlines():
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    german_headlines, intl_headlines = [], []

    # 🇩🇪 German headlines (Tagesschau)
    try:
        res_de = requests.get("https://www.tagesschau.de/api2u/news/", timeout=30).json()
        for a in res_de.get("news", [])[:3]:
            title = a.get("title")
            if title:
                translated = translate_to_english(title)
                german_headlines.append(f"• {translated}")
    except Exception as e:
        print("Error fetching Tagesschau:", e)

    # 🌍 International headlines (NewsAPI)
    try:
        if NEWS_API_KEY:
            url_intl = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
            res_intl = requests.get(url_intl, timeout=30).json()
            for a in res_intl.get("articles", [])[:3]:
                t = a.get("title")
                if t:
                    intl_headlines.append(f"• {t}")
    except Exception as e:
        print("Error fetching international news:", e)

    if not german_headlines and not intl_headlines:
        return "📰 <b>Headlines</b>\nNo news found."

    text = "📰 <b>Headlines</b>\n"
    if german_headlines:
        text += "<b>🇩🇪 German News</b>\n" + "\n".join(german_headlines) + "\n<i>(source: Tagesschau)</i>\n\n"
    if intl_headlines:
        text += "<b>🌍 International News</b>\n" + "\n".join(intl_headlines) + "\n<i>(source: NewsAPI)</i>"
    return text


# --- Quote Section ---
def get_quote():
    try:
        res = requests.get("https://zenquotes.io/api/random").json()
        q, a = res[0]["q"], res[0]["a"]
        return f"💬 <b>Quote of the Day</b>\n“{q}” ~ {a}"
    except Exception:
        return "💬 <b>Quote of the Day</b>\nKeep pushing forward — you’ve got this!"
    

# --- Today in History Section ---
def get_today_events():
    today = date.today()
    try:
        url = f"https://byabbe.se/on-this-day/{today.month}/{today.day}/events.json"
        res = requests.get(url).json()
        events = res.get("events", [])[:3]
        if not events:
            return "📆 No events found for today."
        text = "\n".join([f"• {e['year']}: {e['description']}" for e in events])
        return f"📆 <b>On this day ({today.strftime('%b %d')})</b>\n{text}"
    except Exception as e:
        return f"📆 Could not fetch today’s events ({e})"
    

# --- Personal Reminders ---
# MM-DD
reminders = {
    "01-01": "🎂 Happy New Year!",
    "12-19": "🎂 Mom's Birthday",
    "02-07": "🎂 Dad's Birthday & Shrithika's Birthday",
    "02-15": "🎂 Ricky's Birthday",
    "08-05": "🎂 Sister's Birthday",
    "05-16": "🎂 Parent's Wedding anniversary",
    "06-15": "🎂 Kiran's Birthday",
    "07-10": "🎂 Danush's Birthday",
    "08-10": "🎂 Yugesh's Birthday",
    "08-20": "🎂 Haamid's Birthday",
    "08-26": "🎂 Aro's Birthday",
    "05-25": "🎂 Karthikeyan's Birthday",
    "03-06": "🎂 Harish Balaji's Birthday",
    "12-11": "🎂 Kishore's Birthday",
    "03-14": "🎂 Nidarshan's Birthday",
    "09-24": "🎂 Mrunmayee's Birthday",
    "05-28": "🎂 Jowin's Birthday",
    "06-08": "🎂 Mahalakshmi's Birthday",
    "12-14": "🎂 Sister's Wedding anniversary",
    "12-22": "🎂 Brother-in-law's Birthday",
    "12-25": "🎂 Merry Christmas",
}

def get_upcoming_events():
    today = datetime.now().strftime("%m-%d")
    msgs = [f"<b>Today:</b> {event}" for d, event in reminders.items() if d == today]
    return "\n".join(msgs) if msgs else ""

# --- Combine Everything ---
def build_daily_message():
    today_str = datetime.now().strftime("%A, %b %d %Y")

    parts = [
        f"🌞 <b>Good Morning!</b>\nHere’s your daily update ☕️",
        f"<i>{today_str}</i>",  # adds date just below greeting
        "",
        get_weather(),
        "",
        "----",
        get_headlines(),
        "",
        "----",  # visually separate quote section
        get_quote(),
        "",
        # "📆",  # visually separate events section
        # get_today_events(),
        "",
        "----",
        get_upcoming_events(),
    ]

    # Join and remove any accidental double empty lines
    message = "\n".join([p for p in parts if p.strip()])
    return message.strip()

# --- Main ---
if __name__ == "__main__":
    message = build_daily_message()
    send_message(message)
    print("✅ Daily update sent!")
