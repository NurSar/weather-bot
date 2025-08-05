import os
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from weather import Weather, DB_PATH
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # Set your chat ID here or dynamically

engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

bot = Bot(token=TELEGRAM_TOKEN)


def get_latest_weather():
    session = Session()
    weather = session.query(Weather).order_by(Weather.timestamp.desc()).first()
    session.close()
    return weather

def send_daily_weather():
    weather = get_latest_weather()
    if weather:
        message = f"Astana Weather {weather.timestamp.strftime('%Y-%m-%d %H:%M')}: {weather.temperature}°C"
        bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        bot.send_message(chat_id=CHAT_ID, text="No weather data available.")

def start(update, context):
    weather = get_latest_weather()
    if weather:
        update.message.reply_text(f"Current Astana temperature: {weather.temperature}°C")
    else:
        update.message.reply_text("No weather data available.")

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_weather, 'cron', hour=9, minute=0)  # Sends at 09:00 every day
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
