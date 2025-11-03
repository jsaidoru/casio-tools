import discord
from discord.ext import commands
from pathlib import Path

RESOURCE_PATH = Path(__file__).resolve().parent.parent / "resources" / "580vnx"
font_1byte = RESOURCE_PATH / "display_font_1byte.png"
font_2byte = RESOURCE_PATH / "display_font_2byte.png"

class fx_580VNX(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='display_font', help='Mở file bảng chữ 1 byte và 2 byte.')
    async def display_font(self, ctx):
        await ctx.send(files=[discord.File(fp=font_1byte), discord.File(fp=font_2byte)])

async def setup(bot):
    await bot.add_cog(fx_580VNX(bot))