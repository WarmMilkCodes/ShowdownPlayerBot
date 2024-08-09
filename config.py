import os
from dotenv import load_dotenv

load_dotenv()

# ENVs
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URL = os.getenv('MONGO_URL')
DATABASE = os.getenv('DATABASE_NAME')
PLAYER_COLLECTION = os.getenv('PLAYER_COLLECTION')
TEAM_COLLECTION = os.getenv('TEAM_COLLECTION')

# Frequently used server channels
bot_testing_channel = 1271304798888656999
new_member_announce = 1271334787122073691

# Server ID
scl_server = 1113860513575731282