from discord.ext import commands
from config import NOTIFICATION_CHANNEL_ID, ADMIN_USERNAME

class ProfileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx):
        """Displays the user's profile channel."""
        user_id = ctx.author.id
        if user_id not in self.bot.profiles:
            await ctx.send("You do not have a profile. Please create one with `/ppcal create`.")
            return

        channel_id = self.bot.profiles[user_id]
        channel = self.bot.get_channel(channel_id)
        if channel:
            await ctx.send(f"Your profile channel is: {channel.mention}")
        else:
            await ctx.send("Profile channel not found.")

    @commands.command()
    async def create(self, ctx, display_name: str, override: bool = False):
        """Create a profile channel with the given display name."""
        channel = await self.bot.create_profile_channel(ctx, display_name, override)
        if channel:
            self.bot.profiles[ctx.author.id] = channel.id
            await ctx.send(f"Profile channel created and saved as {display_name}.")
            self.bot.save_backup()

    @commands.command()
    async def create_override(self, ctx, *, display_name: str):
        """Create a profile channel with override permissions."""
        if ctx.author.name != ADMIN_USERNAME:
            await ctx.send("You do not have permission to use this command.")
            return

        user_id = ctx.author.id
        if user_id in self.bot.profiles:
            await ctx.send("You already have a profile.")
            return

        channel = await self.bot.create_profile_channel(ctx, display_name, override=True)
        self.bot.profiles[user_id] = channel.id  # Store channel ID
        self.bot.save_backup()
        await ctx.send(f"Profile created with override successfully! Your profile channel is: {channel.mention}")

        notif_channel = self.bot.get_channel(NOTIFICATION_CHANNEL_ID)
        if notif_channel:
            await notif_channel.send(f"New profile (with override) created by {ctx.author.mention} ({display_name}) in {channel.mention}.")
        else:
            print("Notification channel not found.")

async def setup(bot):
    await bot.add_cog(ProfileCommands(bot))