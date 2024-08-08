from discord.ext import commands
from config import ADMIN_USERNAME, NOTIFICATION_CHANNEL_ID
import discord

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self, ctx, pass_id: str):
        """Verify a pass ID."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        if pass_id not in getattr(self.bot, 'pp_scores', {}):
            await ctx.send("Invalid Pass ID.")
            return

        if self.bot.pp_scores[pass_id].get('verified', False):
            await ctx.send("This pass has already been verified.")
            return

        self.bot.pp_scores[pass_id]['verified'] = True
        user_id = self.bot.pp_scores[pass_id]['user_id']
        profile_channel_id = self.bot.profiles.get(user_id)
        if profile_channel_id:
            profile_channel = self.bot.get_channel(profile_channel_id)
            if profile_channel:
                await profile_channel.send(f"Pass ID {pass_id} has been verified by {ctx.author.mention}.")
            else:
                await ctx.send(f"Profile channel not found for user ID {user_id}.")
        else:
            await ctx.send(f"No profile channel associated with user ID {user_id}.")

        await ctx.send(f"Pass ID {pass_id} has been successfully verified.")
        if hasattr(self.bot, 'update_profile_channel'):
            await self.bot.update_profile_channel(user_id)

    @commands.command()
    async def terminate(self, ctx):
        """Terminate all profiles and clear data."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        # Try to delete profile channels safely
        for profile_channel_id in list(self.bot.profiles.values()):
            try:
                profile_channel = self.bot.get_channel(profile_channel_id)
                if profile_channel:
                    await profile_channel.delete()
                else:
                    await ctx.send(f"Profile channel with ID {profile_channel_id} not found.")
            except discord.Forbidden:
                await ctx.send(f"Cannot delete channel {profile_channel_id} due to permissions.")
            except discord.NotFound:
                await ctx.send(f"Channel {profile_channel_id} not found, might have already been deleted.")
        
        # Clear all data structures
        self.bot.profiles.clear()
        self.bot.user_data.clear()
        self.bot.pp_scores.clear()

        # Save a backup after clearing data
        self.bot.save_backup()

        await ctx.send("All profiles and data have been deleted.")

    @commands.command()
    async def updatelb(self, ctx):
        """Update the leaderboard."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        if hasattr(self.bot, 'leaderboard'):
            await self.bot.leaderboard(ctx)
        else:
            await ctx.send("Leaderboard function is not defined.")

    @commands.command()
    async def stop(self, ctx):
        """Stop the bot and save a backup."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        if hasattr(self.bot, 'save_backup'):
            self.bot.save_backup()

        await ctx.send("Shutting down the bot. Goodbye!")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))