import asyncio, os
import discord, logging
from utils.logger import setup_logging
from discord.ext import commands
from config import DISCORD_TOKEN

# Configure logging
bot_logger = setup_logging()
logger = logging.getLogger(__name__)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="SCL Players"))


# Load cogs from cogs directory
def load_extensions():
    logger.info("Loading cogs...")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f'cogs.{filename[:-3]} loaded')
            except Exception as e:
                logger.error(f"Error loading cogs.{filename[:-3]}: {e}")

# Run bot
async def main():
    async with bot:
        load_extensions()
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

