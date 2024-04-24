Evren Acar - 04/02/2024
Python Weather Bot - WeatherNotification.py
Last Updated: 04/22/2024

# WeatherAlertPyv2 Description
Python-based weather app that sends alerts to you (via Discord, Email, and/or Desktop Notification) every 12 (Hours changeable) hour based on your current location (location data pulled with ipinfo.io) using OpenWeatherMap API. All values are configurable via the config.json file included.

# You must have the config.json file in the same place as this python file to run the code

# REQUIRED PIP INSTALLS
pip install requests (To get the forecast)
pip install plyer (for Desktop notifications)
pip install yagmail (For Email notifications)
pip install discord.py (For Discord notifications)

# Config.json instructions
"discordToken": "", (In the double quotes paste your Discord Bot Token)
"discordUserID": , (right before the , paste the user ID you want to receive the Discord DM)
"emailPassword": "", (In the double quotes paste your Bot emails application password)
"emailSender": "", (In the double quotes paste your bot email you want to send the weather alert)
"emailRecipient": "", (In the double quotes paste the email you want to alert to be sent to)
"WeatherAPI": "", (In the double quotes paste your OpenWeatherMap API Key)
"rain": , (right before the , type the value you want the rain alert to trigger at Default is 45(mm every 3 hours))
"snow": , (right before the , type the value you want the snow alert to trigger at Default is 25 (mm every 3 hours))
"heat": , (right before the , type the value you want the heat alert to trigger at Default is 30 (c))
"cold": , (right before the , type the value you want the cold alert to trigger at Default is 0 (c))
"notifFrequency": 12 (right before the , type the rate you want the alerts to be sent default is 12 (hours))
