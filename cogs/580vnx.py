import discord
from discord.ext import commands
from pathlib import Path

RESOURCE_PATH = Path(__file__).resolve().parent.parent / "resources" / "580vnx"
font_1byte = RESOURCE_PATH / "display_font_1byte.png"
font_2byte = RESOURCE_PATH / "display_font_2byte.png"
token_table = RESOURCE_PATH / "token_table.png"

class fx_580VNX(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='580', invoke_without_command=True)
    async def fx580vnx(self, ctx):
        await ctx.send("Nhóm lệnh cho máy fx-580 VNX. Sử dụng `c!help 580` để xem các lệnh con.")

    @fx580vnx.command(name='display_font', help='Mở file bảng chữ 1 byte và 2 byte.')
    async def display_font(self, ctx):
        await ctx.send(files=[
            discord.File(fp=font_1byte), 
            discord.File(fp=font_2byte)
            ])

    @fx580vnx.command(name='token_table', help="Mở file bảng token.")
    async def _token_table(self, ctx):
        await ctx.send(files=[discord.File(fp=token_table)])

    def split_by_n_chars(self, s, n):
        return [s[i:i+n] for i in range(0, len(s), n)]

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
        ]

        # Normalize & split; remove any internal 23
        hex_bytes = self.split_by_n_chars(hex_string.replace(" ", ""), 2)
        hex_bytes = [b.upper() for b in hex_bytes if b and b.upper() != "23"]

        enterable = [b for b in hex_bytes if b in non_enterable]
        if len(enterable) >= 21:
            return "Quá nhiều byte để nhập vào 3 biến(tối đa 21 byte)"

        # Setup A/B/C
        A, B, C = "A=1.0000", "B=1.", "C=1."
        vars_list = [A, B, C]
        current = 0
        byte_count = 0
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
    
    @fx580vnx.command(name='hex_split', help="Tách hex vào các biến A, B, C.")
    async def hex_split(self, ctx, *, hex_string: str):
        await ctx.send("Lưu ý: Bot hiện chưa hỗ trợ các ký tự multibyte(như chữ tiếng Việt)")
        result = self.split_hex(hex_string)
        await ctx.send(f"```\n{result}\n```")
    @fx580vnx.command(name='findguide', help="Tìm tài liệu liên quan đến fx-580VN X")
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

    def calculate_nums(self, total, text):
        vietnamese_chars = "ẠẮẰẶẤẦẨẬẼẸẾỀỂỄỆỐỒỔỖỘỢỚỜỞỊỎỌỈỦŨỤỲÕắằặấầẩậẽẹếềểễệốồổỗỠƠộờởịỰỨỪỬơớƯÀÁÂÃẢĂẳẵÈÉÊẺÌÍĨỳĐứÒÓÔạỷừửÙÚỹỵÝỡưàáâãảăữẫèéêẻìíĩỉđựòóôõỏọụùúũủýợỮẲẴẪỶỸỴ"
        singlebyte_chars = "𝒙𝒚𝒛…▲▼▸₋$◁&𝑡ᴛₜₕ₅!\"#×%÷'()⋅+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[▫]^_−abcdefghijklmnopqrstuvwxyz{|}~├𝒊𝒆°ʳᵍ∠→∏⇒⌟≤≠≥√∫ᴀʙᴄₙ▶◀⁰¹²³⁴⁵⁶⁷⁸⁹₍₎₀₁₂ꜰɴᴘ𝗔𝗕𝗖𝗗𝗘𝗙𝗣▷∑𝛼𝛾𝜀𝜃𝜆𝜇𝜋𝜎𝜙ℓℏ▮▯₃＿𝐟𝐩𝐧𝝁𝐦𝐤𝐌𝐆𝐓𝐏𝐄𝐹ₚₑᴊᴋ₉Åₘɪ₄∟⟲↻ⁿ"
        all_chars = vietnamese_chars + singlebyte_chars
        for char in text:
            if char not in all_chars and char != " ":
                return "Phát hiện ký tự không hợp lệ. Nên hạn chế sử dụng ký tự đặc biệt vì bot rất dễ bị lỗi."
        
        vn_chars_amount = len([x for x in text if x in vietnamese_chars])
        en_chars_amount = len([x for x in text if x in singlebyte_chars])
        spaces_amount = len([x for x in text if x == " "])
        
        return total - (vn_chars_amount + spaces_amount)*2 - en_chars_amount
        
    @fx580vnx.command(name="calculatenums", help="Tính NUMS, dùng trong spell")
    async def calculatenums(self, ctx, *, text):
        error_msg = "Phát hiện ký tự không hợp lệ. Nên hạn chế sử dụng ký tự đặc biệt để bot không bị nhầm lẫn."
        mode100an = self.calculate_nums(34, text)
        mode160an = self.calculate_nums(60, text)
        mode164an = self.calculate_nums(64, text)
        if mode100an == error_msg or mode160an == error_msg or mode164an == error_msg:
            return await ctx.send(error_msg)
        
        await ctx.send(f"Chọn NUMS phù hợp với cách bạn đang spell.\n* 100an: {mode100an}\n* 160an: {mode160an}\n* 164an: {mode164an}\n Nếu tất cả các kết quả đều ra âm thì hết cứu")
async def setup(bot):
    await bot.add_cog(fx_580VNX(bot))
