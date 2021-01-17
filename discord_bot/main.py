import discord
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
from discord.utils import get
import requests
import json
#import youtube_dl
import time
import asyncio
#import ffmpeg
from weather import *
import os
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv()


DISCORD_API_KEY =os.getenv('DISCORD_API_KEY')
WEATHER_API_KEY =os.getenv('WEATHER_API_KEY')
command_prefix = '!'
client = discord.Client()
bot = Bot(command_prefix=command_prefix)
messages = joined = 0
ROLE = 'new'


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def member_join(member):
    global joined
    joined += 1
    for channel in member.server.channgels:
        if channel == "general":
            await channel.send(f""" Welcome to the server {member.mention}""")
    
@client.event
async def assign_role(member):
    role = get(member.guild.roles, name=ROLE)
    await member.add_roles(role)
    print(f"{member} was given role {role}")



async def update_stats():
    await client.wait_until_ready()
    global messages, joined

    while not client.is_closed():
        try:
            with open('stats.txt','a') as f:
                f.write(f"Time : {int(time.time())}, Messages: {messages}, Members joined:{joined}\n")

            messages = 0
            joined = 0

            await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

@client.event
async def on_member_update(before,after):
    n = after.nick
    if n:
        if n.lower().count('brent') > 0:
            last = before.nick
            if last:
                await after.edit(nick=last)
            else:
                await after.edit(nick='you cant be me')




@client.event
async def on_message(message):
    id = client.get_guild(798095841671249921)
    global messages 
    messages += 1
    channels = ['commands']
    bad_words = ['peanut','almond','walnut']

    for word in bad_words:
        if message.content.count(word) > 0:
            print('caught you talking about peanuts')
            await message.channel.purge(limit=1)

    if message.content == '!help':
        embed = discord.Embed(title='channel commands',description='list of commands',)
        embed.add_field(name='!hello',value='greets user')    
        embed.add_field(name='!users',value='prints number of users')
        await message.channel.send(content=None,embed=embed)
    if str(message.channel) in channels:

        if message.author == client.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        elif message.content == '!users':
            await message.channel.send(f""" # of members: {id.member_count}""")

        if message.author != client.user and message.content.startswith('w.'):
            if len(message.content.replace('w.', '')) >= 1:
                location = message.content.replace('w.', '').lower()
                url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=imperial'
                try:
                    data = parse_data(json.loads(requests.get(url).content)['main'])
                    await message.channel.send(embed=weather_message(data, location))
                    print(data)
                except KeyError:
                    await message.channel.send(embed=error_message(location))
# @client.command(name="join")
# async def join(ctx):
#     channel = ctx.author.voice.channel
#     voice = get(client.voice_clients, guild=ctx.guild)

#     if voice and voice.is_connected():
#         await voice.move_to(channel)
#     else:
#         voice = await channel.connect()


client.loop.create_task(update_stats())
client.run(DISCORD_API_KEY)
