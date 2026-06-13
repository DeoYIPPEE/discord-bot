import dotenv
import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
import json
from enum import Enum
from mcstatus import JavaServer as mcs
from functions.server_syncer import server_syncer


dotenv.load_dotenv()
TOKEN = str(os.getenv("DISCORD_TOKEN"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

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
    with open("data/up.json", "r") as f:
        server_up_cache = json.load(f)
        print(f"On load: server_up_cache = {server_up_cache}")

    channel = bot.get_channel(CHANNEL)
    embed = discord.Embed(title="Bot is now online!", color=discord.Color.dark_green())
    await channel.send(embed=embed)

    server_syncer()

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
            # "timed out" is only raised as an exception when the server is currently loading up. So, if this isn't found then the server must be offline
            if not "timed out" in str(e):
                up_list_changed[count] = False
        if up_list_changed[count] != server_up_cache[count]:
            server_up_cache[count] = up_list_changed[count]

            if server_up_cache[count]:
                forge_check = str(status.forge_data)
                embed = discord.Embed(title = f"SERVER {name} IS NOW ONLINE", description= f"The version is {'Forge ' if forge_check != 'None' else ''}{status.version.name}. Hop on!\nThe IP is `{ip}`", color=discord.Color.green())
            else:
                embed = discord.Embed(title = f"SERVER {name} IS NOW OFFLINE", color=discord.Color.red())
            channel = bot.get_channel(CHANNEL)
            await channel.send(embed=embed)
        count += 1
    with open("data/up.json", "w") as f:
        json.dump(server_up_cache, f)
        

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
            forge_check = f"{status.forge_data}"
            await ctx.response.send_message(f"The server {name.name} is online with {status.players.online} players currently online. \nThe following players are currently online: `{''.join(online_players)}`\nThe server version is `{'Forge ' if forge_check != 'None' else ''}{status.version.name}`\nThe IP is `{server_ip}`")
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