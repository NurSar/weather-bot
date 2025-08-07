
import os
import logging
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY_2 = os.getenv('VISUALCROSSING_API_KEY')
LAT = os.getenv('LATITUDE')
LON = os.getenv('LONGITUDE')


def get_logger(name=__name__):
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(f'logs/{name}.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_5day_forecast_VS(datenow, lat=LAT, lon=LON, api_key=API_KEY_2, units='metric', lang='en'):
    """
    Fetch 5-day weather forecast for given coordinates from OpenWeatherMap API.
    Returns a pandas DataFrame with selected columns for each 3-hour interval.
    """
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lat}%2C%20{lon}?unitGroup=metric&include=hours&key={api_key}&contentType=json"
    )
    response = requests.get(url)
    response.raise_for_status()
    forecast_json = response.json()
    records = []
    for day in forecast_json.get('days', [])[:5]:
        date = day['datetime']
        for hour in day.get('hours', []):
            dt_str = f"{date} {hour['datetime']}"
            dt = pd.to_datetime(dt_str)
            records.append({
                'request_datetime': datenow,
                'datetime': dt,
                'temp': hour['temp'],
                'feels': hour['feelslike'],
                'humidity': hour['humidity'],
                'precip': hour['precip'],
                'wind': hour['windspeed'],
                'condition': hour['icon'],
            })
    return pd.DataFrame(records)


def get_yesterday_VS(datenow, lat=LAT, lon=LON, api_key=API_KEY_2, units='metric', lang='en'):
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lat}%2C%20{lon}/yesterday?unitGroup=metric&include=hours&key={api_key}&contentType=json"
    )
    response = requests.get(url)
    response.raise_for_status()
    forecast_json = response.json()
    records = []
    for day in forecast_json.get('days', []):
        date = day['datetime']
        for hour in day.get('hours', []):
            dt_str = f"{date} {hour['datetime']}"
            dt = pd.to_datetime(dt_str)
            records.append({
                'request_datetime':datenow,
                'datetime': dt,
                'temp': hour['temp'],
                'feels': hour['feelslike'],
                'humidity': hour['humidity'],
                'precip': hour['precip'],
                'wind': hour['windspeed'],
                'condition': hour['icon'],
            })
    return pd.DataFrame(records)