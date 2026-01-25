import discord
from discord.ext import commands
from discord.ui import Button, View, Select

# 1. THE PERSISTENT VIEW
# This class defines the buttons. 'timeout=None' makes them never expire.
# In your bot setup, you MUST register these views so they work after a restart
# bot.add_view(PersistentView())
class CommandPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Button 1: Custom ID is key for persistence
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.danger, emoji="🔥", custom_id="persistent:red")
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Tracking the user: interaction.user gives you everything
        user = interaction.user
        await interaction.response.send_message(f"Logged: {user.name} (ID: {user.id}) clicked the Heat button.", ephemeral=True)

    # Button 2
    @discord.ui.button(label="2nd Button", style=discord.ButtonStyle.secondary, emoji="😂", custom_id="persistent:grey")
    async def grey_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Hey {interaction.user.mention}, you clicked the second button!", ephemeral=True)

# 1.5 THE DROPDOWN VIEW
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="category_select",
        placeholder="Choose a category...",
        options=[
            discord.SelectOption(label="Support", description="Open a ticket", emoji="🎫"),
            discord.SelectOption(label="Roles", description="Get your roles", emoji="🎭")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message(f"You selected: {select.values[0]}", ephemeral=True)


# ===========================================================================
# 2. THE BOT SETUP
# ===========================================================================


@bot.command()
async def say_hi(ctx):
    await ctx.send("Hello, how are you?")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# 3. COMMAND TO DEPLOY THE PANEL
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_panel(ctx):
    """Sends the persistent message to the #command-panel channel"""
    embed = discord.Embed(
      title="🧭 Server Control Panel",
      description="Select an action below",
      color=discord.Color.blurple()
    )

    await ctx.send("Select an action below:", view=CommandPanel())
    await ctx.message.delete() # Cleans up the !setup_panel message

