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
PANEL_NAME = "station_base"  # Panel identifier for config storage

# Cooldown configuration for each station
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
STATION_COOLDOWNS = {
    "Wealth Clock": CooldownConfig(hours=1),
    "Honey Storm": CooldownConfig(hours=4),
    "Special Sprout": CooldownConfig(hours=16),
    "Mythic Meteor": CooldownConfig(hours=22),
    "Wind Shrine": CooldownConfig(hours=1),
    "Sticker Printer": CooldownConfig(hours=1),
    "Coconut Dispenser": CooldownConfig(hours=4),
    "Glue Dispenser": CooldownConfig(hours=22),
    "Ant Pass Dispenser": CooldownConfig(hours=2),
    "Robo Pass Dispenser": CooldownConfig(hours=22),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("station_base", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationBaseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this base game station panel"""

        embed = discord.Embed(
            title="Set Reminder for Base Game Station",
            description=(
              "Track your stations cooldowns.\n\n"
              "⬇️ Use this chart to track each station cooldown."
            ),
            color=discord.Color.from_str("0xFFFFFF"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Category:Machines"
        )
        embed.set_author(
          name="Machine & Station Tracker",
          icon_url="https://cdn.discordapp.com/emojis/462596042106470400.webp?size=80"
        )
        embed.set_footer(
          text="Select a location below to start its cooldown reminder.",
          icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/T7oZDl835Ro/maxresdefault.jpg")
        
        embed.add_field(
          name="Row 1",
          value=(
              "`1 Hour` <:sticker_hourglass:1465022845800157255> Wealth Clock\n"
              "`4 Hours` <:token_honey:1465023103477219329> Honey Storm\n"
              "`16 Hours` <:sticker_sprout:1465023224143282417> Special Sprout\n"
              "`22 Hours` ☄️ Mythic Meteor"
          ),
          inline=False
        )
        embed.add_field(
          name="Row 2",
          value=(
              "`1 Hour` <:item_spiritpetal:1465024160467255347> Wind Shrine\n"
              "`1 Hour` 🖨️ Sticker Printer"
          ),
          inline=False
        )
        embed.add_field(
          name="Row 3",
          value=(
              "`4 Hours` <:item_spiritpetal:1465024160467255347> Wind Shrine\n"
              "`22 Hour` <:item_glue:1464852440527405056> Glue Dispenser\n"
              "`2 Hour` <:item_antpass:1465771181176258757> Ant Pass Dispenser\n"
              "`22 Hour` <:item_robopass:1465771250046468097> Robo Pass Dispenser"
          ),
          inline=False
        )
        
        return embed

    #? --------------- Row 1: 4 buttons ---------------
    @discord.ui.button(
      label="Wealth Clock",
      emoji=discord.PartialEmoji(name="sticker_hourglass", id=1465022845800157255),
      custom_id="station_base:wealth_clock",
      row=0
    )
    async def wealth_clock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Wealth Clock")

    @discord.ui.button(
      label="Honey Storm",
      emoji=discord.PartialEmoji(name="token_honey", id=1465023103477219329),
      custom_id="station_base:honey_storm",
      row=0
    )
    async def honey_storm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Honey Storm")

    @discord.ui.button(
      label="Special Sprout",
      emoji=discord.PartialEmoji(name="sticker_sprout", id=1465023224143282417),
      custom_id="station_base:sprout",
      row=0
    )
    async def sprout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Special Sprout")

    @discord.ui.button(
      label="Mythic Meteor",
      emoji="☄️",
      custom_id="station_base:meteor",
      row=0
    )
    async def meteor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Mythic Meteor")


    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
      label="Wind Shrine",
      emoji=discord.PartialEmoji(name="item_spiritpetal", id=1465024160467255347),
      custom_id="station_base:windshrine",
      row=1
    )
    async def windshrine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Wind Shrine")

    @discord.ui.button(
      label="Sticker Printer",
      emoji="🖨️",
      custom_id="station_base:sticker_printer",
      row=1
    )
    async def sticker_printer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Sticker Printer")

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
      label="Coconut Dispenser",
      emoji=discord.PartialEmoji(name="item_coconut", id=1464960629004697701),
      custom_id="station_base:coconut_dispenser",
      row=2
    )
    async def coconut_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Coconut Dispenser")

    @discord.ui.button(
      label="Glue Dispenser",
      emoji=discord.PartialEmoji(name="item_glue", id=1464852440527405056),
      custom_id="station_base:glue_dispenser",
      row=2
    )
    async def glue_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Glue Dispenser")

    @discord.ui.button(
      label="Ant Pass Dispenser",
      emoji=discord.PartialEmoji(name="item_antpass", id=1465771181176258757),
      custom_id="station_base:ant_dispenser",
      row=2
    )
    async def ant_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Ant Pass Dispenser")
        
    @discord.ui.button(
      label="Robo Pass Dispenser",
      emoji=discord.PartialEmoji(name="item_robopass", id=1465771250046468097),
      custom_id="station_base:robo_dispenser",
      row=2
    )
    async def robo_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Robo Pass Dispenser")

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
            
            print(f"Station Base: {interaction.user.name} set reminder for {item} - reminder on {reminder_time_str} ({cooldown_str})")

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in station base panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class StationBase(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("station_base", reminder_service)

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-station-base", description="Set up the Base Station panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Base Station panel"""
        embed = StationBaseView.get_embed()
        view = StationBaseView()
        await interaction.response.send_message(embed=embed, view=view)
        
        # Get the message that was sent
        message = await interaction.original_response()
        
        # Save panel message info for persistence
        save_panel_message(PANEL_NAME, interaction.channel.id, message.id)
        
        print(f"Base Station panel set up in #{interaction.channel.name} by {interaction.user.name} (Message ID: {message.id})")

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
                        view = StationBaseView()
                        await message.edit(view=view)
                        print(f"Restored Base Station panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = StationBaseView.get_embed()
                        view = StationBaseView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Base Station panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(StationBaseView())
    await bot.add_cog(StationBase(bot))
