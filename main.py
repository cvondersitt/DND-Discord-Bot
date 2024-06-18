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

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await initialize_globals()
    await load_lore()
    bot.tree.copy_global_to(guild=settings.GUILD_ID_DEV)
    await bot.tree.sync(guild=settings.GUILD_ID_DEV)

# Global variables
events = []
lores = []
sessionBegin = None

async def initialize_globals():
    global events
    myguild = bot.guilds[1]
    events = await myguild.fetch_scheduled_events()

async def load_lore():
    global lores
    with open("Lore_Snippets/lores.txt", "r") as f:
        lores = [line.strip().lower() for line in f]

@bot.tree.command()
async def gaming(interaction: discord.Interaction):
    """Shows if we are playing this Sunday"""
    today = datetime.date.today()
    event_exists = False
    
    for event in events:
        event_date = event.start_time.date()
        if today - datetime.timedelta(days=7) <= event_date <= today + datetime.timedelta(days=7) and event.status != 4:
            await interaction.response.send_message(f'We are gaming this Sunday {event_date.month}/{event_date.day}')
            event_exists = True
            break
    
    if not event_exists:
        await interaction.response.send_message('We are not gaming this Sunday')

@bot.tree.command()
async def sessionstart(interaction: discord.Interaction):
    global sessionBegin
    sessionBegin = datetime.date.now()
    await interaction.response.send_message("The session has started at " + str(sessionBegin) + ". Please join the session chat @everyone!")

@bot.tree.command()
async def sessionend(interaction: discord.Interaction):
    global sessionBegin
    if sessionBegin == None:
        await interaction.response.send_message("Please start a session with /sessionstart")
        return
    sessionFinal = datetime.date.now()
    difference = sessionFinal - sessionBegin
    await interaction.response.send_message(
        "The session has ended at " + str(sessionFinal) + ". The session duration was " + str(difference) + ".")
    sessionBegin = None

@bot.tree.command()
async def lorelist(interaction: discord.Interaction):
    """Displays all available lores"""
    with open("Lore_Snippets/lores.txt", "r") as f:
        lore_message = f'**Here are the available lores:** \n{f.read()}\n**To get a lore, type /lore (name of lore)**'
    await interaction.response.send_message(lore_message)

async def lore_autocomplete(
    interaction: discord.Interaction, 
    current: str
) -> typing.List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=lore, value=lore)
        for lore in lores if current.lower() in lore.lower()
    ]

@bot.tree.command()
@app_commands.autocomplete(lore=lore_autocomplete)
async def lore(interaction: discord.Interaction, lore: str):
    """Displays the inputted lore"""
    query = lore.lower().strip()
    
    if query == 'list':
        await lorelist(interaction)
        return

    if query in lores:
        file_path = f'Lore_Snippets/{query}.png'
        if os.path.exists(file_path):
            await interaction.response.send_message(file=discord.File(file_path))
        else:
            await interaction.response.send_message('The lore image does not exist.')
    else:
        await interaction.response.send_message('That is not a valid lore')

@bot.tree.command()
async def help(interaction: discord.Interaction):
    """Displays the available commands"""
    help_message = (
        '**Here are the available commands:**\n\n'
        '/lorelist: displays a list of lores\n'
        '/lore (name of lore): displays the lore\n'
        '/gaming: displays if we are gaming this Sunday\n'
        '/help: displays this message'
    )
    await interaction.response.send_message(help_message)

@lore.error
async def lore_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await interaction.response.send_message('You must provide a lore')

bot.run(settings.DISCORD_API_SECRET)