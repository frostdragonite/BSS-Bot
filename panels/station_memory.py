import discord
from discord.ext import commands
from core.reminder_service import ReminderService, CooldownConfig, get_reminder_checker
from core.config_service import (
    get_panel_message,
    save_panel_message
)
from core.click_handler_service import handle_panel_click

# ===========================================================================
# ========================= STORAGE SETUP =========================
# ===========================================================================
PANEL_NAME = "station_memory"  # Panel identifier for config storage

# Cooldown configuration for each station
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
COOLDOWN_MAP = {
    "normal": CooldownConfig(hours=2),
    "mega": CooldownConfig(hours=4),
    "night": CooldownConfig(hours=8),
    "extreme": CooldownConfig(hours=8),
    "winter": CooldownConfig(hours=4),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("station_memory", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationMemoryView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    
    
    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this memory match station panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Memory Match Cooldown Reminders",
            description=(
                "Track cooldowns for all Memory Match stations.\n"
                "Each station has its own independent cooldown timer.\n\n"
                "⬇️ Use this chart to view each station cooldown and cost."
            ),
            color=discord.Color.from_str("0xEBC94C"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Memory_Match"
        )
        embed.set_author(
            name="Memory Match Tracker",
            icon_url="https://media.discordapp.net/attachments/1464545436353433674/1465744228750594109/100.png?ex=697a3830&is=6978e6b0&hm=a1dd87468b1dba3051d30935007ce128d48e6cc1dc681465dd596311de780474&=&format=webp&quality=lossless&width=150&height=150"
        )
        embed.set_footer(
            text="If you just played a Memory Match, select the station below to start its cooldown reminder.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/QLk6X9tniFE/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "`2 Hours` → <:item_royaljelly:1464986308639326373> Normal - <:honey:1462393791104155744> 25k Honey\n"
                "`4 Hours` → <:icon_badge:1464996867376152764> Mega - <:honey:1462393791104155744> 500k Honey\n"
                "`8 Hours` → <:item_mooncharm:1464990091721314304> Night - <:honey:1462393791104155744> 5M Honey\n"
                "`8 Hours` → <:item_cloudvial:1464990525122940948> Extreme - <:honey:1462393791104155744> 25B Honey\n"
                "`4 Hours` → <:item_gingerbread:1464992612892147722> Winter - <:item_snowflake:1465027529684553758> 100 Snowflakes"
                ),
            inline=False
        )
        
        return embed
    # ====================================================================

    #? ------------------------ Row 1: 5 buttons -------------------------
    @discord.ui.button(
        label="Normal",
        emoji=discord.PartialEmoji(name="item_royaljelly", id=1464986308639326373),
        custom_id="station_memory:normal",
        row=0
    )
    async def normal_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="normal",
            item_emoji="<:item_royaljelly:1464986308639326373>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Normal Memory Match"
        )
    # ====================================================================
    @discord.ui.button(
        label="Mega",
        emoji=discord.PartialEmoji(name="icon_badge", id=1464996867376152764),
        custom_id="station_memory:mega",
        row=0
    )
    async def mega_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="mega",
            item_emoji="<:icon_badge:1464996867376152764>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Mega Memory Match"
        )
    # ====================================================================
    @discord.ui.button(
        label="Night",
        emoji=discord.PartialEmoji(name="item_mooncharm", id=1464990091721314304),
        custom_id="station_memory:night",
        row=0
    )
    async def night_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="night",
            item_emoji="<:item_mooncharm:1464990091721314304>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Night Memory Match"
        )
    # ====================================================================
    @discord.ui.button(
        label="Extreme",
        emoji=discord.PartialEmoji(name="item_cloudvial", id=1464990525122940948),
        custom_id="station_memory:extreme",
        row=0
    )
    async def extreme_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="extreme",
            item_emoji="<:item_cloudvial:1464990525122940948>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Extreme Memory Match"
        )
    # ====================================================================
    @discord.ui.button(
        label="Winter",
        emoji=discord.PartialEmoji(name="item_gingerbread", id=1464992612892147722),
        custom_id="station_memory:winter",
        row=0
    )
    async def winter_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="winter",
            item_emoji="<:item_gingerbread:1464992612892147722>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Winter Memory Match"
        )



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationMemory(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("station_memory", reminder_service)

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-station-memory", description="Set up the Memory Match station panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Memory Match station panel"""
        embed = StationMemoryView.get_embed()
        view = StationMemoryView()
        await interaction.response.send_message(embed=embed, view=view)
        
        # Get the message that was sent
        message = await interaction.original_response()
        
        # Save panel message info for persistence
        save_panel_message(PANEL_NAME, interaction.channel.id, message.id)
        
        print(f"Memory Match panel set up in #{interaction.channel.name} by {interaction.user.name} (Message ID: {message.id})")

    #? --------------- Restore Panel on Startup ---------------
    @commands.Cog.listener()
    async def on_ready(self):
        """Restore panel message on bot startup"""
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
                        view = StationMemoryView()
                        await message.edit(view=view)
                        print(f"Restored Memory Match panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = StationMemoryView.get_embed()
                        view = StationMemoryView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Memory Match panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(StationMemoryView())
    await bot.add_cog(StationMemory(bot))
