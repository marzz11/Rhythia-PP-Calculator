from discord.ext import commands
from config import ADMIN_USERNAME
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

        if pass_id not in self.bot.pp_scores:
            await ctx.send("Invalid Pass ID.")
            return

        if self.bot.pp_scores[pass_id].get('verified', False):
            await ctx.send("This pass has already been verified.")
            return

        # Verify the pass
        self.bot.pp_scores[pass_id]['verified'] = True
        user_id = self.bot.pp_scores[pass_id]['user_id']

        # Check for the user's profile
        profile = self.bot.profiles.get(str(user_id))
        if not profile:
            await ctx.send(f"No profile found for user ID {user_id}.")
            return

        # Update the profile with verified PP
        verified_pp = self.bot.pp_scores[pass_id]['score']  # Assuming 'score' holds the PP score
        profile['verified_pp'] += verified_pp  # Add to verified PP
        profile['unverified_pp'] -= verified_pp  # Subtract from unverified PP
        profile['verified_pass_ids'].append(pass_id)  # Add pass ID to verified list
        profile['unverified_pass_ids'].remove(pass_id)  # Remove pass ID from unverified list
        
        # Save the updated profile
        self.bot.save_backup()  # Save backup after updating the profile

        # Update the profile channel with the new stats
        profile_channel_id = profile['channel_id']
        profile_channel = self.bot.get_channel(profile_channel_id)
        if profile_channel:
            await profile_channel.send(f"Profile Updated:\n"
                                       f"Display Name: {profile['display_name']}\n"
                                       f"User ID: {profile['user_id']}\n"
                                       f"Username: {profile['username']}\n"
                                       f"Verified PP: {profile['verified_pp']}\n"
                                       f"Unverified PP: {profile['unverified_pp']}")
        else:
            await ctx.send(f"Profile channel not found for user ID {user_id}.")

        await ctx.send(f"Pass ID `{pass_id}` has been successfully verified and profile updated.")
        
        # Update leaderboard after verification
        await self.update_leaderboard()

    @commands.command()
    async def terminate(self, ctx):
        """Terminate all profiles and clear data."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        # Try to delete profile channels safely
        for profile in self.bot.profiles.values():
            profile_channel_id = profile['channel_id']
            try:
                profile_channel = self.bot.get_channel(profile_channel_id)
                if profile_channel:
                    await profile_channel.delete()
                else:
                    await ctx.send(f"Profile channel with ID `{profile_channel_id}` not found.")
            except discord.Forbidden:
                await ctx.send(f"Cannot delete channel `{profile_channel_id}` due to permissions.")
            except discord.NotFound:
                await ctx.send(f"Channel `{profile_channel_id}` not found, might have already been deleted.")
        
        # Clear all data structures
        self.bot.profiles.clear()
        self.bot.user_data.clear()
        self.bot.pp_scores.clear()

        # Save a backup after clearing data
        self.bot.save_backup()

        await ctx.send("All profiles and data have been deleted.")

    async def update_leaderboard(self):
        """Update the leaderboard message in the designated channel."""
        leaderboard_channel_id = self.bot.leaderboard_channel_id  # Set this in your bot's config
        leaderboard_channel = self.bot.get_channel(leaderboard_channel_id)

        if not leaderboard_channel:
            return
        
        # Calculate total verified PP for each player
        total_scores = {}
        for profile in self.bot.profiles.values():
            user_id = profile['user_id']
            total_scores[user_id] = profile['verified_pp']

        # Sort players by total verified PP and get top 100
        top_players = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)[:100]

        # Create leaderboard message
        leaderboard_message = "**Leaderboard**\n"
        for idx, (user_id, score) in enumerate(top_players):
            user = await self.bot.fetch_user(user_id)
            leaderboard_message += f"{idx + 1}. {user.name} - {score} PP\n"
        
        # Send or update the leaderboard message
        async for message in leaderboard_channel.history(limit=1):
            await message.edit(content=leaderboard_message)

    @commands.command()
    async def updatelb(self, ctx):
        """Update the leaderboard."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        await self.update_leaderboard()
        await ctx.send("Leaderboard updated.")

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
