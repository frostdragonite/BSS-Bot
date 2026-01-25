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
class MobBossesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this panel"""
        return discord.Embed(
            title="👹 Bosses",
            description="Select a boss:",
            color=discord.Color.red()
        )

    #? --------------- Row 1: 4 buttons ---------------
    @discord.ui.button(
      label="King Beetle",
      emoji="🐞",
      custom_id="mob_bosses:king_beetle",
      row=0
    )
    async def boss_king_beetle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "King Beetle")

    @discord.ui.button(
      label="Tunnel Bear",
      emoji="🐻",
      custom_id="mob_bosses:tunnel_bear",
      row=0
    )
    async def boss_tunnel_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Tunnel Bear")

    @discord.ui.button(
      label="Coconut Crab",
      emoji="🦀",
      custom_id="mob_bosses:coconut_crab",
      row=0
    )
    async def boss_coconut_crab_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Coconut Crab")

    @discord.ui.button(
      label="Stump Snail",
      emoji="🐌",
      custom_id="mob_bosses:stump_snail",
      row=0
    )
    async def boss_stump_snail_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stump Snail")

    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
      label="Commando Chick",
      emoji="💣",
      custom_id="mob_bosses:commando_chick",
      row=1
    )
    async def boss_commando_chick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Commando Chick")
        
    @discord.ui.button(
      label="Mondo Chick",
      emoji="🐣",
      custom_id="mob_bosses:mondo_chick",
      row=1
    )
    async def boss_mondo_chick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Mondo Chick")

    @discord.ui.button(
      label="Stickbug", 
      emoji="🦗",
      custom_id="mob_bosses:stickbug",
      row=1
    )
    async def boss_stickbug_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stickbug")
    
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
            await destination_channel.send(f"{interaction.user.mention} selected **{item}** (Boss)")
            print(f"Mob Bosses: {interaction.user.name} selected {item} - sent to #{destination_channel.name}")
            
            await interaction.response.send_message(
                f"✅ {item} sent to {destination_channel.mention}!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in mob bosses panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class MobBosses(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-mob-bosses", description="Set up the Bosses panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Bosses panel"""
        embed = MobBossesView.get_embed()
        view = MobBossesView()
        await interaction.response.send_message(embed=embed, view=view)
        print(f"Bosses panel set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    bot.add_view(MobBossesView())
    await bot.add_cog(MobBosses(bot))
