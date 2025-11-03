import discord
import os

from discord.ext import commands
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="c!", intents=intents)
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    try:
        await bot.load_extension('cogs.580vnx')
    except Exception as e:
        print(f"Error loading cogs or syncing commands: {e}")

token = os.environ.get('BOT_TOKEN')
bot.run(token)