import settings
import datetime
import os
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await globals()
  await load_lore()

async def globals():
  myguild = bot.guilds[0]
  global events 
  events = await myguild.fetch_scheduled_events()
  global lores
  lores = []

async def load_lore():
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      lores.append(line.strip().lower())
  f.close()
  
@bot.command()
async def gaming(ctx, args = None):
  """Shows if we are playing this Sunday"""
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
      eventExists = True
      await ctx.channel.send('We are gaming this Sunday ' + str(m) + '/' + str(d))
  if not eventExists:
    await ctx.channel.send('We are not gaming this Sunday')

@bot.command()
async def lorelist(ctx, args = None):
  """Displays a list of all available lores"""
  loreMessage = ''
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      loreMessage += line
  f.close()
  await ctx.channel.send('**Here are the following lores:** ')
  await ctx.channel.send(loreMessage)
  await ctx.channel.send('**To get a lore, type !lore (name of lore)**')

@bot.command()
async def lore(ctx, arg):
  """Displays a lore snippit"""
  query = arg
  query = query.lower().strip()
  if query == 'list':
    await lorelist(ctx)
    return
  
  if query in lores:
    fileName = 'Lore_Snippits/' + query + '.png'
    await ctx.channel.send(file=discord.File(fileName))
  else:
    await ctx.channel.send('That is not a valid lore')

@bot.command()
async def help(ctx, args = None):
  helpMessage = (
    '**Here are the available commands:**\n\n'
    '!lore list: displays a list of lores\n'
    '!lore (name of lore): displays the lore\n'
    '!gaming: displays if we are gaming this Sunday'
  )
  await ctx.channel.send(helpMessage)


@lore.error
async def lore_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must provide a lore')
bot.run(settings.DISCORD_API_SECRET)