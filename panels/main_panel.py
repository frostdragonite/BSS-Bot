import discord
from discord.ext import commands
import importlib
import asyncio
from core.config_service import save_panel_message

# ===========================================================================
# ========================= DYNAMIC IMPORTS =========================
# ===========================================================================
def get_panel_view(module_name, class_name):
    """Dynamically import and return a panel view class"""
    module = importlib.import_module(f"panels.{module_name}")
    return getattr(module, class_name)

def module_to_class_name(module_name: str) -> str:
    """Convert module name (snake_case) to class name (PascalCase) + 'View'"""
    # station_beesmas -> StationBeesmas -> StationBeesmasView
    words = module_name.split('_')
    class_name = ''.join(word.capitalize() for word in words)
    return f"{class_name}View"

# Available panels for autocomplete
AVAILABLE_PANELS = [
    "planter_caustic",
    "planter_swirled",
    "planter_special",
    "mob_bosses",
    "periodic_timer",
    "station_memory",
    "station_base",
    "station_beesmas",
    "favorite_panel"
]

async def panel_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[discord.app_commands.Choice[str]]:
    """Autocomplete for panel names"""
    choices = [panel for panel in AVAILABLE_PANELS if current.lower() in panel.lower()]
    return [discord.app_commands.Choice(name=panel, value=panel) for panel in choices[:25]]

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
    {
        "module": "station_base",
        "class": "StationBaseView"
    },
    {
        "module": "station_beesmas",
        "class": "StationBeesmasView"
    },
    {
        "module": "periodic_timer",
        "class": "PeriodicTimerView"
    },
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
                sent_msg = await interaction.channel.send(embed=embed, view=view)
                # Persist panel message so it can be restored after a restart
                try:
                    save_panel_message(panel_config["module"], interaction.channel.id, sent_msg.id)
                except Exception as e:
                    print(f"Warning: failed to save panel message for {panel_config['module']}: {e}")

                print(f"Panel '{panel_config['module']}' set up in #{interaction.channel.name}")

                # Add a visual separator between panels (except after the last one)
                if index < total - 1:
                    await interaction.channel.send("``` ```")
                    await asyncio.sleep(1)  # Delay between panels to avoid spam
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

    @discord.app_commands.command(name="set-panel-order", description="Set up specific panels in a custom order (comma-separated)")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.autocomplete(panels=panel_autocomplete)
    async def setup_custom_panels(self, interaction: discord.Interaction, panels: str):
        """
        Set up custom panels in specified order.
        Example: /set-panel-order panels: station_beesmas,station_base,favorite_panel
        """
        await interaction.response.send_message(
            "🚀 Setting up custom panels... This may take a moment.",
            ephemeral=True
        )

        # Parse the comma-separated panel list
        panel_names = [p.strip() for p in panels.split(',')]
        
        # Build panel configs dynamically
        custom_panel_order = []
        for panel_name in panel_names:
            class_name = module_to_class_name(panel_name)
            custom_panel_order.append({
                "module": panel_name,
                "class": class_name
            })

        # Send all panels in order
        total = len(custom_panel_order)
        successful = 0
        
        for index, panel_config in enumerate(custom_panel_order):
            try:
                # Dynamically import the view class
                view_class = get_panel_view(panel_config["module"], panel_config["class"])
                
                # Get the embed from the panel's own method
                embed = view_class.get_embed()
                
                # Create the view instance
                view = view_class()
                
                # Send the panel
                sent_msg = await interaction.channel.send(embed=embed, view=view)
                # Persist panel message so it can be restored after a restart
                try:
                    save_panel_message(panel_config["module"], interaction.channel.id, sent_msg.id)
                except Exception as e:
                    print(f"Warning: failed to save panel message for {panel_config['module']}: {e}")

                print(f"Panel '{panel_config['module']}' set up in #{interaction.channel.name}")
                successful += 1

                # Add a visual separator between panels (except after the last one)
                if index < total - 1:
                    await interaction.channel.send("``` ```")
                    await asyncio.sleep(1)  # Delay between panels to avoid spam
                    
            except Exception as e:
                print(f"Error setting up panel '{panel_config['module']}': {e}")
                await interaction.followup.send(
                    f"❌ Error setting up panel '{panel_config['module']}': {str(e)}",
                    ephemeral=True
                )
        
        # Send completion message
        await interaction.followup.send(
            f"✅ {successful}/{total} panel(s) have been set up successfully!",
            ephemeral=True
        )
        
        print(f"Custom panels set up in #{interaction.channel.name} by {interaction.user.name}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MainPanel(bot))
