import discord
import os
import math
import re
from discord.ext import tasks
from pyarr import SonarrAPI
from pyarr import RadarrAPI
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

sonarr = SonarrAPI(os.getenv('SONARR_URL'), os.getenv('SONARR_API_KEY'))
radarr = RadarrAPI(os.getenv('RADARR_URL'), os.getenv('RADARR_API_KEY'))

def get_progressbar(percentage):
    progressbar = ''
    for i in range(0, 10):
        if percentage > i:
            progressbar += '⣿'
        elif percentage == i:
            progressbar += '⣦'
        else:
            progressbar += '⣀'
    return progressbar

def append_message(message, queue):
    for item in queue:
        percentage = math.floor((item['size'] - item['sizeleft']) / item['size'] * 10)
        progressbar = get_progressbar(percentage)
        state = ' '.join(map(lambda x: x.capitalize(), re.findall('[a-zA-Z][^A-Z]*', item['trackedDownloadState'])))
        if item['trackedDownloadStatus'] == 'ok':
            message += f'{item["title"]}\n\u001b[0;32m{progressbar} [{item["timeleft"]}] \u001b[1;33m{state}\u001b[0;0m\n\n'
        else:
            message += f'{item["title"]}\n\u001b[0;32m{progressbar} [{item["timeleft"]}] \u001b[1;31m{state}\u001b[0;0m\n\n'
    return message

@tasks.loop(minutes=1)
async def edit_message(message):
    print("Updating message")

    sonarr_queue = sonarr.get_queue()
    radarr_queue = radarr.get_queue()
    
    msg = ''
    msg = append_message(msg, sonarr_queue['records'])
    msg = append_message(msg, radarr_queue['records'])
    
    if not msg:
        msg = '```No downloads in queue```'
    else:
        msg = '```ansi\n' + msg + '```'
    
    await message.edit(content=msg)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    async for message in channel.history(limit=200):
        if message.author == client.user:
            print("Found previous message")
            edit_message.start(message)

client.run(os.getenv('DISCORD_TOKEN'))