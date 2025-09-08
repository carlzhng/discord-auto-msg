import discord
from discord.ext import tasks
from flask import Flask
import asyncio
from threading import Thread
import os

# --------------------------
# Discord Bot Setup
# --------------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Load channel IDs (comma-separated list)
channel_id_str = os.environ.get("CHANNEL_ID_BTS")
if channel_id_str is None:
    raise ValueError("Environment variable CHANNEL_ID_BTS is not set!")

CHANNEL_IDS = [int(cid.strip()) for cid in channel_id_str.split(",")]

# Flag to control scheduled messages
scheduled_on = True

# --------------------------
# Scheduled Messages
# --------------------------
@tasks.loop(seconds=60)
async def send_message():
    if scheduled_on:
        for channel_id in CHANNEL_IDS:
            channel = client.get_channel(channel_id)
            if channel:
                await channel.send(
                    "crazy? I was crazy once. They locked me in a room. "
                    "A rubber room. A rubber room with rats, and the rats made me crazy."
                )

@client.event
async def on_ready():
    print(f"Bot is running! Logged in as {client.user}")
    if not send_message.is_running():
        send_message.start()

# --------------------------
# Flask Server Setup
# --------------------------
app = Flask(__name__)

def send_discord_message(text):
    for channel_id in CHANNEL_IDS:
        channel = client.get_channel(channel_id)
        if channel:
            asyncio.run_coroutine_threadsafe(channel.send(text), client.loop)
    return True

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/left-home")
def left_home():
    send_discord_message("Carl has left home!")
    return "Discord message sent!"

@app.route("/arrived-home")
def arrived_home():
    send_discord_message("Carl has arrived home!")
    return "Discord message sent!"

@app.route("/at-school")
def at-school():
    send_discord_message("Carl is in class at the University of Alberta!")
    return "Discord message sent!"
    
@app.route("/at-liquor")
def at-liquor():
    send_discord_message("Carl is at the liquor store...")
    return "Discord message sent!"

@app.route("/pause-scheduled")
def pause_scheduled():
    global scheduled_on
    scheduled_on = False
    return "Scheduled messages paused!"

@app.route("/resume-scheduled")
def resume_scheduled():
    global scheduled_on
    scheduled_on = True
    return "Scheduled messages resumed!"

@app.route("/status")
def status():
    return f"Scheduled messages are {'ON' if scheduled_on else 'OFF'}."

def run_flask():
    # Optimized for hosting
    app.run(host="0.0.0.0", port=8080)

# Run Flask in a separate thread
Thread(target=run_flask).start()

# --------------------------
# Run Discord Bot
# --------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
client.run(BOT_TOKEN)
