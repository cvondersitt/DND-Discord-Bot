import settings
import datetime
import os
import discord
import typing
from discord.ext import commands
from discord import app_commands


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await globals()
  await load_lore()
  # bot.tree.copy_global_to(guild=settings.GUILD_ID_DEV)
  await bot.tree.sync(guild=settings.GUILD_ID_DEV)

async def globals():
  global __MYGUILD__
  __MYGUILD__ = bot.guilds[0]
  global __EVENTS__
  __EVENTS__ = __MYGUILD__.fetch_scheduled_events()
  global __LORES__
  __LORES__ = [] # Populates with lores in load lores
async def load_lore():
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      __LORES__.append(line.strip().lower())
  f.close()

@bot.tree.command()
async def gaming(interaction: discord.Interaction):
  """Shows if we are playing this Sunday"""
  eventExists = False
  for event in __EVENTS__:
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
      await interaction.response.send_message('We are gaming this Sunday ' + str(m) + '/' + str(d))
  if not eventExists:
    await interaction.response.send_message('We are not gaming this Sunday')

@bot.tree.command()
async def lorelist(interaction: discord.Interaction):
  """Displays all available lores"""
  prefix = '**Here are the available lores:** \n'
  loreMessage = ''
  with open("Lore_Snippits/lores.txt", "r") as f:
    for line in f:
      loreMessage += line
  f.close()
  loreMessage = prefix + loreMessage + '\n**To get a lore, type !lore (name of lore)**'
  await interaction.response.send_message(loreMessage)

async def lore_autocomplete(
  interaction: discord.Interaction, 
  current: str
) -> typing.List[app_commands.Choice[str]]:
  data = []
  for l in __LORES__:
    if current.lower() in l.lower():
      data.append(app_commands.Choice(name=l, value=l))
  return data
  
@bot.tree.command()
@app_commands.autocomplete(lore=lore_autocomplete)
async def lore(interaction: discord.Interaction, lore: str):
  """Displays the inputted lore"""
  query = lore
  query = query.lower().strip()
  if query == 'list':
    await lorelist(interaction)
    return
  
  if query in __LORES__:
    fileName = 'Lore_Snippits/' + query + '.png'
    await interaction.response.send_message(file=discord.File(fileName))
  else:
    await interaction.response.send_message('That is not a valid lore')

@bot.tree.command()
async def help(interaction: discord.Interaction):
  """Displays the available commands"""
  helpMessage = (
    '**Here are the available commands:**\n\n'
    '/lorelist: displays a list of lores\n'
    '/lore (name of lore): displays the lore\n'
    '/gaming: displays if we are gaming this Sunday'
  )
  await interaction.response.send_message(helpMessage)

@lore.error
async def lore_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await interaction.response.send_message('You must provide a lore')

bot.run(settings.DISCORD_API_SECRET)