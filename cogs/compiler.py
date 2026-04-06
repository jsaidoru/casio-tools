import discord
from discord.ext import commands
import subprocess
import os
import uuid

COMPILER_PATH = "fxesplus/580vnx_emu/compiler.py"
class Compiler(commands.Cog, name="Compiler"):
    def __init__(self, bot):
        self.bot = bot

    def extract_code(self, message: str) -> str:
        return message.replace("`", "")

    def run_compiler_from_file(self, code: str):
        temp_filename = f"temp_{uuid.uuid4().hex}.asm"
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            result = subprocess.run(
                f"python {COMPILER_PATH} -f hex < {temp_filename}",
                shell=True,
                capture_output=True,
                text=True
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            os.remove(temp_filename)

            if stderr:
                return f"⚠️ Lưu ý:\n```\n{stderr}\n```\n✅Output:\n```\n{stdout}\n```"
            if stdout:
                return f"✅ Output:\n```\n{stdout}\n```"

            return "❔ Không nhận được output."

        except Exception as e:
            try:
                os.remove(temp_filename)
            except Exception:
                pass
            return f"❌ Exception: `{e}`"

    @commands.command(name="comp")
    async def compile(self, ctx, *, text: str):
        text = text.replace("`", "")
        code = self.extract_code(text)

        if not code.strip():
            await ctx.send("❌ Không nhận được code.")
            return

        await ctx.send("⏳ Đang compile...")

        result = self.run_compiler_from_file(code)

        if len(result) < 1000:
            await ctx.send(result)
        else:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(result)
            await ctx.send("📄 Output quá dài:", file=discord.File("output.txt"))
async def setup(bot):
    await bot.add_cog(Compiler(bot))