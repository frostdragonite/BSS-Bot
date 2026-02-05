import asyncio
import discord
from discord.ext import commands
from core.reminder_service import ReminderService, CooldownConfig, get_reminder_checker
from core.config_service import (
    clear_panel_message,
    get_panel_message,
    get_restore_delay,
    save_panel_message
)
from core.click_handler_service import handle_panel_click

# ===========================================================================
# ========================= STORAGE SETUP =========================
# ===========================================================================
PANEL_NAME = "station_base"  # Panel identifier for config storage

# Cooldown configuration for each station
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
COOLDOWN_MAP = {
    "clock": CooldownConfig(hours=1),
    "honeystorm": CooldownConfig(hours=4),
    "sprout": CooldownConfig(hours=16),
    "meteor": CooldownConfig(hours=22),
    "shrine": CooldownConfig(hours=1),
    "printer": CooldownConfig(hours=1),
    "coconut_dispenser": CooldownConfig(hours=4),
    "glue_dispenser": CooldownConfig(hours=22),
    "ant_dispenser": CooldownConfig(hours=2),
    "robo_dispenser": CooldownConfig(hours=22),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("station_base", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationBaseView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    
    
    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this base game station panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Station and Dispenser Cooldown Reminders",
            description=(
                "Track cooldowns for base game stations and dispensers.\n"
                "Each station or dispenser has its own independent cooldown.\n\n"
                "⬇️ Use this chart to view each station and dispenser cooldown."
            ),
            color=discord.Color.from_str("0xFFFFFF"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Category:Machines"
        )
        embed.set_author(
            name="Station & Dispenser Tracker",
            icon_url="https://cdn.discordapp.com/emojis/462596042106470400.webp?size=80"
        )
        embed.set_footer(
            text="If you just used a station or dispenser,, select it below to start its cooldown reminder.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/T7oZDl835Ro/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "`1 Hour` → <:sticker_hourglass:1465022845800157255> Wealth Clock\n"
                "`4 Hours` → <:token_honey:1465023103477219329> Honey Storm\n"
                "`16 Hours` → <:sticker_sprout:1465023224143282417> Special Sprout\n"
                "`22 Hours` → ☄️ Mythic Meteor"
            ),
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value=(
                "`1 Hour` → <:item_spiritpetal:1465024160467255347> Wind Shrine\n"
                "`1 Hour` → 🖨️ Sticker Printer"
            ),
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value=(
                "`4 Hours` → <:item_coconut:1464960629004697701> Coconut Dispenser\n"
                "`22 Hours` → <:item_glue:1464852440527405056> Glue Dispenser\n"
                "`2 Hours` → <:item_antpass:1465771181176258757> Ant Pass Dispenser\n"
                "`22 Hours` → <:item_robopass:1465771250046468097> Robo Pass Dispenser"
            ),
            inline=False
        )
        
        return embed
    # ====================================================================

    #? ------------------------ Row 1: 4 buttons -------------------------
    @discord.ui.button(
        label="Wealth Clock",
        emoji=discord.PartialEmoji(name="sticker_hourglass", id=1465022845800157255),
        custom_id="station_base:wealth_clock",
        row=0
    )
    async def wealth_clock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="clock",
            item_emoji="<:sticker_hourglass:1465022845800157255>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Wealth Clock",
        )
    # ====================================================================
    @discord.ui.button(
        label="Honey Storm",
        emoji=discord.PartialEmoji(name="token_honey", id=1465023103477219329),
        custom_id="station_base:honey_storm",
        row=0
    )
    async def honey_storm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="honeystorm",
            item_emoji="<:token_honey:1465023103477219329>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Honey Storm",
        )
    # ====================================================================
    @discord.ui.button(
        label="Special Sprout",
        emoji=discord.PartialEmoji(name="sticker_sprout", id=1465023224143282417),
        custom_id="station_base:sprout",
        row=0
    )
    async def sprout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="sprout",
            item_emoji="<:sticker_sprout:1465023224143282417>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Special Sprout",
        )
    # ====================================================================
    @discord.ui.button(
        label="Mythic Meteor",
        emoji="☄️",
        custom_id="station_base:meteor",
        row=0
    )
    async def meteor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="meteor",
            item_emoji="☄️",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Mythic Meteor",
        )
    # ====================================================================

    #? ------------------------ Row 2: 2 buttons -------------------------
    @discord.ui.button(
        label="Wind Shrine",
        emoji=discord.PartialEmoji(name="item_spiritpetal", id=1465024160467255347),
        custom_id="station_base:windshrine",
        row=1
    )
    async def windshrine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="shrine",
            item_emoji="<:item_spiritpetal:1465024160467255347>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Wind Shrine",
        )
    # ====================================================================
    @discord.ui.button(
        label="Sticker Printer",
        emoji="🖨️",
        custom_id="station_base:sticker_printer",
        row=1
    )
    async def sticker_printer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="printer",
            item_emoji="🖨️",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Sticker Printer",
        )
    # ====================================================================

    #? ------------------------ Row 3: 4 buttons -------------------------
    @discord.ui.button(
        label="Coconut Dispenser",
        emoji=discord.PartialEmoji(name="item_coconut", id=1464960629004697701),
        custom_id="station_base:coconut_dispenser",
        row=2
    )
    async def coconut_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="coconut_dispenser",
            item_emoji="<:item_coconut:1464960629004697701>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Coconut Dispenser",
        )
    # ====================================================================
    @discord.ui.button(
        label="Glue Dispenser",
        emoji=discord.PartialEmoji(name="item_glue", id=1464852440527405056),
        custom_id="station_base:glue_dispenser",
        row=2
    )
    async def glue_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="glue_dispenser",
            item_emoji="<:item_glue:1464852440527405056>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Glue Dispenser",
        )
    # ====================================================================
    @discord.ui.button(
        label="Ant Pass Dispenser",
        emoji=discord.PartialEmoji(name="item_antpass", id=1465771181176258757),
        custom_id="station_base:ant_dispenser",
        row=2
    )
    async def ant_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="ant_dispenser",
            item_emoji="<:item_antpass:1465771181176258757>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Ant Dispenser",
        )
    # ====================================================================
    @discord.ui.button(
        label="Robo Pass Dispenser",
        emoji=discord.PartialEmoji(name="item_robopass", id=1465771250046468097),
        custom_id="station_base:robo_dispenser",
        row=2
    )
    async def robo_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="robo_dispenser",
            item_emoji="<:item_robopass:1465771250046468097>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Robo Dispenser",
        )



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationBase(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service(PANEL_NAME, reminder_service)

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
                        # Message exists, re-add the view to make buttons work
                        view = StationBaseView()
                        await message.edit(view=view)
                        print(f"Restored Base Station panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        clear_panel_message(PANEL_NAME)
                        print(f"Base Station panel message was deleted; cleared from config.")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(StationBaseView())
    await bot.add_cog(StationBase(bot))
