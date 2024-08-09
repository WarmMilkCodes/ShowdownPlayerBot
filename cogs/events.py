import config
import dbInfo
import discord, logging
from discord.ext import commands
from datetime import datetime
import pytz

logger = logging.getLogger('scl_log')

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for member in self.bot.get_all_members():
            if not member.bot:
                self.add_member_to_db(member)
        logger.info("Bot is ready and members have been checked and added to database.")

    def add_member_to_db(self, member):
        existing_member = dbInfo.player_collection.find_one({"discord_id": member.id})
        if existing_member is None:
            # Add new member(s) to database
            dbInfo.player_collection.insert_one({
                "discord_id": member.id,
                "user_name": member.name,
                "display_name": member.display_name,
                "team": None,
                "rank": None,
                "db_added": datetime.now(pytz.utc).strftime('%m-%d-%Y')
            })
            logger.info(f"Added {member.name} ({member.id}) to database.")
        else:
            logger.info(f"Member {member.name} ({member.id}) already exists in database.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        
        logger.info(f"New member joined: {member.name} ({member.id}). Adding to database.")
        # Add member to database
        self.add_member_to_db(member)

        # Assign "Member" and "NOT REGISTERED" roles to new member(s)
        await self.assign_role(member, "Member")
        await self.assign_role(member, "NOT REGISTERED")

        # Notify in admin channel
        await self.notify_admin_channel(member)

    async def assign_role(self, member, role_name):
        guild = member.guild
        role = discord.utils.get(guild.roles, name=role.name)

        if role:
            await member.add_roles(role)
            logger.info(f"Assigned role '{role_name}' to {member.name}")
        else:
            logger.error(f"Role '{role_name}' not found in guild '{guild.name}'.")

    async def notify_admin_channel(self, member):
        member_pfp = member.avatar.url if member.avatar else member.default_avatar.url
        embed = discord.Embed(title="New Member Joined", color=discord.Color.blue())
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Discord ID", value=member.id, inline=True)
        embed.set_thumbnail(url=member_pfp)

        admin_channel = config.new_member_announce
        channel = self.bot.get_channel(admin_channel)

        if channel:
            await channel.send(embed=embed)
        else:
            logger.error(f"Admin channel with ID {admin_channel} not found.")


def setup(bot):
    bot.add_cog(EventsCog(bot))