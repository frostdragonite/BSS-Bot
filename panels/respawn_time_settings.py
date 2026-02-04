import discord
from discord.ext import commands
from core.config_service import set_user_cooldown_reduction

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class RespawnTimeSettings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Set Respawn Time Command ---------------
    @discord.app_commands.command(
        name="set-respawn-time",
        description="Set the monster respawn cooldown reduction percentage (0-50%) for Mob Bosses"
    )
    @discord.app_commands.describe(
        percentage="Cooldown reduction percentage (0-50)"
    )
    async def set_respawn_time(
        self,
        interaction: discord.Interaction,
        percentage: int
    ):
        """Set respawn time cooldown reduction for Mob Bosses"""
        
        # Validate input
        if not 0 <= percentage <= 50:
            await interaction.response.send_message(
                "❌ Cooldown reduction must be between 0 and 50%",
                ephemeral=True
            )
            return
        
        try:
            # Save the user's cooldown reduction percentage for mob_bosses panel
            set_user_cooldown_reduction(interaction.user.id, percentage, panel_name="mob_bosses")
            
            # Send ephemeral message
            message = (
                f"✅ The current monster respawn time is set to -{percentage}%, "
                f"please overwrite the boss timer if you have any existing reminder to update it"
            )
            
            await interaction.response.send_message(
                message,
                ephemeral=True
            )
            
            print(f"User {interaction.user.name} set mob_bosses respawn time reduction to {percentage}%")
            
        except ValueError as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
            print(f"Error setting respawn time: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(RespawnTimeSettings(bot))
