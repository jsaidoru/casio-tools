import discord
from discord.ext import commands
import os

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

def get_all_commands(cmd: commands.Command, parent=""):
    cmds = []
    qualified_name = f"{parent} {cmd.name}".strip()
    if isinstance(cmd, commands.Group):
        cmds.append((qualified_name, cmd.help))
        for sub in cmd.commands:
            cmds.extend(get_all_commands(sub, qualified_name))
    else:
        cmds.append((qualified_name, cmd.help))
    return cmds

bot.remove_command('help')
@bot.command(name="help")
async def help(ctx, *, command_name: str = None):
    embed = discord.Embed(color=discord.Color.blurple())

    if command_name is None:
        # No args → show all commands grouped by cog
        embed.title = "📘 Help Menu"
        embed.description = "Sử dụng `c!help lệnh` để có thêm chi tiết về lệnh."

        cog_commands = {}

        for cmd in ctx.bot.commands:
            if cmd.hidden:
                continue
            try:
                if not await cmd.can_run(ctx):
                        continue
            except commands.CommandError:
                continue

            cog = cmd.cog_name or "Chưa được phân loại"
            cog_commands.setdefault(cog, []).append(cmd)

        for cog, commands_list in cog_commands.items():
            value = ""
            for cmd in commands_list:
                if isinstance(cmd, commands.Group):
                    value += f"• `{cmd.name}` (nhóm lệnh)\n"
                else:
                    value += f"• `{cmd.name}`\n"

            embed.add_field(
                name=f"📂 {cog}", value=value or "Không tìm thấy lệnh.", inline=False
            )
        await ctx.send(embed=embed)
    else:
        cmd = ctx.bot.get_command(command_name)
        if cmd is None:
            await ctx.send(f"❌ Không tìm thấy lệnh `{command_name}`.")
            return

        embed.title = f"❓ Help: `{cmd.qualified_name}`"
        embed.description = cmd.help or "Không có mô tả."

        if isinstance(cmd, commands.Group) and cmd.commands:
            value = ""
            for sub in cmd.commands:
                value += (
                     f"• `{cmd.name} {sub.name}` - {sub.help or 'Không có mô tả'}\n"
                )
            embed.add_field(name="Subcommands", value=value, inline=False)

        await ctx.send(embed=embed)
token = os.environ.get('BOT_TOKEN')
bot.run(token)
