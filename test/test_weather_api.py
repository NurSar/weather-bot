import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv('VISUALCROSSING_API_KEY')
lat = os.getenv('LATITUDE')
lon = os.getenv('LONGITUDE')

def check_api_status():
    # url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    # url = (
    #     f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    #     f"{lat}%2C%20{lon}?unitGroup=metric&include=hours&key={API_KEY}&contentType=json"
    # )
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lat}%2C%20{lon}/yesterday?unitGroup=metric&include=hours&key={API_KEY}&contentType=json"
    )
    response = requests.get(url)
    print(response.json())
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("API is working!")
    else:
        print("API error:", response.text)

if __name__ == '__main__':
    check_api_status()