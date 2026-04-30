import dotenv
import os
import discord
import logging
from mcstatus import JavaServer as mcs

dotenv.load_dotenv()
TOKEN = str(os.getenv("DISCORD_TOKEN"))

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print("Bot starting!")

@bot.command(name="status", description="Gets status of SMP", integration_types={discord.IntegrationType.user_install},contexts={discord.InteractionContextType.private_channel, discord.InteractionContextType.guild})
async def status(ctx):
    try:
        server = mcs.lookup("vocation-publicity.gl.joinmc.link:25565")
        status = server.status()

        await ctx.respond(f"The server is online with {status.players.online} players currently online")
    except Exception:
        await ctx.respond(f"The server is offline.")
        user = await bot.fetch_user(1173455513288196127)
        try:
            await user.send('start server idiot')
        except Exception as e:
            print(f"User: {user}")
            print(f"An exception occurred: {e}")


bot.run(token=TOKEN)