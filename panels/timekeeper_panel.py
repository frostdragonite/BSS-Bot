import asyncio
import discord
from discord.ext import commands
from core.config_service import (
    toggle_user_timer_flag,
    clear_panel_message,
    get_panel_message,
    get_restore_delay,
    save_panel_message
)

# ===========================================================================
# ========================= STORAGE SETUP =========================
# ===========================================================================
PANEL_NAME = "timekeeper_panel"

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class TimekeeperView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    
    
    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this timekeeper panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Real World Time Reminders",
            description=(
                "Some of the events use real world timers.\n"
                "This usually relies on the minute marks.\n\n"
                "⬇️ Use this chart to track each event timer."
            ),
            color=discord.Color.from_str("0x447200"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Mobs"
        )
        embed.set_author(
            name="Events Tracker",
            icon_url="https://cdn.discordapp.com/emojis/1462393771311235175.webp?size=64&quality=lossless"
        )
        embed.set_footer(
            text="You can select the event below, and you'll be notified when it starts.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/YvG2TGzeOac/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "`XX:00` → 🐣 Mondo Chick\n"
                "`XX:15 and XX:45` → <:sticker_puffshroom:1468791392816988293> Puffshroom"
            ),
            inline=False
        )
        return embed
    # ====================================================================

    #? ------------------------ Row 1: 5 buttons -------------------------
    @discord.ui.button(
        label="Mondo Chick",
        emoji="🐣",
        custom_id="timekeeper:mondo",
        row=0
    )
    async def mondo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            new_state = toggle_user_timer_flag(interaction.user.id, "mondo_timer")
            status = "enabled" if new_state else "disabled"
            
            message = f"{ '✅' if new_state else '❌' } Mondo Timer is {status}"
            if new_state:
              message += "\n⏱️ You'll be pinged on every :00 minute mark."

            await interaction.response.send_message(
                message,
                ephemeral=True
            )
            print(f"Timekeeper: {interaction.user.name} toggled Mondo Timer -> {new_state}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
    # ====================================================================
    @discord.ui.button(
        label="Puffshroom",
        emoji="<:sticker_puffshroom:1468791392816988293>",
        custom_id="timekeeper:puffshroom",
        row=0
    )
    async def puff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            new_state = toggle_user_timer_flag(interaction.user.id, "puffshroom_timer")
            status = "enabled" if new_state else "disabled"
            
            message = f"{ '✅' if new_state else '❌' } Puffshroom Timer is {status}"
            if new_state:
              message += "\n⏱️ You'll be pinged on every :15 and :45 minute mark."

            await interaction.response.send_message(
                message,
                ephemeral=True
            )
            print(f"Timekeeper: {interaction.user.name} toggled Puffshroom Timer -> {new_state}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class TimekeeperPanel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #? --------------- Restore Panel on Startup ---------------
    @commands.Cog.listener()
    async def on_ready(self):
        """Restore panel message on bot startup"""
        delay = get_restore_delay(PANEL_NAME)
        if delay > 0:
            await asyncio.sleep(delay)
        panel_info = get_panel_message(PANEL_NAME)
        if panel_info:
            try:
                channel_id = panel_info["channel_id"]
                message_id = panel_info["message_id"]

                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        message = await channel.fetch_message(message_id)
                        view = TimekeeperView()
                        await message.edit(view=view)
                        print(f"Restored Timekeeper panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        clear_panel_message(PANEL_NAME)
                        print(f"Timekeeper panel message was deleted; cleared from config.")
            except Exception as e:
                print(f"Error restoring Timekeeper panel: {e}")


async def setup(bot: commands.Bot):
    bot.add_view(TimekeeperView())
    await bot.add_cog(TimekeeperPanel(bot))
