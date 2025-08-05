import os
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')
lat = os.getenv('LATITUDE')
lon = os.getenv('LONGITUDE')
DB_PATH = 'sqlite:///weather.db'

Base = declarative_base()

class Weather(Base):
    __tablename__ = 'weather'
    id = Column(Integer, primary_key=True)
    city = Column(String)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

def get_temperature(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data['main']['temp']

def save_temperature(city, temperature):
    engine = create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    weather = Weather(city=city, temperature=temperature)
    session.add(weather)
    session.commit()
    session.close()

def main():
    temp = get_temperature(CITY)
    save_temperature(CITY, temp)
    print(f"Saved temperature for {CITY}: {temp}°C")

if __name__ == '__main__':
    main()
