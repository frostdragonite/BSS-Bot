import discord
from discord.ext import commands
from core.reminder_service import ReminderService, CooldownConfig, get_reminder_checker
from core.config_service import (
    get_destination_channel_id,
    get_panel_message,
    save_panel_message
)

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
STATION_COOLDOWNS = {
    "Stocking": CooldownConfig(hours=1),
    "Feast": CooldownConfig(hours=1, minutes=30),
    "Snow Bear": CooldownConfig(hours=1, minutes=30),
    "Snow Machine": CooldownConfig(hours=2),
    "Robo Party": CooldownConfig(hours=3),
    "Riley Candle": CooldownConfig(hours=4),
    "Samovar": CooldownConfig(hours=6),
    "Onett Art": CooldownConfig(hours=8),
    "Gummy Beacon": CooldownConfig(hours=8),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("station_base", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationBeesmasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this panel"""
        return discord.Embed(
            title="🎄 Beesmas Station",
            description="Select a Beesmas station option:",
            color=discord.Color.gold()
        )

    #? --------------- Row 1: 4 buttons ---------------
    @discord.ui.button(
      label="Stocking",
      emoji=discord.PartialEmoji(name="sticker_stocking", id=1465024944701313176),
      custom_id="station_beesmas:stocking",
      row=0
    )
    async def stocking_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stocking")

    @discord.ui.button(
      label="Feast",
      emoji=discord.PartialEmoji(name="sticker_forkandknife", id=1465025577391231167),
      custom_id="station_beesmas:feast",
      row=0
    )
    async def feast_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Feast")

    @discord.ui.button(
      label="Snow Bear",
      emoji=discord.PartialEmoji(name="sticker_snowbear", id=1465028535629643867),
      custom_id="station_beesmas:snow_bear",
      row=0
    )
    async def snow_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Snow Bear")

    @discord.ui.button(
      label="Snow Machine",
      emoji=discord.PartialEmoji(name="item_snowflake", id=1465027529684553758),
      custom_id="station_beesmas:snow_machine",
      row=0
    )
    async def snow_machine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Snow Machine")

    #? --------------- Row 2: 3 buttons ---------------
    @discord.ui.button(
      label="Robo Party",
      emoji=discord.PartialEmoji(name="sticker_partyrobo", id=1465026484300419074),
      custom_id="station_beesmas:robo_party",
      row=1
    )
    async def robo_party_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Robo Party")

    @discord.ui.button(
      label="Riley Candle",
      emoji=discord.PartialEmoji(name="beequip_candle", id=1465028727519051998),
      custom_id="station_beesmas:riley_candle",
      row=1
    )
    async def riley_candle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Riley Candle")

    @discord.ui.button(
      label="Samovar",
      emoji=discord.PartialEmoji(name="sticker_yellowmug", id=1465026671282356264),
      custom_id="station_beesmas:samovar",
      row=1
    )
    async def samovar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Samovar")

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
      label="Onett Art",
      emoji=discord.PartialEmoji(name="sticker_beekeeper", id=1465026845526462606),
      custom_id="station_beesmas:onett_art",
      row=2
    )
    async def onett_art_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Onett Art")

    @discord.ui.button(
      label="Gummy Beacon",
      emoji=discord.PartialEmoji(name="sticker_gummybear", id=1465026964065620216),
      custom_id="station_beesmas:gummy_beacon",
      row=2
    )
    async def gummy_beacon_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Gummy Beacon")

    #? --------------- Handle Click ---------------
    async def handle_click(self, interaction: discord.Interaction, item: str):
        """Handle button clicks and create reminders"""
        destination_id = get_destination_channel_id()
        
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
            # Get cooldown for this specific planter
            cooldown = STATION_COOLDOWNS.get(item)
            
            # Create reminder using the core service
            reminder_time = reminder_service.create_reminder(
                user_id=interaction.user.id,
                item_name=item,
                cooldown=cooldown,
                channel_id=destination_id,
                username=interaction.user.name
            )
            
            # Format reminder time for display
            reminder_time_str = reminder_service.format_reminder_time(reminder_time)
            cooldown_str = str(cooldown)
            
            await interaction.response.send_message(
                f"✅ Reminder set for **{item}**!\n"
                f"⏱️ You'll be pinged on {reminder_time_str} (in {cooldown_str}).",
                ephemeral=True
            )
            
            print(f"Station Beesmas: {interaction.user.name} set reminder for {item} - reminder on {reminder_time_str} ({cooldown_str})")

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in station beesmas panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationBeesmas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("station_beesmas", reminder_service)

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-station-beesmas", description="Set up the Beesmas Station panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Beesmas Station panel"""
        embed = StationBeesmasView.get_embed()
        view = StationBeesmasView()
        await interaction.response.send_message(embed=embed, view=view)
        
        # Get the message that was sent
        message = await interaction.original_response()
        
        # Save panel message info for persistence
        save_panel_message(PANEL_NAME, interaction.channel.id, message.id)
        
        print(f"Beesmas Station panel set up in #{interaction.channel.name} by {interaction.user.name} (Message ID: {message.id})")

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
