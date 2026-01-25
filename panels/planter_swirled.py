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
class PlanterSwirledView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this swirled wax planter panel"""
        
        embed = discord.Embed(
            title="Guaranteed Swirled Wax Placements",
            description=(
              "Each planter placed in its specific field is guaranteed to drop 1 Swirled Wax.\n"
              "This can only occur once per planter per month.\n\n"
              "⏱️ **Cooldown Duration:** estimated 36 days\n\n"
              "⬇️ Use this chart to place each planter in its guaranteed field."
            ),
            color=discord.Color.from_str("0xD7DB59"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Swirled_Wax"
        )
        embed.set_author(
          name="Swirled Wax Planter Tracker",
          icon_url="https://beeswarmtools.netlify.app/static/media/SwirledWax.c31ef0dcfe6622beeb44.png"
        )
        embed.set_footer(
          text="If you just received Swirled Wax, select the same planter below to start its cooldown reminder.",
          icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/4kakWbUpg34/maxresdefault.jpg")
        
        embed.add_field(
          name="\u200b",
              value=(
                  "<:planter_plastic:1462393814911029271> → <:field_coconut:1464671533837451325> Coconut\n"
                  "<:planter_candy:1462393769801289840> → <:field_cactus:1464671315138187596> Cactus\n"
                  "<:planter_tacky:1462393832820965520> → <:field_pumpkin:1464671357592670229> Pumpkin\n"
                  "<:planter_pesticide:1462393806803697897> → <:field_strawberry:1464671115786850476> Strawberry"
              ),
          inline=True
        )
        embed.add_field(
          name="\u200b",
          value=(
            "<:planter_redclay:1462393818480381952> → <:field_sunflower:1464670823863550095> Sunflower\n"
            "<:planter_blueclay:1462393764453679289> → <:field_spider:1464671182182682840> Spider"
          ),
          inline=True
        )
        embed.add_field(
          name="\u200b",
          value=(
            "<:planter_heattreated:1462393789447536862> → <:field_blueflower:1464671010711408742> Blue Flower\n"
            "<:planter_hydroponic:1462393792832208927> → <:field_mushroom:1464670962833428768> Mushroom\n"
            "<:planter_petal:1462393808476963051> → <:field_strawberry:1464671115786850476> Strawberry"
          ),
          inline=True
        )

        return embed

    #? --------------- Row 1: 5 buttons ---------------
    @discord.ui.button(
      label="Plastic",
      emoji=discord.PartialEmoji(name="planter_plastic", id=1462393814911029271),
      custom_id="planter_swirled:plastic",
      row=0
    )
    async def swirled_plastic_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Plastic")

    @discord.ui.button(
      label="Candy",
      emoji=discord.PartialEmoji(name="planter_candy", id=1462393769801289840),
      custom_id="planter_swirled:candy",
      row=0
    )
    async def swirled_candy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Candy")

    @discord.ui.button(
      label="Tacky",
      emoji=discord.PartialEmoji(name="planter_tacky", id=1462393832820965520),
      custom_id="planter_swirled:tacky",
      row=0
    )
    async def swirled_tacky_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Tacky")

    @discord.ui.button(
      label="Pesticide",
      emoji=discord.PartialEmoji(name="planter_pesticide", id=1462393806803697897),
      custom_id="planter_swirled:pesticide",
      row=0
    )
    async def swirled_pesticide_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Pesticide")

    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
      label="Red Clay",
      emoji=discord.PartialEmoji(name="planter_redclay", id=1462393818480381952),
      custom_id="planter_swirled:red",
      row=1
    )
    async def swirled_red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Red Clay")

    @discord.ui.button(
      label="Blue Clay",
      emoji=discord.PartialEmoji(name="planter_blueclay", id=1462393764453679289),
      custom_id="planter_swirled:blue",
      row=1
    )
    async def swirled_blue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Blue Clay")

    #? --------------- Row 3: 3 buttons ---------------
    @discord.ui.button(
      label="Heat-Treated",
      emoji=discord.PartialEmoji(name="planter_heattreated", id=1462393789447536862),
      custom_id="planter_swirled:heat",
      row=2
    )
    async def swirled_heat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Heat-Treated")

    @discord.ui.button(
      label="Hydroponic",
      emoji=discord.PartialEmoji(name="planter_hydroponic", id=1462393792832208927),
      custom_id="planter_swirled:hydro",
      row=2
    )
    async def swirled_hydro_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Hydroponic")

    @discord.ui.button(
      label="Petal",
      emoji=discord.PartialEmoji(name="planter_petal", id=1462393808476963051),
      custom_id="planter_swirled:petal",
      row=2
    )
    async def swirled_petal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Petal")

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
            await destination_channel.send(f"{interaction.user.mention} selected **{item}** (Swirled Planter)")
            print(f"Planter Swirled: {interaction.user.name} selected {item} - sent to #{destination_channel.name}")
            
            await interaction.response.send_message(
                f"✅ {item} sent to {destination_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in planter swirled panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class PlanterSwirled(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-planter-swirled", description="Set up the Swirled Planter panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Swirled Planter panel"""
        embed = PlanterSwirledView.get_embed()
        view = PlanterSwirledView()
        await interaction.response.send_message(embed=embed, view=view)
        print(f"Swirled Planter panel set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    bot.add_view(PlanterSwirledView())
    await bot.add_cog(PlanterSwirled(bot))
