import dotenv
import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
# from discord.commands import option
import json
from enum import Enum
#import logging
from mcstatus import JavaServer as mcs

dotenv.load_dotenv()
TOKEN = str(os.getenv("DISCORD_TOKEN"))
#handler = logging.FileHandler(filename="discord.log", mode="a", encoding="utf-8")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
SERVER = "fall-workers.gl.joinmc.link:25565"

with open("data/servers.json", "r") as f:
    servers = json.load(f)
Names = Enum("Name", servers)

CHANNEL = 1502203891813716079
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
        server_up_cache = [True if i.replace("\n", "")=='True' else False for i in f.readlines()]
        print(f"On load: server_up_cache = {server_up_cache}")

    channel = bot.get_channel(CHANNEL)
    embed = discord.Embed(title="Bot is now online!", color=discord.Color.dark_green())
    await channel.send(embed=embed)

@tasks.loop(seconds = 30)
async def statusChangeMessage():

    global server_up_cache
    global servers
    up_list_changed = server_up_cache.copy()
    count = 0
    global embed_cycle
    for name, ip in servers.items():
        try:
            server = mcs.lookup(ip)
            status = server.status()
            up_list_changed[count] = True
        except Exception as e:
            if not "timed out" in str(e):
                up_list_changed[count] = False
        if up_list_changed[count] != server_up_cache[count]:
            server_up_cache[count] = up_list_changed[count]

            if server_up_cache[count]:
                embed = discord.Embed(title = f"SERVER {name} IS NOW ONLINE", description= f"The version is {status.version.name}. Hop on!", color=discord.Color.green())
            else:
                embed = discord.Embed(title = f"SERVER {name} IS NOW OFFLINE", color=discord.Color.red())
            channel = bot.get_channel(CHANNEL)
            await channel.send(embed=embed)
        count += 1
    with open("up.txt", "w") as f:
        temp = [f"{i}\n" for i in server_up_cache]
        temp[-1] = temp[-1].replace("\n", "")
        f.writelines(temp)
        

@bot.tree.command(name="status", description="Gets status of SMP") #, integration_types={bot.IntegrationType.user_install},contexts={bot.InteractionContextType.private_channel, discord.InteractionContextType.guild}
@app_commands.allowed_contexts(dms=True, private_channels=True, guilds=True)
# @option(name="Server name", description = "The name of the server whose status you want to check", required=True, choices=list(servers))
async def status(ctx: discord.Interaction, 
                 name: Names):
    try:
        server_ip = name.value
    except Exception as e:
        await ctx.response.send_message("That isn't a valid server!")
        return
    try:
        server = mcs.lookup(server_ip)
        status = server.status()
        try:
            online_players = [i.name for i in status.players.sample]
            await ctx.response.send_message(f"The server {name.name} is online with {status.players.online} players currently online. \nThe following players are currently online: `{''.join(online_players)}`\nThe server version is `{status.version.name}`")
        except TypeError:
            await ctx.response.send_message(f"The server {name.name} is online but no one's online (T-T)")
    except Exception as e:
        print(e)
        await ctx.response.send_message(f"The server {name.name} is offline.")
        user = await bot.fetch_user(1173455513288196127)
        try:
            await user.send(f'start server idiot\n\nServer name: `{name.name}`\nIP: `{name.value}`')
        except Exception as e:
            print(f"User: {user}")
            print(f"An exception occurred: {e}")
    

bot.run(token=TOKEN)