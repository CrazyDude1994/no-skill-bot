from asyncio import sleep

from discord.ext import commands

from round import Round

import discord
import json
import urllib3
import os
import os.path

http = urllib3.PoolManager()

rounds = []

client = commands.Bot(command_prefix='$')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    for round in rounds:
        if round.channel == message.channel:
            if message.clean_content.isnumeric() and 0 < int(message.clean_content) < 5:
                round.add_answer(message.author, message.clean_content)
    await client.process_commands(message)


@client.command()
async def start(ctx, count=10):
    if 5 <= count <= 50:
        for round in rounds:
            if round.channel == ctx.message.channel:
                await ctx.message.channel.send("> Trivia is already started")
                return
        data = http.request('GET',
                            'https://opentdb.com/api.php?amount={0}&type=multiple&encode=url3986'.format(count))
        json_data = json.loads(data.data)
        rounds.append(Round(ctx.message.channel, json_data["results"], count))
    else:
        await ctx.message.channel.send("> Round count must be between 5-50")


@client.command()
async def stop(ctx):
    for round in rounds:
        if round.channel == ctx.message.channel:
            await ctx.message.channel.send("> Round has been stopped")
            round.task.cancel()
            rounds.remove(round)


@client.command()
async def play(ctx, name=None):
    if name is not None:
        if os.path.isfile("sounds/{0}.mp3".format(name)):
            vc = await ctx.message.author.voice.channel.connect()
            vc.play(discord.FFmpegPCMAudio("sounds/{0}.mp3".format(name)))
            while vc.is_playing():
                await sleep(1)
            await vc.disconnect()
    else:
        await ctx.message.channel.send("> Use play [sound]. Sounds available: `{0}`".format(
            " ".join([os.path.splitext(filename)[0] for filename in os.listdir("sounds")])))


client.run(os.environ["DISCORD_KEY"])
