import discord
from discord.ext import commands
import json
import os

# ===========================================================================
# ========================= STORAGE SETUP =========================
# ===========================================================================
STORAGE_FILE = "panel_config.json"

def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {"destination_channel_id": None}

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationMemoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @staticmethod
    def get_embed():
        """Create and return the embed for this panel"""
        return discord.Embed(
            title="🧠 Memory Match",
            description="Select a memory match option:",
            color=discord.Color.purple()
        )

    #? --------------- Row 1: 5 buttons ---------------
    @discord.ui.button(
      label="Normal",
      emoji=discord.PartialEmoji(name="item_royaljelly", id=1464986308639326373),
      custom_id="station_memory:normal",
      row=0
    )
    async def normal_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Normal Memory Match")

    @discord.ui.button(
      label="Mega",
      emoji=discord.PartialEmoji(name="icon_badge", id=1464996867376152764),
      custom_id="station_memory:mega",
      row=0
    )
    async def mega_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Mega Memory Match")

    @discord.ui.button(
      label="Night",
      emoji=discord.PartialEmoji(name="item_mooncharm", id=1464990091721314304),
      custom_id="station_memory:night",
      row=0
    )
    async def night_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Night Memory Match")

    @discord.ui.button(
      label="Extreme",
      emoji=discord.PartialEmoji(name="item_cloudvial", id=1464990525122940948),
      custom_id="station_memory:extreme",
      row=0
    )
    async def extreme_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Extreme Memory Match")

    @discord.ui.button(
      label="Winter",
      emoji=discord.PartialEmoji(name="item_gingerbread", id=1464992612892147722),
      custom_id="station_memory:winter",
      row=0
    )
    async def winter_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Winter Memory Match")

    #? --------------- Handle Click ---------------
    async def handle_click(self, interaction: discord.Interaction, item: str):
        """Handle button clicks"""
        config = load_config()
        destination_id = config.get("destination_channel_id")
        
        if not destination_id:
            await interaction.response.send_message(
                "❌ No destination channel set! Use `/set-destination` to set one.",
                ephemeral=True
            )
            return
        
        destination_channel = interaction.client.get_channel(destination_id)
        if not destination_channel:
            await interaction.response.send_message(
                "❌ Destination channel not found! Please set a new destination channel.",
                ephemeral=True
            )
            return
        
        try:
            await destination_channel.send(f"{interaction.user.mention} selected **{item}** (Memory Match)")
            print(f"Station Memory: {interaction.user.name} selected {item} - sent to #{destination_channel.name}")
            
            await interaction.response.send_message(
                f"✅ {item} sent to {destination_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in station memory panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationMemory(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-station-memory", description="Set up the Memory Match station panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Memory Match station panel"""
        embed = StationMemoryView.get_embed()
        view = StationMemoryView()
        await interaction.response.send_message(embed=embed, view=view)
        print(f"Memory Match panel set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    bot.add_view(StationMemoryView())
    await bot.add_cog(StationMemory(bot))
