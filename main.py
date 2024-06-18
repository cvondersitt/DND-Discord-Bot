import settings
import datetime
import os
import discord
import typing
import asyncio
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await initialize_globals()
    await load_lore()
    # bot.tree.copy_global_to(guild=settings.GUILD_ID_DEV)
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
    '''Starts a D&D Session'''
    global sessionBegin
    if (sessionBegin is not None):
        await interaction.response.send_message("You may not start two sessions at once.")
        return
    sessionBegin = datetime.datetime.now()
    formatted_time = sessionBegin.strftime("%A, %B %d, %Y at %I:%M %p")
    await interaction.response.send_message(
        content=f"The session has started at {formatted_time}. Please join the session chat @everyone!",
        allowed_mentions=discord.AllowedMentions(everyone=True)
    )
    await remind_end(interaction)
    

async def remind_end(interaction: discord.Interaction):
    global sessionBegin
    await asyncio.sleep(18000)  # Wait for 5 hours
    if (sessionBegin is None):
        return
    
    await interaction.followup.send(
        content=f"Your session has been going on for a while. Did you mean to **/sessionend** <@{interaction.user.id}>?",
        allowed_mentions=discord.AllowedMentions(users=True)
    )
    

@bot.tree.command()
async def sessionend(interaction: discord.Interaction):
    '''Ends a D&D Session'''
    global sessionBegin
    if sessionBegin == None:
        await interaction.response.send_message("Please start a session with /sessionstart")
        return
    sessionFinal = datetime.datetime.now()
    difference = sessionFinal - sessionBegin
    difference = format_timedelta(difference)
    final_formatted = sessionFinal.strftime("%A, %B %d, %Y at %I:%M %p")
    # formatted_time = difference.strftime("%A, %B %d, %Y at %I:%M %p")
    await interaction.response.send_message(
        content=f"The session has ended at {final_formatted}. The session duration was {difference}.")
    sessionBegin = None


def format_timedelta(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)

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
        '/sessionstart: starts a D&D session with a timer. Reminds you ever 5 hours to end\n'
        '/sessionend: ends a D&D session and stops the timer\n'
        '/help: displays this message'
    )
    await interaction.response.send_message(help_message)

@lore.error
async def lore_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await interaction.response.send_message('You must provide a lore')

bot.run(settings.DISCORD_API_SECRET)