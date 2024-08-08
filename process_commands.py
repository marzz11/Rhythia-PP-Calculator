import uuid
from discord.ext import commands
import asyncio

class ProcessCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx):
        user_id = ctx.author.id
        if user_id in self.bot.user_data:
            await ctx.send("**You already have an ongoing process. Complete it before starting a new one.**")
            return

        pass_id = str(uuid.uuid4())  # Generate a unique pass ID
        self.bot.user_data[user_id] = {'pass_id': pass_id}

        await ctx.send(f"**Starting process with Pass ID:** `{pass_id}`. Please provide the following information.")
        await ctx.send("1. **Song Number** (e.g., #1 or #1000)")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            song_number = msg.content.strip()
            if not song_number.startswith('#') or not song_number[1:].isdigit():
                await ctx.send("**Please enter a valid Song Number (e.g., #1 or #1000).**")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['song_number'] = song_number

            await ctx.send("2. **Song Speed** (70%-200%)")
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            song_speed = msg.content.strip()
            if not song_speed.replace('.', '', 1).isdigit() or not (70 <= float(song_speed) <= 200):
                await ctx.send("**Please enter a valid number for Song Speed between 70% and 200%.**")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['song_speed'] = song_speed

            await ctx.send("3. **Percentage Accuracy** (e.g., 95 for 95%)")
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            accuracy = msg.content.strip()
            if not accuracy.replace('.', '', 1).isdigit() or not (0 <= float(accuracy) <= 100):
                await ctx.send("**Please enter a valid number for Accuracy between 0 and 100.**")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['accuracy'] = accuracy

            await ctx.send("4. **Song Difficulty** (number 1-50 that represents the difficulty)")
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            song_difficulty = msg.content.strip()
            if not song_difficulty.replace('.', '', 1).isdigit() or not (1 <= float(song_difficulty) <= 50):
                await ctx.send("**Please enter a valid number for Song Difficulty between 1 and 50.**")
                del self.bot.user_data[user_id]
                return
            self.bot.user_data[user_id]['song_difficulty'] = song_difficulty

            await ctx.send("**Process completed. Calculating PP now...**")
            pp_score = self.bot.calculate_pp(
                song_speed=float(self.bot.user_data[user_id]['song_speed']),
                accuracy=float(self.bot.user_data[user_id]['accuracy']),
                song_difficulty=float(self.bot.user_data[user_id]['song_difficulty'])
            )

            if isinstance(pp_score, str):  # Check for error message
                await ctx.send(pp_score)
                del self.bot.user_data[user_id]
                return

            # Store the pass in the pp_scores
            self.bot.pp_scores[pass_id] = {
                'user_id': user_id,
                'score': pp_score,
                'verified': False
            }

            # Update the profile with the pass information
            profile = self.bot.profiles.get(str(user_id))
            if profile:
                profile['unverified_pass_ids'].append(pass_id)  # Add pass ID to unverified pass IDs
                profile['unverified_pp'] += pp_score  # Update unverified PP
                self.bot.save_backup()  # Save backup after updating the profile

                # Send a message to the user's profile channel
                channel = self.bot.get_channel(profile['channel_id'])
                if channel:
                    await channel.send(f"**New PP Pass submitted!**\n"
                                       f"**Pass ID:** `{pass_id}`\n"
                                       f"**Score:** `{pp_score:.2f}`\n"
                                       f"**Total Unverified PP:** `{profile['unverified_pp']:.2f}`")
                else:
                    await ctx.send("**Profile channel not found.**")

            await ctx.send(f"**Your PP Score is:** `{pp_score:.2f}`\n"
                           f"**Pass ID:** `{pass_id}` has been saved successfully!")

        except asyncio.TimeoutError:
            await ctx.send("**You took too long to respond. Process has been cancelled.**")
            if user_id in self.bot.user_data:
                del self.bot.user_data[user_id]

async def setup(bot):
    await bot.add_cog(ProcessCommands(bot))