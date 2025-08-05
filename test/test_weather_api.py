import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
lat = os.getenv('LATITUDE')
lon = os.getenv('LONGITUDE')

def check_api_status():
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("API is working!")
    else:
        print("API error:", response.text)

if __name__ == '__main__':
    check_api_status()