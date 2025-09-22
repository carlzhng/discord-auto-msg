import discord
from discord.ext import tasks
from flask import Flask
import asyncio
from threading import Thread
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

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

# Flags to control functionality
scheduled_on = False  # Meme messages paused by default
daily_check_on = True  # Daily home check enabled by default
at_home = True  # Tracks whether Carl is currently home

# --------------------------
# Scheduled Meme Messages
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

# --------------------------
# Daily Home Check (10 PM local)
# --------------------------
@tasks.loop(time=time(22, 0, 0, tzinfo=ZoneInfo("America/Edmonton")))
async def daily_home_check():
    if daily_check_on:
        if not at_home:
            for channel_id in CHANNEL_IDS:
                channel = client.get_channel(channel_id)
                if channel:
                    await channel.send("Carl is NOT home by 10 PM!")

@daily_home_check.before_loop
async def before_daily_home_check():
    await client.wait_until_ready()

# --------------------------
# Discord Events
# --------------------------
@client.event
async def on_ready():
    print(f"Bot is running! Logged in as {client.user}")
    if not send_message.is_running():
        send_message.start()
    if not daily_home_check.is_running():
        daily_home_check.start()

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
    global at_home
    at_home = False
    send_discord_message("Carl has left home!")
    return "Discord message sent!"

@app.route("/arrived-home")
def arrived_home():
    global at_home
    at_home = True
    send_discord_message("Carl has arrived home!")
    return "Discord message sent!"

@app.route("/at-school")
def at_school():
    send_discord_message("Carl is in class at the University of Alberta!")
    return "Discord message sent!"
    
@app.route("/at-liquor")
def at_liquor():
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
    return f"Scheduled messages are {'ON' if scheduled_on else 'OFF'}. Daily check is {'ON' if daily_check_on else 'OFF'}. Currently {'HOME' if at_home else 'AWAY'}."

@app.route("/pause-daily")
def pause_daily():
    global daily_check_on
    daily_check_on = False
    return "Daily home check paused!"

@app.route("/resume-daily")
def resume_daily():
    global daily_check_on
    daily_check_on = True
    return "Daily home check resumed!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Run Flask in a separate thread
Thread(target=run_flask).start()

# --------------------------
# Run Discord Bot
# --------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
client.run(BOT_TOKEN)
