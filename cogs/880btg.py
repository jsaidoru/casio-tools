import discord
from discord.ext import commands
from pathlib import Path

RESOURCE_PATH = Path(__file__).resolve().parent.parent / "resources" / "880btg"
font_1byte = RESOURCE_PATH / "display_font_1byte.png"
font_2byte = RESOURCE_PATH / "display_font_2byte.png"
token_table = RESOURCE_PATH / "token_table.png"

class fx_880BTG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='880', invoke_without_command=True)
    async def fx880btg(self, ctx):
        await ctx.send("Nhóm lệnh cho máy fx-880 BTG. Sử dụng `c!help 880` để xem các lệnh con.")

    @fx880btg.command(name='display_font', help='Mở file bảng chữ 1 byte và 2 byte.')
    async def display_font(self, ctx):
        await ctx.send(files=[
            discord.File(fp=font_1byte), 
            discord.File(fp=font_2byte)
            ])
    
    @fx880btg.command(name='token_table', help="Mở file bảng token.")
    async def _token_table(self, ctx):
        await ctx.send(files=[discord.File(fp=token_table)])
    ")

    @fx880btg.command(name='findguide', help="Tìm tài liệu liên quan đến fx-880BTG")
    async def findguide(self, ctx, *, keyword: str):
        found_messages = []
        channel = self.bot.get_channel(1424392139525328951)
        async for message in channel.history(limit=1000):
            if keyword.lower() in message.content.lower():
                found_messages.append(message)
        if found_messages:
            response = f"Tìm thấy {len(found_messages)} guide chứa cụm từ '{keyword}':\n"
            for msg in found_messages:
                response += f"- {msg.jump_url}\n"
        else:
            response = f"Không tìm thấy guide chứa cụm từ '{keyword}'."

        await ctx.send(response)

async def setup(bot):
    await bot.add_cog(fx_880BTG(bot))
