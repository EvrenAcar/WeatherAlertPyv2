# Evren Acar - 04/02/2024
# Hozio: Python Weather Bot - WeatherNotification.py
# Last Updated: 04/22/2024

# Pulls Longitude and Latitude from IP with ipinfo.io to use in weather API 
# Reads and then sends a forecast notification alerting for extreme weather conditions to your Desktop, Email, and Discord

# Once the code starts running it will loop every set amount of hours you put in the config.json file (default is: "notifFrequency": 12) this code is meant to run forever and will do so unless you end it by pressing CTRL + C while in the terminal.

# You must have the config.json file in the same place as this python file to run the code

# REQUIRED PIP INSTALLS
# pip install requests (To get the forecast)
# pip install plyer (for Desktop notifications)
# pip install yagmail (For Email notifications)
# pip install discord.py (For Discord notifications)

# JSON File config - Make sure to insert all information you plan to use in the json file
# {
#     "discordToken": "", (In the double quotes paste your Discord Bot Token)
#     "discordUserID": , (right before the , paste the user ID you want to recieve the Discord DM)
#     "emailPassword": "", (In the double quotes paste your Bot emails application password)
#     "emailSender": "", (In the double quotes paste your bot email you want to send the weather alert)
#     "emailRecipient": "", (In the double quotes paste your email you want to alert to be sent to)
#     "WeatherAPI": "", (In the double quotes paste your OpenWeatherMaps API Key)
#     "rain": , (right before the , type the value you want the rain alert to trigger at Default is 45(mm every 3 hours))
#     "snow": , (right before the , type the value you want the snow alert to trigger at Default is 25 (mm every 3 hours))
#     "heat": , (right before the , type the value you want the heat alert to trigger at Default is 30 (c))
#     "cold": , (right before the , type the value you want the cold alert to trigger at Default is 0 (c))
#     "notifFrequency": 12 (right before the , type the rate you want the alerts to be sent default is 12 (hours))
# }

import requests
from datetime import datetime
import json
import time
from plyer import notification
import yagmail
import discord
from discord.ext import commands

# Function to get the location based on IP
def get_location():
    response = requests.get('https://ipinfo.io')
    data = response.json()
    city = data.get('city')
    latitude, longitude = map(float, data.get('loc').split(','))
    return city, latitude, longitude

# Function to fetch weather forecast from OpenWeatherMap API
def get_weather_forecast(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

# Function to construct weather alerts
def construct_alerts(extreme_weather_days, construct_func):
    alerts = [construct_func(day_temp) for day_temp in extreme_weather_days]
    return ', '.join(alerts)

# Function to check extreme cold weather
def is_extreme_cold(main, extreme_cold_threshold):
    return main['temp_min'] < extreme_cold_threshold

# Function to check extreme hot weather
def is_extreme_hot(main, extreme_heat_threshold):
    return main['temp_max'] > extreme_heat_threshold

# Function to check heavy rain
def is_heavy_rain(weather, rain_threshold):
    return 'Rain' in weather['description'] and weather['rain']['3h'] > rain_threshold

# Function to check heavy snow
def is_heavy_snow(weather, snow_threshold):
    return 'Snow' in weather['description'] and weather['snow']['3h'] > snow_threshold

# Function to update extreme weather days
def update_extreme_weather_days(extreme_weather_days, day, value, category):
    extreme_weather_days[category].add((day, value))

# Function to print weather alerts
def print_weather_alerts(weather_data, extreme_cold_threshold, extreme_heat_threshold, heavy_rain_threshold, heavy_snow_threshold):
    extreme_weather_days = {'cold': set(), 'hot': set(), 'rain': set(), 'snow': set()}
    days_mentioned = set()  # Track the days already mentioned

    for forecast in weather_data['list']:
        weather = forecast['weather'][0]
        main = forecast['main']
        dt_txt = forecast['dt_txt']
        day = datetime.strptime(dt_txt[:10], '%Y-%m-%d').strftime('%A')

        if day in days_mentioned:  # Skip if day is already mentioned
            continue

        if is_extreme_cold(main, extreme_cold_threshold):
            update_extreme_weather_days(extreme_weather_days, day, main['temp_min'], 'cold')
            days_mentioned.add(day)
        elif is_extreme_hot(main, extreme_heat_threshold):
            update_extreme_weather_days(extreme_weather_days, day, main['temp_max'], 'hot')
            days_mentioned.add(day)
        elif is_heavy_rain(weather, heavy_rain_threshold):
            update_extreme_weather_days(extreme_weather_days, day, forecast['rain']['3h'], 'rain')
            days_mentioned.add(day)
        elif is_heavy_snow(weather, heavy_snow_threshold):
            update_extreme_weather_days(extreme_weather_days, day, forecast['snow']['3h'], 'snow')
            days_mentioned.add(day)

    alerts = [construct_alerts(extreme_weather_days[category], lambda value, category=category: f"{value[0]} ({value[1]}{category.upper()})") for category in extreme_weather_days if extreme_weather_days[category]]

    if alerts:
        return "It will " + ', and '.join(alerts)
    else:
        return "Normal forecast for your current location"

# Function to send desktop notification
def send_notification(message):
    notification.notify(
        title="Weather Alert",
        message=message,
        timeout=1
    )

# Function to send email alert
def send_email_alert(weather_alert, config):

    email_sender = config['emailSender']
    email_password = config['emailPassword']
    email_recipient = config['emailRecipient']

    yag = yagmail.SMTP(email_sender, email_password)
    subject = "Weather Alert"
    content = weather_alert
    yag.send(email_recipient, subject, content)

# Function to send Discord alert
def send_discord_alert(weather_alert, config):

    bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
    discord_token = config['discordToken']
    discord_ID = config['discordUserID']

    @bot.event
    async def on_ready():
        user = bot.get_user(int(discord_ID))
        await user.send(weather_alert)
        await bot.close()

    bot.run(discord_token)

# Main function to execute the weather notification process
def main():
    with open("config.json") as config_file:
        config = json.load(config_file)

    api_key = config['WeatherAPI']
    EXTREME_COLD_THRESHOLD = config['cold']
    EXTREME_HEAT_THRESHOLD = config['heat']
    HEAVY_RAIN_THRESHOLD = config['rain']
    HEAVY_SNOW_THRESHOLD = config['snow']

    city, latitude, longitude = get_location()
    weather_data = get_weather_forecast(latitude, longitude, api_key)
    weather_alert = print_weather_alerts(weather_data, EXTREME_COLD_THRESHOLD, EXTREME_HEAT_THRESHOLD, HEAVY_RAIN_THRESHOLD, HEAVY_SNOW_THRESHOLD)

    if config.get('enable_notif_alert', True):
        send_notification(weather_alert)
        print('Desktop Notification successfully ran')

    if config.get('enable_email_alert', True):
        send_email_alert(weather_alert, config)
        print('Email successfully ran')

    if config.get('enable_discord_bot', True):
        send_discord_alert(weather_alert, config)
        print('Discord Bot successfully ran')

    # If none of the alerts are enabled, print the forecast
    if not any([config.get('enable_notif_alert', True), config.get('enable_email_alert', True), config.get('enable_discord_bot', True)]):
        print(weather_alert)

    time.sleep(config['notifFrequency'] * 3600)  # Sleep for the specified frequency in hours

if __name__ == "__main__":
    while True:
        main()
