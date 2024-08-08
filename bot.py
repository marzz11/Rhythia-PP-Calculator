import discord
import os
from discord.ext import commands, tasks
from config import BOT_TOKEN, STATUS_CHANNEL_ID
from calculate_pp import calculate_pp, save_backup, update_passes_log, load_backup

def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists('./data'):
        os.makedirs('./data')

# Ensure the data directory exists when the bot starts
ensure_data_directory()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix='/ppcal ', intents=intents)

def calculate_pp_method(song_speed, accuracy, song_difficulty):
    """Calculate and return the PP value based on song speed, accuracy, and song difficulty."""
    return calculate_pp(song_speed, accuracy, song_difficulty)

def save_backup_method():
    """Save the current PP scores and profiles."""
    save_backup(bot.pp_scores, bot.profiles)

def update_passes_log_method():
    """Update the passes log."""
    update_passes_log(bot.pp_scores)

async def create_profile_channel_method(ctx, display_name: str, override: bool = False):
    """Create a profile channel with the given display name."""
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="Profile Channels")
    if not category:
        category = await guild.create_category(name="Profile Channels")
    
    existing_channel = discord.utils.get(guild.text_channels, name=f"profile-{display_name}")
    if existing_channel:
        if not override:
            await ctx.send(f"**Channel {existing_channel.mention} already exists.**")
            return existing_channel
        else:
            await existing_channel.delete()
    
    channel = await guild.create_text_channel(name=f"profile-{display_name}", category=category)
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    await ctx.send(f"**Profile channel created: {channel.mention}**")
    return channel

bot.calculate_pp = calculate_pp_method
bot.save_backup = save_backup_method
bot.update_passes_log = update_passes_log_method
bot.create_profile_channel = create_profile_channel_method

# Load data on startup
bot.pp_scores, bot.profiles = load_backup()
bot.user_data = {}  # Initialize user_data

extensions = [
    'commands.admin_commands',
    'commands.profile_commands',
    'commands.process_commands',
    'commands.leaderboard_commands'
]

async def load_cogs():
    """Load all specified cogs."""
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f'Loaded {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')

@tasks.loop(seconds=10)  # Check every 10 seconds
async def update_status_task():
    """Update the status channel with the bot's online/offline status."""
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if channel:
        if bot.is_ready():
            await channel.edit(name='STATUS: 🟢')  # Bot is online
        else:
            await channel.edit(name='STATUS: 🔴')  # Bot is offline

@update_status_task.before_loop
async def before_update_status_task():
    """Wait until the bot is ready before starting the status loop."""
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    print(f'Logged in as {bot.user.name}')
    await load_cogs()
    update_status_task.start()  # Start the status update task

@bot.event
async def on_command_error(ctx, error):
    """Event handler for command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Please provide all required arguments for the command.**")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("**You do not have permission to use this command.**")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("**Command not found.**")
    else:
        await ctx.send(f"**An unexpected error occurred: {error}**")
        print(f"An unexpected error occurred: {error}")

@bot.event
async def on_disconnect():
    """Event handler for bot shutdown."""
    save_backup_method()  # Save data on shutdown
    print("Bot is shutting down...")

bot.run(BOT_TOKEN)  # Start the bot
