from round import Round

import discord
import json
import urllib3

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
        mention, command, *round_number = message.content.split(" ")
        if len(round_number) == 0:
            round_number = 10
        else:
            round_number = int(round_number[0])
        if command == "start":
            if 5 <= round_number <= 50:
                for round in rounds:
                    if round.channel == message.channel:
                        await message.channel.send("> Trivia is already started")
                        return
                data = http.request('GET', 'https://opentdb.com/api.php?amount={0}&type=multiple&encode=url3986'.format(round_number))
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
    else:
        for round in rounds:
            if round.channel == message.channel:
                if message.clean_content.isnumeric() and 0 < int(message.clean_content) < 5:
                    round.add_answer(message.author, message.clean_content)


client.run("")
