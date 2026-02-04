import discord
from discord.ext import commands
from core.reminder_service import ReminderService, CooldownConfig, get_reminder_checker
from core.config_service import (
    get_destination_channel_id,
    get_panel_message,
    save_panel_message
)
from core.click_handler_service import handle_panel_click

# ===========================================================================
# ========================= STORAGE SETUP =========================
# ===========================================================================
PANEL_NAME = "station_beesmas"  # Panel identifier for config storage

# Cooldown configuration for each station
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
COOLDOWN_MAP = {
    "stocking": CooldownConfig(hours=1),
    "feast": CooldownConfig(hours=1, minutes=30),
    "snowbear": CooldownConfig(hours=1, minutes=30),
    "snowmachine": CooldownConfig(hours=2),
    "roboparty": CooldownConfig(hours=3),
    "candle": CooldownConfig(hours=4),
    "samovar": CooldownConfig(hours=6),
    "onett": CooldownConfig(hours=8),
    "gummybeacon": CooldownConfig(hours=8),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("station_base", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationBeesmasView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    

    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this beesmas station panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Beesmas Station Cooldown Reminders",
            description=(
                "Track cooldowns for all Beesmas event stations.\n"
                "Each station has its own activation rules and cooldown timer.\n\n"
                "⬇️ Use this chart to view each station cooldown."
            ),
            color=discord.Color.from_str("0xF46C55"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Category:Machines"
        )
        embed.set_author(
            name="Beesmas Station Tracker",
            icon_url="https://media.discordapp.net/attachments/1464545436353433674/1466364006515081369/latest.png?ex=697c7966&is=697b27e6&hm=e704e8b502c46ebe8413e9e8e35e279a656a19edab647cd2033747df5396022f&=&format=webp&quality=lossless&width=179&height=179"
        )
        embed.set_footer(
            text="If you just used a Beesmas station, select it below to start its cooldown reminder.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/YEb_2jPeZqc/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "`1 Hour` → <:sticker_stocking:1465024944701313176> Stocking (Brown Bear)\n"
                "`1 Hour 30 Minutes` → <:sticker_forkandknife:1465025577391231167> Beesmas Feast (Polar Bear)\n"
                "`1 Hour 30 Minutes` → <:sticker_snowbear:1465028535629643867> Snow Bear (Panda Bear)\n"
                "`2 Hours` → <:item_snowflake:1465027529684553758> Snow Machine (Bucko Bee)"
            ),
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value=(
                "`3 Hours` → <:sticker_partyrobo:1465026484300419074> Robo Party Cake (Robo Bear)\n"
                "`4 Hours` → <:beequip_candle:1465028727519051998> Honeyday Candle (Riley Bee)\n"
                "`6 Hours` → <:sticker_yellowmug:1465026671282356264> Samovar (Dapper Bear)"
            ),
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value=(
                "`8 Hours` → <:sticker_beekeeper:1465026845526462606> Lit Art (Onett)\n"
                "`8 Hours` → <:sticker_gummybear:1465026964065620216> Gummy Beacon (Gummy Bear)"
            ),
            inline=False
        )
        
        return embed
    # ====================================================================

    #? ------------------------ Row 1: 4 buttons -------------------------
    @discord.ui.button(
        label="Stocking",
        emoji=discord.PartialEmoji(name="sticker_stocking", id=1465024944701313176),
        custom_id="station_beesmas:stocking",
        row=0
    )
    async def stocking_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="stocking",
            item_emoji="<:sticker_stocking:1465024944701313176>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Stocking",
        )
    # ====================================================================
    @discord.ui.button(
        label="Beesmas Feast",
        emoji=discord.PartialEmoji(name="sticker_forkandknife", id=1465025577391231167),
        custom_id="station_beesmas:beesmas_feast",
        row=0
    )
    async def feast_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="feast",
            item_emoji="<:sticker_forkandknife:1465025577391231167>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Beesmas Feast",
        )
    # ====================================================================
    @discord.ui.button(
        label="Snow Bear",
        emoji=discord.PartialEmoji(name="sticker_snowbear", id=1465028535629643867),
        custom_id="station_beesmas:snow_bear",
        row=0
    )
    async def snow_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="snowbear",
            item_emoji="<:sticker_snowbear:1465028535629643867>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Snow Bear",
        )
    # ====================================================================
    @discord.ui.button(
        label="Snow Machine",
        emoji=discord.PartialEmoji(name="item_snowflake", id=1465027529684553758),
        custom_id="station_beesmas:snow_machine",
        row=0
    )
    async def snow_machine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="snowmachine",
            item_emoji="<:item_snowflake:1465027529684553758>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Snow Machine",
        )
    # ====================================================================

    #? --------------- Row 2: 3 buttons ---------------
    @discord.ui.button(
        label="Robo Party Cake",
        emoji=discord.PartialEmoji(name="sticker_partyrobo", id=1465026484300419074),
        custom_id="station_beesmas:robo_party",
        row=1
    )
    async def robo_party_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="roboparty",
            item_emoji="<:sticker_partyrobo:1465026484300419074>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Robo Party",
        )
    # ====================================================================
    @discord.ui.button(
        label="Honeyday Candle",
        emoji=discord.PartialEmoji(name="beequip_candle", id=1465028727519051998),
        custom_id="station_beesmas:riley_candle",
        row=1
    )
    async def riley_candle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="candle",
            item_emoji="<:beequip_candle:1465028727519051998>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Honeyday Candle",
        )
    # ====================================================================
    @discord.ui.button(
        label="Samovar",
        emoji=discord.PartialEmoji(name="sticker_yellowmug", id=1465026671282356264),
        custom_id="station_beesmas:samovar",
        row=1
    )
    async def samovar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="samovar",
            item_emoji="<:sticker_yellowmug:1465026671282356264>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Samovar",
        )
    # ====================================================================

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
        label="Lit Art",
        emoji=discord.PartialEmoji(name="sticker_beekeeper", id=1465026845526462606),
        custom_id="station_beesmas:onett_art",
        row=2
    )
    async def onett_art_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="onett",
            item_emoji="<:sticker_beekeeper:1465026845526462606>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Onett Lit Art",
        )
    # ====================================================================
    @discord.ui.button(
        label="Gummy Beacon",
        emoji=discord.PartialEmoji(name="sticker_gummybear", id=1465026964065620216),
        custom_id="station_beesmas:gummy_beacon",
        row=2
    )
    async def gummy_beacon_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="gummybeacon",
            item_emoji="<:sticker_gummybear:1465026964065620216>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Gummy Beacon",
        )



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationBeesmas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("station_beesmas", reminder_service)

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
                        view = StationBeesmasView()
                        await message.edit(view=view)
                        print(f"Restored Beesmas Station panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = StationBeesmasView.get_embed()
                        view = StationBeesmasView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Beesmas Station panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(StationBeesmasView())
    await bot.add_cog(StationBeesmas(bot))
