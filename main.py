import settings
import datetime
import os
import discord
import typing
import asyncio
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    await sync_events()

    path = 'Lore_Snippets'
    os.makedirs(path, exist_ok=True)

    file_path = 'Lore_Snippets/lores.txt'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("")

    await load_lore()

    for guild in bot.guilds:
        bot.tree.clear_commands(guild=guild)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

# Global variables
events = []
lores = []
sessionBegin = None
deleteLore = False

async def load_lore():
    global lores
    lores = []
    with open("Lore_Snippets/lores.txt", "r") as f:
        lores = [line.strip().lower() for line in f]

@bot.tree.command()
async def sync_events(interaction: discord.Interaction):
    global events
    myguild = bot.guilds[1]
    events = await myguild.fetch_scheduled_events()

@bot.tree.command()
async def gaming(interaction: discord.Interaction):
    """Shows if we are playing this Sunday"""
    today = datetime.date.today()
    playingThisSunday = True
    for event in events:
        event_date = event.start_time.date()
        if today - datetime.timedelta(days=7) <= event_date <= today + datetime.timedelta(days=7):
            await interaction.response.send_message('We are not gaming this Sunday')
            playingThisSunday = False
            break
    
    if playingThisSunday:
        await interaction.response.send_message("We are gaming this Sunday")
        

@bot.tree.command()
async def sessionstart(interaction: discord.Interaction):
    """Starts a D&D Session"""
    global sessionBegin
    if sessionBegin is not None:
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
    if sessionBegin is None:
        return
    
    await interaction.followup.send(
        content=f"Your session has been going on for a while. Did you mean to **/sessionend** <@{interaction.user.id}>?",
        allowed_mentions=discord.AllowedMentions(users=True)
    )
    
@bot.tree.command()
async def sessionend(interaction: discord.Interaction):
    """Ends a D&D Session"""
    global sessionBegin
    if sessionBegin is None:
        await interaction.response.send_message("Please start a session with /sessionstart")
        return
    sessionFinal = datetime.datetime.now()
    difference = sessionFinal - sessionBegin
    difference = format_timedelta(difference)
    final_formatted = sessionFinal.strftime("%A, %B %d, %Y at %I:%M %p")
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
async def listlore(interaction: discord.Interaction):
    """Displays all available lores"""
    with open("Lore_Snippets/lores.txt", "r") as f:
        lines = [line.strip().lower() for line in f]
    
    lore_message = f'**Here are the available lores:**'
    for line in lines:
        if line != '':
            lore_message += ('\n' + line)
    lore_message += '\n**To get a lore, type /lore (name of lore)**'
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
    
    if query in lores:
        file_path = f'Lore_Snippets/{query}.png'
        if os.path.exists(file_path):
            await interaction.response.send_message(file=discord.File(file_path))
        else:
            await interaction.response.send_message('The lore image does not exist.')
    else:
        await interaction.response.send_message('That is not a valid lore')

@bot.tree.command()
async def addlore(interaction: discord.Interaction, lore: str, image: discord.Attachment):
    """Adds a lore to the database"""
    global lores
    filename = 'Lore_Snippets/' + lore + '.png'
    if os.path.exists(filename) or lore in lores:
        await interaction.response.send_message(f"The lore **{lore}** is already added. Please choose a different lore or delete the existing **{lore}**")
        return
    
    await image.save(filename)
    with open("Lore_Snippets/lores.txt", "a") as f:
        f.write(f"\n{lore}")
    await interaction.response.send_message(f"The lore **{lore}** was successfully added.")

    await load_lore()

@bot.tree.command()
@app_commands.autocomplete(lore=lore_autocomplete)
async def deletelore(interaction: discord.Interaction, lore: str):
    """Removes a lore from the database"""
    global lores
    global deleteLore
    if lore not in lores:
        await interaction.response.send_message(f"The lore **{lore}** does not exist.")
        return
    emojis = ["✅", "❌"]
    await interaction.response.send_message(f"Are you sure that you would like to delete **{lore}**")

    message = interaction.channel.last_message
    if message.author != bot.user:
        await interaction.followup.send(f"Please try again! (Cole is bad at coding)")
        return
    
    for emoji in emojis:
        await message.add_reaction(emoji)

    await asyncio.sleep(3)

    if deleteLore:
        deleteLore = False
        with open('Lore_Snippets/lores.txt', 'r') as file:
            lines = file.readlines()

        # Remove the specified line
        new_lines = ''
        for line in lines:
            if line.strip().lower() != lore.lower() and line.strip().lower() != '':
                new_lines += line
        # lines = [line for line in lines if line.strip().lower() != lore.lower()]

        # Write the modified list back to the file
        with open('Lore_Snippets/lores.txt', 'w') as file:
            file.writelines(new_lines)
        
        # Delete the lore file
        lore_file_path = f'Lore_Snippets/{lore}.png'
        if os.path.exists(lore_file_path):
            os.remove(lore_file_path)
        await interaction.followup.send(f"The lore **{lore}** was successfully deleted")
    else:
        await interaction.followup.send(f"The lore **{lore}** was not deleted")
    
    await load_lore()

@bot.event
async def on_reaction_add(reaction, user):
    global deleteLore

    if user == bot.user:
        return
    if str(reaction.emoji) == "✅":
        deleteLore = True
    elif str(reaction.emoji) == "❌":
        deleteLore = False

@bot.tree.command()
async def help(interaction: discord.Interaction):
    """Displays the available commands"""
    help_message = (
        '**Here are the available commands:**\n\n'
        '/listlore: displays a list of lores\n'
        '/lore (name of lore): displays the lore\n'
        '/gaming: displays if we are gaming this Sunday\n'
        '/sessionstart: starts a D&D session with a timer. Reminds you ever 5 hours to end\n'
        '/sessionend: ends a D&D session and stops the timer\n'
        '/addlore: Write a lore name to add and attach the lore image\n'
        '/deletelore: Deletes a lore from the database\n'
        '/help: displays this message'
    )
    await interaction.response.send_message(help_message)

@lore.error
async def lore_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await interaction.response.send_message('You must provide a lore')

bot.run(settings.DISCORD_API_SECRET)