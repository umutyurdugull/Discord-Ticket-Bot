import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Senkronize edilen {len(synced)} adet Slash komutu bulundu.")
    except Exception as e:
        print(f"Slash komutları senkronizasyonunda hata oluştu: {e}")
    print(f"Bot çalışıyor: {bot.user} (ID: {bot.user.id})")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Gecikme süresi: {round(bot.latency * 1000)}ms")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount < 1:
        await ctx.send("Lütfen geçerli bir sayı girin (en az 1).")
        return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} adet mesaj temizlendi.", delete_after=5)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kullanmak için `Mesajları Yönet` iznine sahip olmalısınız.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Lütfen kaç mesaj silineceğini sayı olarak belirtin.")

@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    user = ctx.author
    channel_name = f"ticket-{user.name.lower().replace(' ', '-')}"
    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if existing_channel:
        await ctx.send(f"{user.mention}, zaten açık bir ticketin var {existing_channel.mention}!")
        return
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
    await ticket_channel.send(f"{user.mention}, Ticket Açıldı! Lütfen sorununuzu açıklayın. Birazdan bir yetkili sizinle ilgilenecektir.")
    await ctx.send(f"{user.mention}, ticket kanalın oluşturuldu: {ticket_channel.mention}", delete_after=10)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):
    if ctx.channel.name.startswith("ticket-"):
        await ctx.send("Ticket 5 saniye içinde kapatılıyor ve siliniyor...")
        await ctx.channel.delete(delay=5)
    else:
        await ctx.send("Bu komut sadece ticket- ile başlayan kanallarda kullanılabilir.")

@close.error
async def close_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu ticket'ı kapatmak için `Kanalları Yönet` iznine sahip olmalısınız.")

bot.run(token)
