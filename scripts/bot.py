
import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import date, timedelta
from sqlalchemy import create_engine
from _helpers import get_tomorrow_agg, get_7_day_agg, get_logger


emoji_map = {
    "clear-day": "☀️",
    "clear-night": "🌕",
    "partly-cloudy-day": "🌤",
    "partly-cloudy-night": "🌥",
    "cloudy": "☁️",
    "fog": "🌫",
    "wind": "🌬",
    "rain": "🌧",
    "showers-day": "🌦",
    "showers-night": "🌧🌙",
    "snow": "🌨",
    "snow-showers-day": "🌨🌤",
    "snow-showers-night": "🌨🌙",
    "sleet": "🧊🌧",
    "hail": "🌨❄️",
    "thunder": "🌩",
    "thunder-rain": "⛈",
    "thunder-showers-day": "⛈🌤",
    "thunder-showers-night": "⛈🌙",
    "rain-snow": "🌧❄️",
    "rain-snow-showers-day": "🌧❄️🌤",
    "rain-snow-showers-night": "🌧❄️🌙"
}

# Set up logger
logger = get_logger("bot")

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DISC_ID = os.getenv('TELEGRAM_DISC_ID')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_PATH = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQL query for today's forecast data
today = date.today().isoformat()
tomorrow = (date.today() + timedelta(days=1)).isoformat()
query = f"""
SELECT *
FROM forecast_data
WHERE DATE(request_datetime) = '{today}'
  AND request_datetime = (
      SELECT MAX(request_datetime)
      FROM forecast_data
      WHERE DATE(request_datetime) = '{today}'
  )
ORDER BY request_datetime;
"""

# Connect to PostgreSQL and load data using SQLAlchemy
engine = create_engine(DB_PATH)
df = pd.read_sql_query(query, engine)

if df.empty:
    message = f"No forecast data available for {tomorrow}."
else:
    daily_result = get_tomorrow_agg(df, emoji_map)
    
    # Header
    message_lines = [f"📍 Астана — {tomorrow} (завтра)\n"]

    # Forecast lines
    for _, row in daily_result.iterrows():
        label = f"{str(row['3h_block']).zfill(2)}–{str(int(row['3h_block'])+3).zfill(2)}"
        emoji = row['emoji']
        temp = int(row['temp'])
        feels = int(row['feels'])
        humidity = int(row['humidity'])
        precip = row['precip']
        wind = row['wind']
        message_lines.append(
            f"{label} {emoji} {temp}°C ({feels}) 🌬{wind} 💧{precip}"
        )

    message = "\n".join(message_lines)

    forecast_7_day = get_7_day_agg(df, emoji_map)

    lines = [f"📍 Астана — Прогноз на 7 дней ({pd.Timestamp.today().date()})", ""]
    for _, row in forecast_7_day.iterrows():
        date = pd.to_datetime(row['date'])
        day_str = date.strftime("%a %d").replace("Mon", "Пн").replace("Tue", "Вт").replace("Wed", "Ср").replace("Thu", "Чт").replace("Fri", "Пт").replace("Sat", "Сб").replace("Sun", "Вс")
        line = (
            f"{day_str} "
            f"🌙{int(row['temp_night'])}°C "
            f"☀️{int(row['temp_day'])}°C "
            f"{row['06–09']}{row['10–13']}{row['14–17']}{row['18–21']}"
            f" 💧{row['precip']} мм"
        )
        lines.append(line)
    message_7d = "<pre>\n" + "\n".join(lines) + "\n</pre>"


# 1) Send 7-day forecast to discussion chat
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
forecast_data = {
    'chat_id': DISC_ID,
    'text': message_7d,
    'parse_mode': 'HTML'
}
response = requests.post(url, data=forecast_data)
res = response.json()

if not res.get("ok"):
    logger.info(f"❌ Failed to send forecast: {res}")
    exit()

forecast_message_id = res['result']['message_id']
logger.info(f"✅ 7-Day forecast posted in discussion. ID: {forecast_message_id}")


# 2) Build the link to that discussion message
discussion_username = "pogodastana"
forecast_link = f"https://t.me/{discussion_username}/{forecast_message_id}"


# 3) Send the short daily update to the channel with a button
time.sleep(1)
channel_data = {
    'chat_id': CHAT_ID,
    'text': message,
    'reply_markup': {
        'inline_keyboard': [
            [{'text': '📅 Прогноз на 7 дней', 'url': forecast_link}]
        ]
    }
}

response = requests.post(url, json=channel_data)
if response.status_code == 200 and response.json().get("ok"):
    logger.info("✅ Channel message sent with button.")
else:
    logger.info(f"❌ Failed to send channel message: {response.text}")