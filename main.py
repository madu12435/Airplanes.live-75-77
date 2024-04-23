import discord
from discord.ext import tasks
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Discord Bot Token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Discord Channel ID
CHANNEL_ID = 1165402020916760717

# Initialize the Discord client
client = discord.Client()

# Initialize the airplanes.live API endpoint
AIRPLANES_LIVE_API = "http://api.airplanes.live/v2/squawk/"

# Set to track sent messages
sent_messages = set()

# Function to fetch data from airplanes.live API
def fetch_aircraft_data(squawk):
    url = f"{AIRPLANES_LIVE_API}{squawk}"
    response = requests.get(url)
    return response.json()

# Function to format message
def format_message(aircraft, squawk):
    hex_code = aircraft.get('hex')
    flight = aircraft.get('flight', '').strip()
    aircraft_type = aircraft.get('t', 'Unknown Type')
    altitude = aircraft.get('alt_baro', 'Unknown Altitude')
    ground_speed = aircraft.get('gs', 'Unknown Speed')
    # Check if lat and lon are available
    if 'lastPosition' in aircraft and 'lat' in aircraft['lastPosition'] and 'lon' in aircraft['lastPosition']:
        lat = aircraft['lastPosition']['lat']
        lon = aircraft['lastPosition']['lon']
        url = f"https://globe.adsbexchange.com/?icao={hex_code}&lat={lat}&lon={lon}&zoom=13.5&showTrace={datetime.utcnow().strftime('%Y-%m-%d')}&timestamp={datetime.utcnow().timestamp()}"
    else:
        url = f"https://globe.adsbexchange.com/?icao={hex_code}&zoom=13.5&showTrace={datetime.utcnow().strftime('%Y-%m-%d')}&timestamp={datetime.utcnow().timestamp()}"
    alert_messages = {
        '7500': 'Hijacking',
        '7600': 'Communication Failure',
        '7700': 'Emergency'
    }
    emergency_type = alert_messages.get(squawk, 'Unknown Emergency')
    return f"🚨 Airplanes.live Alert: {flight} \n✈️ SQUAWK {squawk} ({emergency_type})\n🌐 {url}\n⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"

# Background task to continuously check for squawks
@tasks.loop(seconds=60)
async def check_squawks():
    squawks = ['7500', '7600', '7700']  # Change to the squawk codes you want to check
    for squawk in squawks:
        data = fetch_aircraft_data(squawk)
        if data.get('total', 0) > 0:
            for aircraft in data.get('ac', []):
                hex_code = aircraft.get('hex')
                # Check if the message for this tail number has already been sent
                if hex_code not in sent_messages:
                    message = format_message(aircraft, squawk)
                    channel = client.get_channel(CHANNEL_ID)
                    await channel.send(message)
                    # Add to sent_messages to prevent duplicates
                    sent_messages.add(hex_code)
        else:
            print(f"No aircraft found squawking {squawk}.")
    # Purge sent messages set periodically
    if datetime.utcnow().hour % 6 == 0:  # Purge every 6 hours
        sent_messages.clear()

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print('Logged in as', client.user)
    check_squawks.start()

# Run the bot
client.run(TOKEN)
