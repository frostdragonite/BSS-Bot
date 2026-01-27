import discord
from discord.ext import commands
import importlib

# ===========================================================================
# ========================= DYNAMIC IMPORTS =========================
# ===========================================================================
def get_panel_view(module_name, class_name):
    """Dynamically import and return a panel view class"""
    module = importlib.import_module(f"panels.{module_name}")
    return getattr(module, class_name)

# ===========================================================================
# ========================= PANEL ORDER =========================
# ===========================================================================
# Define the order of panels to be created
# Each panel file will handle its own embed creation
PANEL_ORDER = [
    {
        "module": "planter_caustic",
        "class": "PlanterCausticView"
    },
    {
        "module": "planter_swirled",
        "class": "PlanterSwirledView"
    },
    {
        "module": "planter_special",
        "class": "PlanterSpecialView"
    },
    {
        "module": "mob_bosses",
        "class": "MobBossesView"
    },
    {
        "module": "station_memory",
        "class": "StationMemoryView"
    },
    # {
    #     "module": "station_base",
    #     "class": "StationBaseView"
    # },
    # {
    #     "module": "station_beesmas",
    #     "class": "StationBeesmasView"
    # }
]

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class MainPanel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="set-panel", description="Set up all bee swarm panels in the current channel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_all_panels(self, interaction: discord.Interaction):
        """Set up all panels in the configured order"""
        await interaction.response.send_message(
            f"🚀 Setting up {len(PANEL_ORDER)} panels... This may take a moment.",
            ephemeral=True
        )

        # Send all panels in order
        total = len(PANEL_ORDER)
        for index, panel_config in enumerate(PANEL_ORDER):
            try:
                # Dynamically import the view class
                view_class = get_panel_view(panel_config["module"], panel_config["class"])
                
                # Get the embed from the panel's own method
                embed = view_class.get_embed()
                
                # Create the view instance
                view = view_class()
                
                # Send the panel
                await interaction.channel.send(embed=embed, view=view)
                print(f"Panel '{panel_config['module']}' set up in #{interaction.channel.name}")

                # Add a visual separator between panels (except after the last one)
                if index < total - 1:
                    await interaction.channel.send("``` ```")
            except Exception as e:
                print(f"Error setting up panel '{panel_config['module']}': {e}")
                await interaction.followup.send(
                    f"❌ Error setting up panel '{panel_config['module']}': {str(e)}",
                    ephemeral=True
                )
        
        # Send completion message
        await interaction.followup.send(
            f"✅ All {len(PANEL_ORDER)} panels have been set up successfully!",
            ephemeral=True
        )
        
        print(f"All panels set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MainPanel(bot))
