import discord
import os
import math
import time
import asyncio
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

async def start(message):
    while True:
        sonarr_queue = sonarr.get_queue()
        radarr_queue = radarr.get_queue()
        
        msg = ''
        if sonarr_queue['records']:
            queue = sonarr_queue['records']
            for item in queue:
                percentage = math.floor((item['size'] - item['sizeleft']) / item['size'] * 10)
                progressbar = get_progressbar(percentage)
                status = "Importing" if item['status'] == 'completed' else item['status'].capitalize()
                msg += f'{item["title"]}\n{progressbar} [{item["timeleft"]}] {status}\n\n'

        if radarr_queue['records']:
            queue = radarr_queue['records']
            for item in queue:
                percentage = math.floor((item['size'] - item['sizeleft']) / item['size'] * 10)
                progressbar = get_progressbar(percentage)
                status = "Importing" if item['status'] == 'completed' else item['status'].capitalize()
                msg += f'{item["title"]}\n{progressbar} [{item["timeleft"]}] {status}\n\n'
        
        if not msg:
            msg = '```No downloads in queue```'
        else:
            msg = '```' + msg + '```'
        
        await message.edit(content=msg)
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    async for message in channel.history(limit=200):
        if message.author == client.user:
            print("Found previous message")
            await start(message)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$start'):
        main_message = await message.channel.send('Starting...')

        await start(main_message)
    
    if message.content.startswith('$restart'):
        channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

        async for message in channel.history(limit=200):
            if message.author == client.user:
                print("Found previous message")
                await start(message)

client.run(os.getenv('DISCORD_TOKEN'))