# Astana Weather Bot

This Python project reads the temperature of Astana, saves it to a local SQLite database, and uses a Telegram bot to send daily weather updates.

## Features
- Fetches current temperature for Astana using a weather API
- Stores weather data in a local SQLite database
- Sends daily weather updates via Telegram bot

## Requirements
- Python 3.11+
- requests
- python-telegram-bot
- sqlalchemy
- apscheduler

## Setup
1. Install dependencies (already handled by setup)
2. Set your Telegram bot token and OpenWeatherMap API key in the `.env` file (to be created)

## Usage
- Run the main script to start the bot and scheduler.

---

This project was generated and managed with GitHub Copilot.
