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
class StationBeesmasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this panel"""
        return discord.Embed(
            title="🎄 Beesmas Station",
            description="Select a Beesmas station option:",
            color=discord.Color.gold()
        )

    #? --------------- Row 1: 4 buttons ---------------
    @discord.ui.button(
      label="Stocking",
      emoji=discord.PartialEmoji(name="sticker_stocking", id=1465024944701313176),
      custom_id="station_beesmas:stocking",
      row=0
    )
    async def stocking_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stocking")

    @discord.ui.button(
      label="Feast",
      emoji=discord.PartialEmoji(name="sticker_forkandknife", id=1465025577391231167),
      custom_id="station_beesmas:feast",
      row=0
    )
    async def feast_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Feast")

    @discord.ui.button(
      label="Snow Bear",
      emoji=discord.PartialEmoji(name="sticker_snowbear", id=1465028535629643867),
      custom_id="station_beesmas:snow_bear",
      row=0
    )
    async def snow_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Snow Bear")

    @discord.ui.button(
      label="Snow Machine",
      emoji=discord.PartialEmoji(name="item_snowflake", id=1465027529684553758),
      custom_id="station_beesmas:snow_machine",
      row=0
    )
    async def snow_machine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Snow Machine")

    #? --------------- Row 2: 3 buttons ---------------
    @discord.ui.button(
      label="Robo Party",
      emoji=discord.PartialEmoji(name="sticker_partyrobo", id=1465026484300419074),
      custom_id="station_beesmas:robo_party",
      row=1
    )
    async def robo_party_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Robo Party")

    @discord.ui.button(
      label="Riley Candle",
      emoji=discord.PartialEmoji(name="beequip_candle", id=1465028727519051998),
      custom_id="station_beesmas:riley_candle",
      row=1
    )
    async def riley_candle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Riley Candle")

    @discord.ui.button(
      label="Samovar",
      emoji=discord.PartialEmoji(name="sticker_yellowmug", id=1465026671282356264),
      custom_id="station_beesmas:samovar",
      row=1
    )
    async def samovar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Samovar")

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
      label="Onett Art",
      emoji=discord.PartialEmoji(name="sticker_beekeeper", id=1465026845526462606),
      custom_id="station_beesmas:onett_art",
      row=2
    )
    async def onett_art_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Onett Art")

    @discord.ui.button(
      label="Gummy Beacon",
      emoji=discord.PartialEmoji(name="sticker_gummybear", id=1465026964065620216),
      custom_id="station_beesmas:gummy_beacon",
      row=2
    )
    async def gummy_beacon_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Gummy Beacon")

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
            await destination_channel.send(f"{interaction.user.mention} selected **{item}** (Beesmas Station)")
            print(f"Station Beesmas: {interaction.user.name} selected {item} - sent to #{destination_channel.name}")
            
            await interaction.response.send_message(
                f"✅ {item} sent to {destination_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in station beesmas panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationBeesmas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-station-beesmas", description="Set up the Beesmas Station panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Beesmas Station panel"""
        embed = StationBeesmasView.get_embed()
        view = StationBeesmasView()
        await interaction.response.send_message(embed=embed, view=view)
        print(f"Beesmas Station panel set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    bot.add_view(StationBeesmasView())
    await bot.add_cog(StationBeesmas(bot))
