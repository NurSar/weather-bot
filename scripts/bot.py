
import os
import requests
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine


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

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_PATH = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQL query for today's forecast data
today = date.today().isoformat()
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
    message = f"No forecast data available for {today}."
else:
    df_new = df.copy()
    df_new = df_new[(df_new['datetime'].dt.hour >= 6) & (df_new['datetime'].dt.hour <= 20)]
    df_new['hour'] = df_new['datetime'].dt.hour
    df_new['3h_block'] = (df_new['hour'] // 3) * 3
    df_new['3h_label'] = df_new['3h_block'].astype(str).str.zfill(2) + '–' + (df_new['3h_block'] + 3).astype(str).str.zfill(2)
    grouped = df_new.groupby([df_new['datetime'].dt.date, '3h_block'])

    result = grouped.agg({
        'temp': lambda x: round(x.mean()),
        'feels': lambda x: round(x.mean()),
        'humidity': lambda x: round(x.mean()),
        'precip': lambda x: round(x.mean(), 1),
        'wind': lambda x: round(x.mean(), 1),
        'condition': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    }).reset_index()

    daily_result = result.iloc[:5]
    daily_result['emoji'] = daily_result['condition'].map(emoji_map).fillna('❔')
    
    # Header
    message_lines = [f"📍 Астана — {today}"]

    # Forecast lines
    for _, row in daily_result.iterrows():
        label = f"{str(row['3h_block']).zfill(2)}–{str(int(row['3h_block'])+3).zfill(2)}"
        emoji = row['emoji']
        temp = int(row['temp'])
        feels = int(row['feels'])
        humidity = int(row['humidity'])
        precip = row['precip']
        message_lines.append(
            f"{label} {emoji}  {temp}° ({feels}°)  💧{humidity}%  ☔️{precip}%"
        )

    message = "\n".join(message_lines)

# Send to Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
data = {
    'chat_id': CHAT_ID,
    'text': message
}
response = requests.post(url, data=data)

if response.status_code == 200:
    print("✅ Message sent to Telegram.")
else:
    print("❌ Failed to send message:", response.text)