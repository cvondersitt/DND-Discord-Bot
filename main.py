import discord
import os
import datetime

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  myguild = client.guilds[0]
  global events 
  events = await myguild.fetch_scheduled_events()

@client.event
async def on_message(message):       
  if message.author == client.user:
    return

  if message.content.startswith('!gaming'):
    eventExists = False
    for event in events:
      monthOfEvent = 100 * event.start_time.month
      dayOfEvent = event.start_time.day
      dateEvent = monthOfEvent + dayOfEvent
      dayNow = datetime.date.today().day
      monthNow = 100 * datetime.date.today().month
      dateNow = dayNow + monthNow
      if dateNow >= (dateEvent - 7) and dateNow <= (dateEvent + 7) and event.status != 4:
        m = int(monthOfEvent / 100) 
        d = dayOfEvent
        await message.channel.send('We are gaming Sunday ' + str(m) + '/' + str(d))
      else:
        await message.channel.send('We are not gaming this Sunday')

token = os.getenv('TOKEN')
client.run(token)