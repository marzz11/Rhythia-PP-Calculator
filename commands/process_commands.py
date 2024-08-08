from discord.ext import commands
import asyncio
import uuid

class ProcessCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx):
        user_id = ctx.author.id
        if user_id in self.bot.user_data:
            await ctx.send("You already have an ongoing process. Complete it before starting a new one.")
            return

        pass_id = str(uuid.uuid4())
        self.bot.user_data[user_id] = {'pass_id': pass_id}

        await ctx.send(f"Starting process with Pass ID: {pass_id}. Please provide the following information.")
        await ctx.send("1. Song Number (e.g., #1 or #1000)")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            song_number = msg.content.strip()
            if not song_number.startswith('#') or not song_number[1:].isdigit():
                await ctx.send("Please enter a valid Song Number (e.g., #1 or #1000).")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['song_number'] = song_number

            await ctx.send("2. Song Speed (70%-200%)")
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            song_speed = msg.content.strip()
            if not song_speed.replace('.', '', 1).isdigit():
                await ctx.send("Please enter a valid number for Song Speed.")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['song_speed'] = song_speed

            await ctx.send("3. Percentage Accuracy (e.g., 95 for 95%)")
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            accuracy = msg.content.strip()
            if not accuracy.replace('.', '', 1).isdigit():
                await ctx.send("Please enter a valid number for Accuracy.")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['accuracy'] = accuracy

            await ctx.send("4. Song Difficulty (number 1-50 that represents the difficulty)")
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            song_difficulty = msg.content.strip()
            if not song_difficulty.replace('.', '', 1).isdigit():
                await ctx.send("Please enter a valid number for Song Difficulty.")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['song_difficulty'] = song_difficulty

            await ctx.send("Process completed. Calculating PP now...")
            pp_score = self.bot.calculate_pp(
                song_speed=float(self.bot.user_data[user_id]['song_speed']),
                accuracy=float(self.bot.user_data[user_id]['accuracy']),
                song_difficulty=float(self.bot.user_data[user_id]['song_difficulty'])
            )
            self.bot.pp_scores[pass_id] = {
                'user_id': user_id,
                'score': pp_score,
                'verified': False
            }

            # Save the backup after updating pp_scores
            self.bot.save_backup()

            # ... rest of the code
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Process has been cancelled.")
            if user_id in self.bot.user_data:
                del self.bot.user_data[user_id]

    @commands.command()
    async def cancel(self, ctx):
        user_id = ctx.author.id
        if user_id not in self.bot.user_data:
            await ctx.send("You do not have an ongoing process to cancel.")
            return

        del self.bot.user_data[user_id]
        await ctx.send("Your ongoing process has been cancelled.")

async def setup(bot):
    await bot.add_cog(ProcessCommands(bot))