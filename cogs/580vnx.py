import discord
from discord.ext import commands
from pathlib import Path
from PIL import Image
import os
import uuid
import numpy as np

RESOURCE_PATH = Path(__file__).resolve().parent.parent / "resources" / "580vnx"
font_1byte = RESOURCE_PATH / "display_font_1byte.png"
font_2byte = RESOURCE_PATH / "display_font_2byte.png"
token_table = RESOURCE_PATH / "token_table.png"

TEMP_FOLDER_PATH = Path("/tmp")
class fx_580VNX(commands.Cog, name=""):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='580', invoke_without_command=True)
    async def fx580vnx(self, ctx):
        await ctx.send("Nhóm lệnh cho máy fx-580 VNX. Sử dụng `c!help 580` để xem các lệnh con.")

    @fx580vnx.command(name='displayfont', aliases=["dispfont", "df"], help='Mở file bảng chữ 1 byte và 2 byte(tiếng Việt).')
    async def display_font(self, ctx):
        await ctx.send(files=[
            discord.File(fp=font_1byte), 
            discord.File(fp=font_2byte)
            ])

    @fx580vnx.command(name='tokentable', aliases=["token", "tt"], help="Mở file bảng token.")
    async def _token_table(self, ctx):
        await ctx.send(files=[discord.File(fp=token_table)])

    def split_bytes(self, hex_string):
        if len(hex_string) % 2 != 0:
            return False

        i = 0
        bytes = []
        while i < len(hex_string):
            byte_1 = hex_string[i:i+2]
            if byte_1.startswith("F"):
                byte_2 = hex_string[i+2:i+4]
                bytes.append(byte_1 + byte_2)
                i += 4
            else:
                byte_1 = hex_string[i:i+2]
                bytes.append(byte_1)
                i+=2

        return bytes

    def split_hex(self, hex_string: str):
        non_enterable = [
            "00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F",
            "10","11","12","13","14","15","16","17","18","19","1A","1B","1C","1D","1E","1F",
            "24","25","26","27","28","29","2A","2B","2F",
            "3A","3B","3C","3D","3E","3F",
            "4C","4D","4E","4F",
            "54","55","56","57","58","59","5A","5B","5C","5D","5E","5F",
            "61","62","63","64","65","66","67","6A","6B",
            "80","81","82","85","86","8A","8B","8C","8D","8E","8F",
            "90","91","92","93","94","95","96","97","98","99","9A","9B","9C","9D","9E","9F",
            "A0","A1","A2","A3","A4","AB","AC","AF",
            "B0","B1","B2","B3","B4","B5","B6","B7","B8","B9","BA","BB","BC","BD","BE","BF",
            "C1","C2","C3","C4","C5","C6","C7","CB","CC","CD","CE","CF",
            "D0","D1","D2","D3",
            "E8","E9","EA","EB","EC","ED","EE","EF"
        ] + [f"{i:04X}" for i in range(int("F000", 16), int("10000", 16)) if i not in ["FD30", "FD31", "FD32", "FD33", "FD34", "FD35", "FD36", "FD37", "FD38", "FD39", "FD3A", "FD3B", "FD3C", "FD3D", "FD3E", "FD3F",
  "FD40", "FD41", "FD42", "FD43", "FD44", "FD45", "FD46", "FD47", "FD48", "FD49", "FD4A", "FD4B", "FD4C", "FD4D", "FD4E", "FD4F",
  "FD50", "FD51", "FD52", "FD53", "FD54", "FD55", "FD56", "FD57", "FD58", "FD59", "FD5A", "FD5B", "FD5C", "FD5D", "FD5E",
  "FE01", "FE02", "FE03", "FE04", "FE05", "FE06", "FE07", "FE08", "FE09", "FE0A", "FE0B", "FE0C", "FE0E", "FE0E", "FE0F",
  "FE10", "FE11", "FE12", "FE13", "FE14", "FE15", "FE16", "FE17", "FE18", "FE19", "FE1A", "FE1B", "FE1C", "FE1E", "FE1E", "FE1F",
  "FE20", "FE21", "FE22", "FE23", "FE24", "FE25", "FE26", "FE27", "FE28"
]]

        

        # Normalize & split; remove any internal 23
        hex_bytes = self.split_bytes(hex_string.replace(" ", "").replace("\n", "").upper())
        hex_bytes = [b.upper() for b in hex_bytes if b and b.upper() != "23"]

        enterable = []
        for i, byte in enumerate(hex_bytes):
            if byte not in non_enterable:
                continue
        
            if len(byte) == 4:
                if i in (4, 12) and any(ch in "ABCDEF" for ch in byte[2:]):
                    enterable.append("20")
                enterable.append(byte[:2])
                enterable.append(byte[2:])
            else:
                enterable.append(byte)
        if len(enterable) >= 21:
            return "Quá nhiều byte để nhập vào 3 biến(tối đa 21 byte)"

        A, B, C = "A=1.0000", "B=1.", "C=1."
        vars_list = [A, B, C]
        current = 0
        byte_count = 2
        calc_bytes = []

        for byte in enterable:
            if current >= len(vars_list):
                break

            if byte_count == 7:
                # last slot for this variable
                if any(ch in "ABCDEF" for ch in byte):
                    vars_list[current] += "x10^x20:"
                    calc_bytes.append("20")
                    current += 1
                    if current < len(vars_list):
                        vars_list[current] += byte
                        calc_bytes.append(byte)
                        byte_count = 1
                    else:
                        # no next var; just record byte for calc_hex
                        calc_bytes.append(byte)
                        byte_count = 0
                else:
                    vars_list[current] += f"x10^x{byte}:"
                    calc_bytes.append(byte)
                    current += 1
                    byte_count = 0
            else:
                vars_list[current] += byte
                calc_bytes.append(byte)
                byte_count += 1

        used = [v for v in vars_list if not (v == "A=1.0000" or v == "B=1." or v == "C=1.")]
        if used:
            used[-1] = used[-1] + "23"
            formatted_result = "\n".join(used)
        else:
            formatted_result = ""

        return formatted_result
    
    @fx580vnx.command(name='hexsplit', aliases=["split", "hs"], help="Tách hex vào các biến A, B, C.")
    async def hex_split(self, ctx, *, hex_string: str):
        result = self.split_hex(hex_string)
        await ctx.send(f"```\n{result}\n```")
        
    @fx580vnx.command(name='findguide', aliases=["find", "fg"], help="Tìm tài liệu liên quan đến fx-580VN X")
    async def findguide(self, ctx, *, keyword: str):
        found_messages = []
        channel = self.bot.get_channel(1424392041735127080)
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

    def translate_hex(self, hex_string: str):
        singlebyte_table =[
    "@", "<01>", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@",
    "@", "@", "@", "@", "@", "@", "@", "@", "@", "▯", "@", "@", "@", "@", "@", "@",
    "𝒊", "𝒆", "𝜋", ":", "$", "?", "@", "@", "@", "@", "@", "@", ",", "x10", ".", "@",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "𝗔", "𝗕", "𝗖", "𝗗", "𝗘", "𝗙",
    "M", "Ans", "A", "B", "C", "D", "E", "F", "𝒙", "𝒚", "PreAns", "𝒛", "𝜃", "@", "@", "@",
    "∑(", "∫(", "d/d𝒙(", "∏(", "@", "@", "@", "@", "Min(", "Max(", "Mean(", "Sum(", "@", "@", "@", "@",
    "(", "P(", "Q(", "R(", "Not(", "Neg(", "Conjg(", "Arg(", "Abs(", "Rnd(", "Det(", "Trn(", "sinh(", "cosh(", "tanh(", "sinh⁻¹(",
    "cosh⁻¹(", "tanh⁻¹(", "𝒆^(", "10^(", "√(", "ln(", "³√(", "sin(", "cos(", "tan(", "sin⁻¹(", "cos⁻¹(", "tan⁻¹(", "log(", "Pol(", "Rec(",
    "@", "@", "@", "Int(", "Intg(", "Ref(", "Rref(", "RanInt#(", "GCD(", "LCM(", "RndFix(", "@", "@", "@", "@", "ReP(",
    "ImP(", "Identity(", "UnitV(", "Angle(", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@", "@",
    "or", "xor", "xnor", "and", "@", "=", "+", "-", "×", "÷", "÷R", "⋅", "∠", "𝗣", "𝗖", "@",
    "@", "@", "@", "@", "@", "@", "@", "@", "x̂", "ŷ", "x̂₁", "x̂₂", "@", "@", "@", "@",
    "−", "b", "o", "d", "h", "@", "@", "@", "⌟", "^(", "ˣ√(", "@", "@", "@", "@", "@",
    ")", "▸t", "▸a+b𝒊", "▸r∠𝜃", "⁻¹", "²", "³", "%", "!", "°", "ʳ", "ᵍ", "▫", "𝐄", "𝐏", "𝐓",
    "E", "𝐆", "𝐌", "𝐤", "𝐦", "𝝁", "𝐧", "𝐩", "𝐟", "@", "▸Simp", "@", "@", "@", "@", "@"
]
        hex_bytes = self.split_bytes(hex_string.replace(" ", "").replace("\n", "").upper())
        tokens = []
        for byte in hex_bytes:
            if len(byte) == 4:
                tokens.append(f"<{byte}>")
            else:
                decimal_byte = int(byte, 16)
                token = singlebyte_table[decimal_byte]
                tokens.append(token)
        return " ".join(tokens)

    @fx580vnx.command(name="translatehex", help="Dịch hex sang token")
    async def translatehex(self, ctx, *,  hex_string: str):
        token = self.translate_hex(hex_string)
        await ctx.send(f"```\n{token}```")

    def txtbits_to_image(self, path_txt, width, height):
        with open(path_txt, "r") as f:
            hex_data = f.read().replace(" ", "").replace("\n", "")
        
        data = bytes.fromhex(hex_data)

        bits = []
        for b in data:
            for i in range(7, -1, -1):
                bits.append((b >> i) & 1)
    
        # limit to the image size
        bits = bits[:width * height]

        # Convert 1=black, 0=white
        pixels = (1 - np.array(bits, dtype=np.uint8)) * 255
        pixels = pixels.reshape((height, width))

        img = Image.fromarray(pixels, mode="L")
        return img

    @fx580vnx.command(name="p2b", help="Dịch tranh sang hex để inject. p2b là viết tắt của \"picture to bitmap")
    async def p2b(self, ctx):
        uid = uuid.uuid4()

        if len(ctx.message.attachments) == 0:
            return await ctx.send("```Vui lòng chọn một bức ảnh.```")

        img_path = TEMP_FOLDER_PATH / f"image_{uid}.png"
        hex_path = TEMP_FOLDER_PATH / f"heximage_{uid}.txt"
        hex_png_path = TEMP_FOLDER_PATH / f"heximagepng_{uid}.png"

        attachment = ctx.message.attachments[0]
        await attachment.save(img_path)

        image = Image.open(img_path).convert("L")
        image = image.resize((192,63))  # fx-580 screen resolution
        w, h = image.size
        pixels = image.load()
        hex_list = []

        for y in range(h):
            byte = 0
            bit_index = 0
            for x in range(w):
                val = pixels[x, y]
                bit = 0 if val >= 128 else 1
                byte = (byte << 1) | bit
                bit_index += 1

                if bit_index == 8:
                    hex_list.append(f"{byte:02X}")
                    byte = 0
                    bit_index = 0

            if bit_index != 0:
                byte <<= (8 - bit_index)
                hex_list.append(f"{byte:02X}")

        with open(hex_path, "w", encoding="utf-8") as f:
            f.write(" ".join(hex_list))
        
        hex_png = self.txtbits_to_image(hex_path, width=192, height=63)
        hex_png = hex_png.resize((384, 189), Image.NEAREST)
        hex_png = hex_png.convert("1")

        hex_png.save(hex_png_path)

        await ctx.send(files=[discord.File(fp=hex_png_path), discord.File(fp=hex_path)])

    # cleanup
        os.remove(img_path)
        os.remove(hex_path)
        os.remove(hex_png_path)
    
async def setup(bot):
    await bot.add_cog(fx_580VNX(bot))
