from discord.ext import commands

class LeaderboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        """Display the leaderboard of player performance scores."""
        if not self.bot.pp_scores:
            await ctx.send("**The leaderboard is currently empty.**")
            return

        leaderboard = sorted(self.bot.pp_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        leaderboard_message = "**Leaderboard:**\n"
        
        for idx, (pass_id, score_data) in enumerate(leaderboard, start=1):
            user = self.bot.get_user(score_data['user_id'])
            if user:
                leaderboard_message += f"{idx}. **{user.name}** - **Score:** {score_data['score']:.2f}\n"

        await ctx.send(leaderboard_message)

async def setup(bot):
    await bot.add_cog(LeaderboardCommands(bot))