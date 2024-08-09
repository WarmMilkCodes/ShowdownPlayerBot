import config, dbInfo, discord, logging
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger('scl_log')

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(config.scl_server)

        if guild:
            logger.info(f"Found guild: {guild.name}")
            for member in guild.members:
                logger.info(f"Checking member: {member.name}")

                if member.bot:
                    # Check if the bot exists in the database
                    bot_in_db = dbInfo.player_collection.find_one({"Discord ID": int(member.id)})

                    # If bot found in database, remove
                    if bot_in_db:
                        dbInfo.player_collection.delete_one({"Discord ID": int(member.id)})
                        logger.info(f"Removed bot {member.name} from player collection")
                    continue

                # Check if member exists in player collection
                existing_member = dbInfo.player_collection.find_one({"Discord ID": int(member.id)})

                if not existing_member:
                    last_id = dbInfo.player_collection.find_one(sort=[('SCL ID', -1)], projection={'_id':0, 'SCL ID':1})
                    new_id = last_id['SCL ID'] + 1 if last_id else 1
                    player_info = {"Discord ID":int(member.id), "SCL ID": int(new_id), "User Name":member.name, "Display Name":member.display_name, "Team": "Unassigned"}
                    dbInfo.player_collection.insert_one(player_info)
                    logger.info(f"Added {member.name} to player collection")
        
        logger.info("Player check completed. Bot is ready for commands.")

    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            logger.warning(f"New member {member.name} is a bot.")
            return
        
        # Check if member exists in user table already
        existing_member = dbInfo.player_collection.find_one({"Discord ID":int(member.id)})

        if not existing_member:
                    last_id = dbInfo.player_collection.find_one(sort=[('SCL ID', -1)], projection={'_id':0, 'SCL ID':1})
                    new_id = last_id['SCL ID'] + 1 if last_id else 1
                    player_info = {"Discord ID":int(member.id), "SCL ID": int(new_id), "User Name":member.name, "Display Name":member.display_name, "Team": "Unassigned"}
                    dbInfo.player_collection.insert_one(player_info)
                    logger.info(f"Added {member.name} to player collection")

        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        embed = discord.Embed(title="New Member Joined", color=0xFFD525) # yellow color from logo
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="Discord ID", value=str(member.id), inline=True)
        embed.set_thumbnail(url=avatar_url)

        new_member_channel = self.bot.get_channel(config.new_member_announce)
        await new_member_channel.send(embed=embed)


def setup(bot):
     bot.add_cog(EventsCog(bot))
    
