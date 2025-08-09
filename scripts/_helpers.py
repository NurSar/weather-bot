
import os
import logging
import requests
import pandas as pd
from dotenv import load_dotenv
from collections import Counter

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


def get_7day_forecast_VS(datenow, lat=LAT, lon=LON, api_key=API_KEY_2, units='metric', lang='en'):
    """
    Fetch 7-day weather forecast for given coordinates from OpenWeatherMap API.
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
    for day in forecast_json.get('days', [])[1:8]:
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

# Emoji by 4-hour block
def get_block(hour):
    if 6 <= hour <= 9:
        return '06–09'
    elif 10 <= hour <= 13:
        return '10–13'
    elif 14 <= hour <= 17:
        return '14–17'
    elif 18 <= hour <= 21:
        return '18–21'
    return None

def get_tomorrow_agg(df, emoji_map):
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
        'wind': lambda x: round(x.mean()/3.6, 1),
        'condition': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    }).reset_index()

    daily_result = result.iloc[:5]
    daily_result['emoji'] = daily_result['condition'].map(emoji_map).fillna('❔')
    
    return daily_result

def get_7_day_agg(df, emoji_map):
    df_new = df.copy()
    df_new = df_new[(df_new['datetime'].dt.hour >= 6) & (df_new['datetime'].dt.hour <= 20)]
    df_new['hour'] = df_new['datetime'].dt.hour
    df_new['date'] = df_new['datetime'].dt.date

    # Convert icons to emojis
    df_new['emoji'] = df_new['condition'].map(emoji_map).fillna('❔')

    # Night (00–06): get min temp and feels_like
    night = (
        df_new[df_new['hour'].between(0, 6)]
        .groupby('date')[['temp', 'feels']]
        .min()
        .rename(columns={'temp': 'temp_night', 'feels': 'feels_night'})
    )

    # Day (12–18): get max temp and feels_like
    day = (
        df_new[df_new['hour'].between(12, 18)]
        .groupby('date')[['temp', 'feels']]
        .max()
        .rename(columns={'temp': 'temp_day', 'feels': 'feels_day'})
    )

    # Precipitation: sum over full day
    precip = df_new.groupby('date')['precip'].sum().round(1)

    df_new['block'] = df_new['hour'].apply(get_block)
    block_emojis = (
        df_new[df_new['block'].notna()]
        .groupby(['date', 'block'])['emoji']
        .agg(lambda x: Counter(x).most_common(1)[0][0])
        .unstack()
        .fillna('❔')
    )

    # Combine all
    forecast = pd.concat([night, day, precip, block_emojis], axis=1).reset_index()
    forecast = forecast.fillna('')  # Ensure no NaNs

    # Reorder columns
    forecast = forecast[['date', 'temp_night', 'feels_night', 'temp_day', 'feels_day',
                        '06–09', '10–13', '14–17', '18–21', 'precip']]
    
    return forecast