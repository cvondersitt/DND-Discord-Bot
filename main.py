import datetime
import os
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await globals()
  await load_lore()

async def globals():
  myguild = client.guilds[0]
  global events 
  events = await myguild.fetch_scheduled_events()
  global lores
  lores = []

async def load_lore():
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      lores.append(line.strip().lower())
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
      eventExists = True
      await message.channel.send('We are gaming this Sunday ' + str(m) + '/' + str(d))
  if not eventExists:
    await message.channel.send('We are not gaming this Sunday')
    
async def lore_help(message):
  loreMessage = ''
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      loreMessage += line
  f.close()
  await message.channel.send('**Here are the following lores:** ')
  await message.channel.send(loreMessage)
  await message.channel.send('**To get a lore, type !lore (name of lore)**')

async def lore_command(message):
  query = message.content[6:]
  query = query.lower().strip()
  print(query)
  if query in lores:
    fileName = 'Lore_Snippits/' + query + '.png'
    await message.channel.send(file=discord.File(fileName))
  else:
    await message.channel.send('That is not a valid lore')

async def help_command(message):
  await message.channel.send('**Here are the following commands:** ')
  await message.channel.send('!lore help: displays a list of lores')
  await message.channel.send('!lore (name of lore): displays the lore')
  await message.channel.send('!gaming: displays if we are gaming this Sunday')
  
@bot.event
async def on_message(message):       
  if message.author == client.user:
    return

  if message.content.startswith('!gaming'):
    await gaming_command(message)
    
  if message.content.startswith('!help'):
    await help_command(message)
    
  if message.content == '!lore help' or message.content == '!lore':
    await lore_help(message)
    
  if message.content.startswith('!lore') and \
    message.content != '!lore help' and \
    message.content != '!lore': 
    await lore_command(message)

token = os.environ['TOKEN']
bot.run(token)