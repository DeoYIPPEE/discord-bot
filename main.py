import dotenv
import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
#import logging
from mcstatus import JavaServer as mcs

dotenv.load_dotenv()
TOKEN = str(os.getenv("DISCORD_TOKEN"))
#handler = logging.FileHandler(filename="discord.log", mode="a", encoding="utf-8")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

hashmap = {"True": True, "False": False}

embed_cycle = [discord.Embed(title="SERVER IS NOW ONLINE", color=discord.Color.green()), discord.Embed(title="SERVER IS OFFLINE", color=discord.Color.red())]

@bot.event
async def on_ready():
    print("Bot starting!")

    try:
        synced = await bot.tree.sync()
        print("SMP bot synced!")
    except Exception as e:
        print(f"An exception occurred while syncing the bot: {e}")

    try:
        statusChangeMessage.start()
    except Exception as e:
        print(f"An exception occurred while starting a task: {e}")
    
    global server_up_cache
    with open("up.txt", "r") as f:
        server_up_cache = hashmap[f.readline()]
        print(f"On load: server_up_cache = {server_up_cache}")

    channel = bot.get_channel(1502203891813716079)
    embed = discord.Embed(title="Bot is now online!", color=discord.Color.dark_green())
    await channel.send(embed=embed)

@tasks.loop(seconds = 30)
async def statusChangeMessage():
    try:
        server = mcs.lookup("vocation-publicity.gl.joinmc.link:25565")
        status = server.status(tries=5)
        server_up = True
    except Exception as e:
        if not "timed out" in f"{e}":
            server_up = False
    global server_up_cache
    global embed_cycle
    if server_up_cache != server_up:
        server_up_cache = server_up
        channel = bot.get_channel(1502203891813716079)
        embed = embed_cycle.next()
        with open("up.txt", "w") as f:
            f.write(str(server_up))
            print(f"Wrote {str(server_up)} to up.txt")
            print(f"server_up_cache = {server_up_cache}")
        await channel.send(embed=embed)
    

@bot.tree.command(name="status", description="Gets status of SMP") #, integration_types={bot.IntegrationType.user_install},contexts={bot.InteractionContextType.private_channel, discord.InteractionContextType.guild}
@app_commands.allowed_contexts(dms=True, private_channels=True, guilds=True)
async def status(ctx: discord.Interaction):
    try:
        server = mcs.lookup("networks-unbraided.gl.joinmc.link:25565")
        status = server.status()
        try:
            online_players = [i.name for i in status.players.sample]
            await ctx.response.send_message(f"The server is online with {status.players.online} players currently online. \nThe following players are currently online: `{''.join(online_players)}`")
        except TypeError:
            await ctx.response.send_message(f"The server is online but no one's online (T-T)")
    except Exception:
        await ctx.response.send_message(f"The server is offline.")
        user = await bot.fetch_user(1173455513288196127)
        try:
            await user.send('start server idiot')
        except Exception as e:
            print(f"User: {user}")
            print(f"An exception occurred: {e}")


bot.run(token=TOKEN)