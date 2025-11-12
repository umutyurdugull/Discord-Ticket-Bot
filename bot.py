import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()  # .env dosyasını yükle
# Bundan sonra .env kullanıcam token = "TOKENİ BURAYA YAZIN"
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot çalışıyor: {bot.user}")


@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    user = ctx.author
    channel_name = f"ticket-{user.name}"

    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if existing_channel:
        await ctx.send(f"{user.mention}, zaten açık bir ticketin var {existing_channel.mention} !")
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
    await ticket_channel.send(f"{user.mention}, ticket açtın! Birazdan yetkili gelir.")
    await ctx.send(f"{user.mention}, ticket kanalın oluşturuldu: {ticket_channel.mention}")

@bot.command()
async def close(ctx):
    if ctx.channel.name.startswith("ticket-"):
        await ctx.send("Ticket kapatılıyor...")
        await ctx.channel.delete()
    else:
        await ctx.send("Bu komut sadece ticket kanallarında kullanılabilir.")

bot.run(token)
