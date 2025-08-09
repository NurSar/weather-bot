
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
from _helpers import get_7day_forecast_VS, get_yesterday_VS, get_logger

# Set up logger
logger = get_logger("weather")

# Load environment variables
load_dotenv()

API_KEY = os.getenv('VISUALCROSSING_API_KEY')
LAT = os.getenv('LATITUDE')
LON = os.getenv('LONGITUDE')
CITY= os.getenv('CITY')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_PATH = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_PATH)

if __name__ == '__main__':
    date = datetime.now()
    # Fetch 5-day forecast as a DataFrame
    forecast_df = get_7day_forecast_VS(date, LAT, LON, API_KEY)

    # Push the DataFrame into the database table 'forecast_data'
    forecast_df.to_sql('forecast_data', engine, if_exists='append', index=False)
    logger.info("✅ 7-day forecast data written to database!")

    # Fetch yesterday data as a DataFrame
    historical_df = get_yesterday_VS(date, LAT, LON, API_KEY)

    # Push the DataFrame into the database table 'historical_data'
    historical_df.to_sql('historical_data', engine, if_exists='append', index=False)
    logger.info("✅ Yesterday's data written to database!")

