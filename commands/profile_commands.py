from discord.ext import commands

class ProfileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def create(self, ctx, display_name: str, override: bool = False):
        """Create a profile channel with the given display name."""
        user_id = ctx.author.id
        
        # Check if the user already has a profile
        if str(user_id) in self.bot.profiles:
            await ctx.send("You already have a profile. You cannot create another one.")
            return

        channel = await self.bot.create_profile_channel(ctx, display_name, override)
        if channel:
            username = ctx.author.name
            
            await channel.set_permissions(ctx.guild.default_role, read_messages=False)  # Deny access to everyone
            await channel.set_permissions(ctx.author, read_messages=True)

            # Store detailed profile information
            self.bot.profiles[str(user_id)] = {
                'channel_id': channel.id,
                'display_name': display_name,
                'user_id': str(user_id),
                'username': username,
                'verified_pp': 0,  # Initialize verified PP
                'unverified_pp': 0,  # Initialize unverified PP
                'verified_pass_ids': [],  # List for verified pass IDs
                'unverified_pass_ids': []  # List for unverified pass IDs
            }
            self.bot.save_backup()  # Save backup after creating profile
            await ctx.send(f"**Profile created successfully!**\n"
                           f"**Display Name:** {display_name}\n"
                           f"**Channel:** {channel.mention}")

    @commands.command()
    async def profile(self, ctx):
        """Displays the user's profile based on their user ID."""
        user_id = ctx.author.id
        # Check if the user has a profile
        if str(user_id) not in self.bot.profiles:
            await ctx.send("You do not have a profile. Please create one with `/ppcal create`.")
            return

        profile = self.bot.profiles[str(user_id)]
        channel_id = profile['channel_id']
        channel = self.bot.get_channel(channel_id)
        if channel:
            await ctx.send(f'Your profile channel is: {channel.mention}\n'
                           f'Display Name: {profile["display_name"]}\n'
                           f'User ID: {profile["user_id"]}\n'
                           f'Username: {profile["username"]}\n'
                           f'Verified PP: {profile["verified_pp"]}\n'
                           f'Unverified PP: {profile["unverified_pp"]}\n'
                           f'Verified Pass IDs: {", ".join(profile["verified_pass_ids"])}\n'
                           f'Unverified Pass IDs: {", ".join(profile["unverified_pass_ids"])}')
        else:
            await ctx.send("Profile channel not found.")

    @commands.command()
    async def delete(self, ctx):
        """Delete the user's profile and associated channel."""
        user_id = ctx.author.id
        # Check if the user has a profile
        if str(user_id) not in self.bot.profiles:
            await ctx.send("You do not have a profile to delete.")
            return

        profile = self.bot.profiles[str(user_id)]
        channel_id = profile['channel_id']
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.delete()
            await ctx.send(f'Profile channel {profile["display_name"]} has been deleted.')

        # Remove the user profile from the bot's profile data
        del self.bot.profiles[str(user_id)]
        self.bot.save_backup()  # Save backup after deletion

async def setup(bot):
    await bot.add_cog(ProfileCommands(bot))
