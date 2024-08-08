from discord.ext import commands
import discord

class LeaderboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        """Display the top 100 players by total PP scores."""
        channel = discord.utils.get(ctx.guild.text_channels, name="leaderboard")
        if not channel:
            await ctx.send("Leaderboard channel does not exist.")
            return

        if not hasattr(self.bot, 'pp_scores') or not self.bot.pp_scores:
            await ctx.send("No player scores are available.")
            return

        user_totals = {}
        for score in self.bot.pp_scores.values():
            user_id = score['user_id']
            if user_id not in user_totals:
                user_totals[user_id] = 0
            user_totals[user_id] += score['score']

        sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)
        top_users = sorted_users[:100]

        leaderboard_msg = "Top 100 Profiles by Total PP Scores:\n"
        for idx, (user_id, total_score) in enumerate(top_users):
            member = ctx.guild.get_member(user_id)
            username = member.display_name if member else "Unknown User"
            leaderboard_msg += f"{idx + 1}. {username} - {total_score:.2f}\n"

        await channel.send(leaderboard_msg)

async def setup(bot):
    await bot.add_cog(LeaderboardCommands(bot))