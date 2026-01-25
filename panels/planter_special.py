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
class PlanterSpecialView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this panel"""
        return discord.Embed(
            title="⭐ Special Planter Combo",
            description="Select a special planter combination:",
            color=discord.Color.purple()
        )

    # Row 1: 4 buttons
    #? --------------- Row 1: 4 buttons ---------------
    @discord.ui.button(
      label="Super Smoothie",
      emoji=discord.PartialEmoji(name="item_smoothie", id=1464852505992106079),
      custom_id="planter_special:plastic_smoothie",
      row=0
    )
    async def plastic_smoothie_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Plastic Smoothie (36d, any)")

    @discord.ui.button(
      label="Glue",
      emoji=discord.PartialEmoji(name="item_glue", id=1464852440527405056),
      custom_id="planter_special:candy_glue",
      row=0
    )
    async def candy_glue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Candy 10Glue (14d, 3 stump)")

    @discord.ui.button(
      label="Stinger",
      emoji=discord.PartialEmoji(name="item_stinger", id=1464852541073522698),
      custom_id="planter_special:red_stinger",
      row=0
    )
    async def red_stinger_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Red 10Stinger (14d, clov spid cac)")

    @discord.ui.button(
      label="Swirled Wax",
      emoji=discord.PartialEmoji(name="item_swirled", id=1464864368691904585),
      custom_id="planter_special:red_swirled",
      row=0
    )
    async def red_swirled_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Red Swirl at BlueF")

    #? --------------- Row 2: 3 buttons ---------------
    @discord.ui.button(
      label="Loaded Dice",
      emoji=discord.PartialEmoji(name="item_loadeddice", id=1464852480851706060),
      custom_id="planter_special:tacky_loadeddice",
      row=1
    )
    async def tacky_loadeddice_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Tacky LoadedDice (30d, mountain)")

    @discord.ui.button(
      label="Purple Potion",
      emoji=discord.PartialEmoji(name="item_purplepotion", id=1464852625890738299),
      custom_id="planter_special:tacky_purplepotion",
      row=1
    )
    async def tacky_purplepotion_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Tacky PurplePotion (??, Mush -> BlueF)")

    @discord.ui.button(
      label="Neonberry",
      emoji=discord.PartialEmoji(name="item_neonberry", id=1464852580160241837),
      custom_id="planter_special:pesticide_neonberry",
      row=1
    )
    async def pesticide_neonberry_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Pest Neon (7d, Stump -> Mount -> Coconut)")

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
      label="Red Extract",
      emoji=discord.PartialEmoji(name="item_redextract", id=1464852356419158303),
      custom_id="planter_special:heat_redextract",
      row=2
    )
    async def heat_red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Heat 100Red (30d, mush straw rose pep)")

    @discord.ui.button(
      label="Enzyme",
      emoji=discord.PartialEmoji(name="item_enzyme", id=1464852397892309005),
      custom_id="planter_special:heat_enzyme",
      row=2
    )
    async def heat_enzyme_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Heat 100Enz (30d, 3 pineap)")

    #? --------------- Row 4: 2 buttons ---------------
    @discord.ui.button(
      label="Blue Extracts",
      emoji=discord.PartialEmoji(name="item_blueextract", id=1464852380582674719),
      custom_id="planter_special:hydro_100blue",
      row=3
    )
    async def hydro_blue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Hydro 100 Blue (30d, bluef bam pine stump)")

    @discord.ui.button(
      label="Oil",
      emoji=discord.PartialEmoji(name="item_oil", id=1464852420818374770),
      custom_id="planter_special:hydro_100oil",
      row=3
    )
    async def hydro_oil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Hydro 100 Oil (30d, 3 Sun)")

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
            await destination_channel.send(f"{interaction.user.mention} selected **{item}** (Special Planter Combo)")
            print(f"Planter Special: {interaction.user.name} selected {item} - sent to #{destination_channel.name}")
            
            await interaction.response.send_message(
                f"✅ {item} sent to {destination_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in planter special panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class PlanterSpecial(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-planter-special", description="Set up the Special Planter Combo panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Special Planter Combo panel"""
        embed = PlanterSpecialView.get_embed()
        view = PlanterSpecialView()
        await interaction.response.send_message(embed=embed, view=view)
        print(f"Special Planter panel set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    bot.add_view(PlanterSpecialView())
    await bot.add_cog(PlanterSpecial(bot))
