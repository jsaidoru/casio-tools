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
        await bot.load_extension('cogs.880btg')
    except Exception as e:
        print(f"Error loading cogs or syncing commands: {e}")

@bot.event
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        error = error.original

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Lệnh không tồn tại! Dùng c!help để xem các lệnh.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"Bạn thiếu các quyền sau để chạy lệnh: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Tham số không hợp lệ. Vui lòng thử lại")
    else:
        await ctx.send(f"Lệnh gặp sự cố khi chạy: ```\n{str(error)}\n```")

token = os.environ.get('BOT_TOKEN')
bot.run(token)
