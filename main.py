import os
import random
import json

import discord
import requests
from sqlitedict import SqliteDict

db_dict = SqliteDict('./my_db.sqlite', autocommit=True,
                     tablename='encouraging_bot')


def update_encouragement(encouraging_message):
    if 'encouragements' in db_dict.keys():
        encouragements = db_dict['encouragements']
        encouragements.append(encouraging_message)
        db_dict['encouragements'] = encouragements
    else:
        db_dict['encouragements'] = [encouraging_message]


def delete_encouragement(index):
    encouragements = db_dict['encouragements']
    if len(encouragements) > index:
        del encouragements[index]
    db_dict['encouragements'] = encouragements


client = discord.Client()

sad_words = [
    'sad',
    'depressed',
    'unhappy',
    'angry',
    'miserable',
    'depressing'
]

starter_encouragments = [
    'Chee up!',
    'Hang in there.',
    'You are a great person / bot!'
]

if 'responding' not in db_dict.keys():
    db_dict['responding'] = True


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if db_dict['responding']:
        options = starter_encouragments
        if 'encouragements' in db_dict.keys():
            options = options + db_dict['encouragements']

        if any(word in msg for word in sad_words):
            await message.channel.send(
                random.choice(options))

    if msg.startswith('$new'):
        encouraging_message = msg.split('$new ', 1)[1]
        update_encouragement(encouraging_message)
        await message.channel.send('New encouraging message added.')

    if msg.startswith('$del'):
        encouragements = []
        if 'encouragements' in db_dict.keys():
            index = int(msg.split('$del', 1)[1])
            delete_encouragement(index)
            encouragements = db_dict['encouragements']
        await message.channel.send(encouragements)

    if msg.startswith('$list'):
        encouragements = []
        if 'encouragements' in db_dict.keys():
            encouragements = db_dict['encouragements']
        await message.channel.send(encouragements)

    if msg.startswith('$responding'):
        value = msg.split('$responding ', 1)[1]
        if value.lower() == 'true':
            db_dict['responding'] = True
            await message.channel.send('Responding is on.')
        else:
            db_dict['responding'] = False
            await message.channel.send('Responding is off.')
client.run(os.getenv('e_bot_token'))
