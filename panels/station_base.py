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
class StationBaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this panel"""
        return discord.Embed(
            title="🏪 Base Station",
            description="Select a station option:",
            color=discord.Color.orange()
        )

    #? --------------- Row 1: 5 buttons ---------------
    @discord.ui.button(
      label="Wealth Clock",
      emoji=discord.PartialEmoji(name="sticker_hourglass", id=1465022845800157255),
      custom_id="station_base:wealth_clock",
      row=0
    )
    async def wealth_clock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Wealth Clock")

    @discord.ui.button(
      label="Honey Storm",
      emoji=discord.PartialEmoji(name="token_honey", id=1465023103477219329),
      custom_id="station_base:honey_storm",
      row=0
    )
    async def honey_storm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Honey Storm")

    @discord.ui.button(
      label="Special Sprout",
      emoji=discord.PartialEmoji(name="sticker_sprout", id=1465023224143282417),
      custom_id="station_base:sprout",
      row=0
    )
    async def sprout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Special Sprout")

    @discord.ui.button(
      label="Mythic Meteor",
      emoji="☄️",
      custom_id="station_base:meteor",
      row=0
    )
    async def meteor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Mythic Meteor")


    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
      label="Wind Shrine",
      emoji=discord.PartialEmoji(name="item_spiritpetal", id=1465024160467255347),
      custom_id="station_base:windshrine",
      row=1
    )
    async def windshrine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Wind Shrine ")

    @discord.ui.button(
      label="Sticker Printer",
      emoji="🖨️",
      custom_id="station_base:sticker_printer",
      row=1
    )
    async def sticker_printer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Sticker Printer")

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
      label="Coconut Dispenser",
      emoji=discord.PartialEmoji(name="item_coconut", id=1464960629004697701),
      custom_id="station_base:coconut_dispenser",
      row=2
    )
    async def coconut_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Coconut Dispenser")

    @discord.ui.button(
      label="Glue Dispenser",
      emoji=discord.PartialEmoji(name="item_glue", id=1464852440527405056),
      custom_id="station_base:glue_dispenser",
      row=2
    )
    async def glue_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Glue Dispenser")

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
            await destination_channel.send(f"{interaction.user.mention} selected **{item}** (Base Station)")
            print(f"Station Base: {interaction.user.name} selected {item} - sent to #{destination_channel.name}")
            
            await interaction.response.send_message(
                f"✅ {item} sent to {destination_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in station base panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationBase(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-station-base", description="Set up the Base Station panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Base Station panel"""
        embed = StationBaseView.get_embed()
        view = StationBaseView()
        await interaction.response.send_message(embed=embed, view=view)
        print(f"Base Station panel set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    bot.add_view(StationBaseView())
    await bot.add_cog(StationBase(bot))
