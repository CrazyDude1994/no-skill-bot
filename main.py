from asyncio import sleep

from round import Round

import discord
import json
import urllib3
import os
import os.path

http = urllib3.PoolManager()

client = discord.Client()

rounds = []


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user in message.mentions:
        mention, command, *param = message.content.split(" ")
        if command == "start":
            if len(param) == 0:
                param = 10
            else:
                param = int(param[0])
            if 5 <= param <= 50:
                for round in rounds:
                    if round.channel == message.channel:
                        await message.channel.send("> Trivia is already started")
                        return
                data = http.request('GET', 'https://opentdb.com/api.php?amount={0}&type=multiple&encode=url3986'.format(param))
                json_data = json.loads(data.data)
                rounds.append(Round(message.channel, json_data["results"], rounds))
            else:
                await message.channel.send("> Round count must be between 5-50")
        elif command == "stop":
            for round in rounds:
                if round.channel == message.channel:
                    await message.channel.send("> Round has been stopped")
                    round.task.cancel()
                    rounds.remove(round)
        elif command == "play" and len(param) != 0:
            param = param[0]
            if os.path.isfile("sounds/{0}.mp3".format(param)):
                vc = await message.author.voice.channel.connect()
                vc.play(discord.FFmpegPCMAudio("sounds/{0}.mp3".format(param)))
                while vc.is_playing():
                    await sleep(1)
                await vc.disconnect()
    else:
        for round in rounds:
            if round.channel == message.channel:
                if message.clean_content.isnumeric() and 0 < int(message.clean_content) < 5:
                    round.add_answer(message.author, message.clean_content)


client.run(os.environ["DISCORD_KEY"])