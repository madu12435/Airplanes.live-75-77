import discord
from discord.ext import tasks
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Discord Bot Token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Discord Channel ID
CHANNEL_ID = 1165402020916760717

# Log file name
LOG_FILE = 'discord_logs.txt'

# Initialize the Discord client
client = discord.Client()

# Function to log messages to a file
def log_message(message):
    with open(LOG_FILE, 'a') as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {message}\n")

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print('Logged in as', client.user)

# Event triggered when a message is sent
@client.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID:
        log_message(f"{message.author}: {message.content}")

# Run the bot
client.run(TOKEN)