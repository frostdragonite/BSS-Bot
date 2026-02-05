import discord
from discord.ext import commands
import os

# ===========================================================================
# ========================= THE BOT SETUP =========================
# ===========================================================================
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Remove when using slash commands only
        intents.members = True
        super().__init__(command_prefix="jick ", intents=intents)

    async def setup_hook(self):
        # Load core reminder checker service first
        from core.reminder_service import get_reminder_checker
        reminder_checker = get_reminder_checker(self)
        await self.add_cog(reminder_checker)
        await self.load_extension("core.admin_commands")

        # Load panels from the panels folder
        for file in os.listdir("./panels"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"panels.{file[:-3]}")
        
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Bot is ready!')

bot = MyBot()

# Get token from environment for safety (set in CI / GitHub Actions / host env)
token = os.environ.get('DISCORD_BOT_TOKEN') or os.environ.get('DISCORD_TOKEN')
if not token:
    raise RuntimeError(
        'Discord token not found. Set the DISCORD_BOT_TOKEN environment variable.'
    )

bot.run(token)