import discord
from discord.ext import commands
import os
import hashlib
import json

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="c!", intents=intents)
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    try:
        await bot.load_extension('cogs.580vnx')
        await bot.load_extension('cogs.880btg')
        await bot.add_view(DownloadButton())
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    channel_id = message.channel.id
    if channel_id != 1424604740221796483 and message.content.startswith("c!") and message.author.id == 1085862271399493732:
        await message.channel.send("Không dùng bot ngoài <#1424604740221796483> !")
        return
    
    await bot.process_commands(message)

sniped_messages = {}
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    sniped_messages[message.channel.id] = {
        "content": message.content,
        "author": message.author,
        "time": message.created_at
    }

    if message.channel.id not in deleted_message_logs:
        deleted_message_logs[message.channel.id] = []
    deleted_message_logs[message.channel.id].append({
        "content": message.content,
        "author": message.author,
        "time": message.created_at
    })

    await asyncio.sleep(60)
    if sniped_messages.get(message.channel.id) and sniped_messages[message.channel.id]["content"] == message.content:
        del sniped_messages[message.channel.id]

    if message.channel.id in deleted_message_logs:
        deleted_message_logs[message.channel.id] = [
            msg for msg in deleted_message_logs[message.channel.id] if msg["content"] != message.content
        ]
        if not deleted_message_logs[message.channel.id]:
            del deleted_message_logs[message.channel.id]
            
@bot.command(name="snipe", help="Snipe tin nhắn vừa bị xoá")
async def snipe(ctx):
    snipe_data = sniped_messages.get(1424366374846726215)

    if snipe_data:
        time_diff = int((discord.utils.utcnow() - snipe_data["time"]).total_seconds())
        await ctx.send(
            f"# Tin nhắn bị xoá bởi **{snipe_data['author']}** ({time_diff} giây trước):\n---\n>>> {discord.utils.escape_mentions(snipe_data['content'])}"
        )
    else:
        await ctx.send("Làm gì có gì để snipe, bớt ảo tưởng đi má.")
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

@bot.command(name="memcount", help="Hiển thị số thành viên trong server")
async def memcount(ctx):
    member_count = ctx.guild.member_count
    await ctx.send(f"Server hiện đang có {member_count} thành viên.")
    
@bot.command(name="avatar", aliases=["av"], help="Lấy avatar của 1 user dựa vào ID")
async def avatar(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        avatar_url = user.display_avatar.url
        
        await ctx.send(f"Đã tìm thấy người dùng **{user.name}**\nAvatar URL: {avatar_url}")
    except discord.NotFound:
        await ctx.send("Không tìm thấy người dùng với ID đã cho.")
    except discord.HTTPException:
        await ctx.send("Đã xảy ra lỗi khi lấy avatar.")
    except ValueError:
        await ctx.send("ID không hợp lệ. Vui lòng chỉ sử dụng số.")


bot.remove_command('help')
@bot.command(name="help", aliases=["h"])
async def help(ctx, *, command_name: str = None):
    embed = discord.Embed(color=discord.Color.blurple())

    if command_name is None:
        # No args → show all commands grouped by cog
        embed.title = "📘 Help Menu"
        embed.description = "Sử dụng `c!help <lệnh>` để có thêm chi tiết về lệnh."

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

SECRET_SALT = "meowww~~~"
def make_version(counter: int):
    raw = f"{counter}:{SECRET_SALT}"
    return hashlib.md5(raw.encode()).hexdigest()
def load_data():
    with open("downloads.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("downloads.json", "w") as f:
        json.dump(data, f)
d
class DownloadButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Tải xuống", style=discord.ButtonStyle.primary)
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        uid = interaction.user.id

        if uid in data["users"]:
            await interaction.response.send_message(
                "❌ Mỗi user chỉ được click một lần.",
                ephemeral=True
            )
            return
        data["count"] += 1
        version_hash = make_version(data["count"])
        filename = f"ver_{version_hash}.txt"
        try:
            await interaction.user.send(
                content="File vẽ siêu ngắn:",
                file=discord.File("guide.txt", filename=filename)
            )
        except:
            await interaction.response.send_message(
                "❌ Vui lòng cho phép DMs hoặc unblock bot.",
                ephemeral=True
            )
            return
        data["users"].append(uid)
        save_data(data)

        await interaction.response.send_message(
            "✅ Vui lòng kiểm tra DMs.",
            ephemeral=True
        )

        owner = await bot.fetch_user(1085862271399493732)
        await owner.send(
            f"📥 Download\n"
            f"User: {interaction.user}\n"
            f"ID: {uid}\n"
            f"Version: {filename}"
        )
@bot.command()
async def installguide(ctx):
    if ctx.author.id != 1085862271399493732:
        return
    await ctx.send(
        "Bấm để tải:",
        view=DownloadButton()
    )

token = os.environ.get('BOT_TOKEN')
bot.run(token)