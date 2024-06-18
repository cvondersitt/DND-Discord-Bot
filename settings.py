import os
from dotenv import load_dotenv
import discord



load_dotenv()

GUILD_ID_DEV = discord.Object(id=int(os.getenv("GUILD_ID_DEV")))
DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")