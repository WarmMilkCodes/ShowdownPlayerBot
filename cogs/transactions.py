import config, dbInfo, discord, logging
from discord.ext import commands
from discord.commands import Option
from discord.ext.commands import MissingAnyRole, CommandInvokeError, CommandError

logger = logging.getLogger('scl_log')

GUILD_ID = config.scl_server

class TransactionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ## Helper Functions ##
    async def get_team_role(self, team_code: str) -> int:
        """Retrieve team role ID from database"""
        team = dbInfo.teams_collection.find_one({"team_code":team_code})
        if team:
            return team.get("team_id")
        return None
    
    async def validate_command_channel(self, ctx):
        """Check if the command is invoked in the transactions bot channel."""
        if ctx.channel.id != config.transaction_bot_channel:
            transaction_bot_channel = ctx.guild.get_channel(config.transaction_bot_channel)
            await ctx.respond(f"This command can only be used in {transaction_bot_channel.mention}", ephemeral=True)
            return False
        return True
    
    async def get_player_info(self, player_id):
        """Fetch player info from database"""
        return dbInfo.player_collection.find_one({"discord_id":player_id})
    
    async def update_team_in_database(self, player_id, new_team):
        """Update the player's team information in the database."""
        dbInfo.player_collection.update_one({"discord_id": player_id}, {'$set': {'team': new_team}})
    
    async def add_role_to_member(self, member, role, reason):
        """Add role to member with error handling"""
        try:
            await member.add_roles(role, reason=reason)
        except Exception as e:
            logger.error(f"Error adding role {role} to {member.display_name}: {e}")

    async def remove_role_from_member(self, member, role, reason):
        """Remove role from member with error handling"""
        try:
            await member.remove_roles(role, reason=reason)
        except Exception as e:
            logger.error(f"Error removing role {role} from {member.display_name}: {e}")


    ## Error Handling Section ##
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle errors globally within the cog."""
        if isinstance(error, MissingAnyRole):
            await ctx.send("You do not have the required roles to use this command", ephemeral=True)
        elif isinstance(error, CommandInvokeError):
            await ctx.respond(f"An error occured while invoking the command: {error.original}", ephemeral=True)
        elif isinstance(error, CommandError):
            await ctx.respond(f"An error occured: {error}", ephemeral=True)
        else:
            await ctx.send(f"An unknown error occured: {error}", ephemeral=True)
        logger.error(f"Error in command {ctx.command}: {error}")


    ## Commands Section ##
    @commands.slash_command(description="Sign player to team")
    @commands.has_any_role("All Staff", "League Scribe")
    async def sign_player(self, ctx, user:Option(discord.Member), team_abbreviation: Option(str, "Enter 3-letter team abbreviation")):
        logger.info(f"Sign player command initiated for {user.name}")
        await ctx.defer()

        try:
            if not await self.validate_command_channel(ctx):
                return
            
            logger.info(f"Signing {user.name} to {team_abbreviation.upper()}.")

            player_entry = await self.get_player_info(user.id)
            if not player_entry or player_entry.get("Team") not in ["FA", "Unassigned", None]:
                logger.warning(f"{user.name} is already on a team or is not a Free Agent/Unassigned and cannot be signed.")
                return await ctx.respond(f"{user.display_name} is already on a team or not eligible for signing.")
            logger.info(f"{user.name} is a free agent. Proceeding with signing.")

            team_role_id = await self.get_team_role(team_abbreviation.upper())
            if not team_role_id:
                logger.info(f"Invalid team abbreviation passed in signing: {team_abbreviation.upper()}")
                return await ctx.respond(f"Invalid team abbreviation: {team_abbreviation.upper()}")
            
            FA = discord.utils.get(ctx.guild.roles, name="F/A")
            team_role = ctx.guild.get_role(team_role_id)
            await self.add_role_to_member(user, ctx.guild.get_role(team_role_id), "Player Signing")
            await self.remove_role_from_member(user, FA, "Player Signing")

            message = f"{user.mention} has been signed to {team_role.mention}"
            channel = self.bot.get_channel(config.posted_transactions_channel)
            await channel.send(message)

            await self.update_team_in_database(user.id, team_abbreviation.upper())
            await ctx.respond(f"{user.display_name} has been signed to {team_abbreviation.upper()}")

        except Exception as e:
            logger.error(f"Error signing {user.name} to {team_abbreviation.upper()}: {e}")
            await ctx.respond(f"Error signing {user.display_name} to {team_abbreviation.upper()}.\n{e}", ephemeral=True)
            

def setup(bot):
    bot.add_cog(TransactionCommands(bot))