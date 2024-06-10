import discord
import os
import date

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):       
  if message.author == client.user:
    return

  if message.content.startswith('!gaming'):
    eventExists = False
    myguild = client.guilds[0]
    for event in myguild._scheduled_events:
      # ADD PARSER FOR DATE AND CHECK IF DATE IS THIS WEEK. IF EVENT EXISTS FOR THIS WEEK/NOT         CANCELLED, WE GAMING BOYS
      
    if eventExists:
      await message.channel.send('We are not gaming this Sunday') 
    else:
      await message.channel.send('We gaming boys')

# token = os.getenv('TOKEN')
token = 'MTI0OTczMTk3MzA1NzA4OTYwOQ.GVLQGx.-UmXT76rHvgTJJachz6plKptamcludkiz_QKrI'

if token is None:
  print('Please set the TOKEN environment variable.')
  exit(1)
client.run(token)