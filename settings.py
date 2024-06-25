import os
from dotenv import load_dotenv
import discord



load_dotenv()

DEV_SERVER = discord.Object(id=int(os.getenv("DEV_SERVER")))
MIKEY_SERVER = discord.Object(id=int(os.getenv("MIKEY_SERVER")))
DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")