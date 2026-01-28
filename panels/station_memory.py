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
PANEL_NAME = "station_memory"  # Panel identifier for config storage

# Cooldown configuration for each station
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
STATION_COOLDOWNS = {
    "Normal": CooldownConfig(hours=2),
    "Mega": CooldownConfig(hours=4),
    "Night": CooldownConfig(hours=8),
    "Extreme": CooldownConfig(hours=8),
    "Winter": CooldownConfig(hours=4),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("station_memory", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class StationMemoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this memory match station panel"""

        embed = discord.Embed(
            title="Set Reminder for Memory Match",
            description=(
              "Track your Memory Match cooldowns to maximize your daily rewards.\n\n"
              "⬇️ Use this chart to track each Memory Match cooldown."
            ),
            color=discord.Color.from_str("0xEBC94C"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Memory_Match"
        )
        embed.set_author(
          name="Memory Match Tracker",
          icon_url="https://media.discordapp.net/attachments/1464545436353433674/1465744228750594109/100.png?ex=697a3830&is=6978e6b0&hm=a1dd87468b1dba3051d30935007ce128d48e6cc1dc681465dd596311de780474&=&format=webp&quality=lossless&width=150&height=150"
        )
        embed.set_footer(
          text="Select a Memory Match station below to start its cooldown reminder.",
          icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/QLk6X9tniFE/maxresdefault.jpg")
        
        embed.add_field(
          name="\u200b",
          value=(
              "`2 Hours` <:item_royaljelly:1464986308639326373> Normal MM: <:honey:1462393791104155744> 25k\n"
              "`4 Hours` <:icon_badge:1464996867376152764> Mega MM: <:honey:1462393791104155744> 500k\n"
              "`8 Hours` <:item_mooncharm:1464990091721314304> Night MM: <:honey:1462393791104155744> 5M\n"
              "`8 Hours` <:item_cloudvial:1464990525122940948> Extreme MM: <:honey:1462393791104155744> 25B\n"
              "`4 Hours` <:item_gingerbread:1464992612892147722> Winter MM: <:item_snowflake:1465027529684553758> 100"
              ),
          inline=False
        )
        
        return embed

    #? --------------- Row 1: 5 buttons ---------------
    @discord.ui.button(
      label="Normal",
      emoji=discord.PartialEmoji(name="item_royaljelly", id=1464986308639326373),
      custom_id="station_memory:normal",
      row=0
    )
    async def normal_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Normal")

    @discord.ui.button(
      label="Mega",
      emoji=discord.PartialEmoji(name="icon_badge", id=1464996867376152764),
      custom_id="station_memory:mega",
      row=0
    )
    async def mega_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Mega")

    @discord.ui.button(
      label="Night",
      emoji=discord.PartialEmoji(name="item_mooncharm", id=1464990091721314304),
      custom_id="station_memory:night",
      row=0
    )
    async def night_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Night")

    @discord.ui.button(
      label="Extreme",
      emoji=discord.PartialEmoji(name="item_cloudvial", id=1464990525122940948),
      custom_id="station_memory:extreme",
      row=0
    )
    async def extreme_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Extreme")

    @discord.ui.button(
      label="Winter",
      emoji=discord.PartialEmoji(name="item_gingerbread", id=1464992612892147722),
      custom_id="station_memory:winter",
      row=0
    )
    async def winter_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Winter")

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
            # Get cooldown for this memory match
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
                f"✅ Reminder set for **{item}** Memory Match!\n"
                f"⏱️ You'll be pinged on {reminder_time_str} (in {cooldown_str}).",
                ephemeral=True
            )
            
            print(f"Station Memory: {interaction.user.name} set reminder for {item} - reminder on {reminder_time_str} ({cooldown_str})")
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in planter caustic panel: {e}")

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
