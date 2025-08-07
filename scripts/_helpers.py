import os
import requests
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()

API_KEY_1 = os.getenv('OPENWEATHER_API_KEY')
API_KEY_2 = os.getenv('VISUALCROSSING_API_KEY')
LAT = os.getenv('LATITUDE')
LON = os.getenv('LONGITUDE')


def get_5day_forecast_VS(lat=LAT, lon=LON, api_key=API_KEY_2, units='metric', lang='en'):
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
    request_time = datetime.utcnow()
    records = []
    for day in forecast_json.get('days', [])[:5]:
        date = day['datetime']
        for hour in day.get('hours', []):
            dt_str = f"{date} {hour['datetime']}"
            dt = pd.to_datetime(dt_str)
            records.append({
                'request_datetime': request_time,
                'datetime': dt,
                'temp': hour['temp'],
                'feels': hour['feelslike'],
                'humidity': hour['humidity'],
                'precip': hour['precip'],
            })
    return pd.DataFrame(records)

def get_yesterday_VS(lat=LAT, lon=LON, api_key=API_KEY_2, units='metric', lang='en'):
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lat}%2C%20{lon}/yesterday?unitGroup=metric&include=hours&key={api_key}&contentType=json"
    )
    response = requests.get(url)
    response.raise_for_status()
    forecast_json = response.json()
    request_time = datetime.utcnow()
    records = []
    for day in forecast_json.get('days', []):
        date = day['datetime']
        for hour in day.get('hours', []):
            dt_str = f"{date} {hour['datetime']}"
            dt = pd.to_datetime(dt_str)
            records.append({
                'request_datetime':request_time,
                'datetime': dt,
                'temp': hour['temp'],
                'feels': hour['feelslike'],
                'humidity': hour['humidity'],
                'precip': hour['precip'],
            })
    return pd.DataFrame(records)