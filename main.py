import os
import discord
from discord.ext import commands
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import requests
from flask import Flask
from threading import Thread

# --- Flask Web Server for UptimeRobot ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def time(ctx, *, city: str):
    try:
        geocode_url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key=749f2587cfd2459bb0be4b348a07fbdc'
        response = requests.get(geocode_url)
        data = response.json()

        if data['results']:
            coordinates = data['results'][0]['geometry']
            lat, lng = coordinates['lat'], coordinates['lng']
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lng=lng, lat=lat)

            if timezone_str:
                timezone = pytz.timezone(timezone_str)
                city_time = datetime.now(timezone)
                await ctx.send(f'The current time in {city.title()} is {city_time.strftime("%Y-%m-%d %H:%M:%S")}')
            else:
                await ctx.send(f'Timezone not found for {city.title()}.')
        else:
            await ctx.send('City not found. Please try another city or check your spelling.')
    except Exception as e:
        await ctx.send('An error occurred: ' + str(e))

# --- Run the bot ---
keep_alive()
bot.run(os.getenv("TOKEN"))
