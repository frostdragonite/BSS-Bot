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
        # Load commands from the cogs folder
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"cogs.{file[:-3]}")
        
        # Load panels from the panels folder
        for file in os.listdir("./panels"):
            if file.endswith(".py") and not file.startswith("__"):
                await self.load_extension(f"panels.{file[:-3]}")
        
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Bot is ready!')

bot = MyBot()
bot.run('ODA3MDY1NzAxMjQwMTQzOTEy.G3lgo_.tTDd2aU7hnOg0ddFbWRWpUZvUYyq8qZezfOvew')