import os
import datetime
import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  myguild = client.guilds[0]
  global events 
  events = await myguild.fetch_scheduled_events()
  global lores
  lores = []
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      lores.append(line.strip())
  f.close()

async def gaming_command(message):
  eventExists = False
  for event in events:
    monthOfEvent = 100 * event.start_time.month
    dayOfEvent = event.start_time.day
    dateEvent = monthOfEvent + dayOfEvent
    dayNow = datetime.date.today().day
    monthNow = 100 * datetime.date.today().month
    dateNow = dayNow + monthNow
    print(dateNow)
    print(dateEvent)
    if dateNow >= (dateEvent - 7) and dateNow <= (dateEvent + 7) and event.status != 4:
      m = int(monthOfEvent / 100) 
      d = dayOfEvent
      await message.channel.send('We are gaming Sunday ' + str(m) + '/' + str(d))
    else:
      await message.channel.send('We are not gaming this Sunday')

async def lore_help(message):
  await message.channel.send('Here are the following lores: ')
  await message.channel.send(file=discord.File('Lore_Snippits/lores.txt'))
  await message.channel.send('To get a lore, type !lore (name of lore)')

async def lore_command(message):
  if message.content[6:] in lores:
    fileName = 'Lore_Snippits/' + message.content[6:] + '.png'
    await message.channel.send(file=discord.File(fileName))
  else:
    await message.channel.send('That is not a valid lore')

@client.event
async def on_message(message):       
  if message.author == client.user:
    return

  if message.content.startswith('!gaming'):
    await gaming_command(message)

  if message.content == '!lore help' or message.content == '!lore':
    await lore_help(message)
    
  if message.content.startswith('!lore') and \
    message.content != '!lore help' and \
    message.content != '!lore': 
    await lore_command(message)
    
token = os.getenv('TOKEN')
token = 'MTI0OTczMTk3MzA1NzA4OTYwOQ.GOB3aZ.OjM6UHScXmPIqo-NTEqP8bqUqLCY5zB4t7IKaI'
client.run(token)