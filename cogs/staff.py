import discord, logging, config, dbInfo
from discord.ext import commands
from discord.commands import Option

logger = logging.getLogger('scl_log')

class StaffCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Returns player info embed")
    @commands.has_any_role("League Scribe", "League Moderator", "League Ops", "All Staff")
    async def player_info(self, ctx, user:Option(discord.Member)):
        guild = ctx.guild

        # Check if command is invoked in admin channel(s)
        allowed_channels = [self.bot.get_channel(ch_id) for ch_id in config.admin_channels]
        if ctx.channel.id not in config.admin_channels:
            channels_str = ', '.join([ch.mention for ch in allowed_channels if ch])
            return await ctx.respond("This command can only be used in the following channels: {channels_str}", ephemeral=True)
    
        team_id = dbInfo.teams_collection.find_one({"team_id": {"$in": [r.id for r in user.roles]}}, {"_id": 0, "team_id": 1})
        team_info = "Unassigned"
        if team_id:
            team_role = ctx.guild.get_role(team_id['team_id'])
            if team_role:
                team_info = team_role.mention

        player_info = dbInfo.player_collection.find_one({"discord_id":user.id})

        player_info_list = {
            f"**Discord ID**: {user.id}",
            f"**Username**: {user.name}"
        }

        embed = discord.Embed(title=f"Player Info for {user.display_name}", color=discord.Color.yellow())
        embed.set_thumbnail(url=user.avatar.url if user.avatar.url else user.default_avatar)
        embed.add_field(name="Player Info", value='\n'.join(x for x in player_info_list))

        user_roles = '\n'.join([x.mention for x in user.roles if x != ctx.guild.default_role])
        if user_roles:
            embed.add_field(name="User Roles", value=user_roles, inline=False)

        embed.add_field(name="Team Info", value=team_info, inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(StaffCommands(bot))