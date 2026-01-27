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
PANEL_NAME = "planter_special"  # Panel identifier for config storage

# Cooldown configuration for each planter
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
PLANTER_COOLDOWNS = {
    "Super Smoothie": CooldownConfig(days=36),
    "Glue": CooldownConfig(days=14),
    "Stinger": CooldownConfig(days=14),
    "Swirled Wax": CooldownConfig(days=0),
    "Loaded Dice": CooldownConfig(days=30),
    "Purple Potion": CooldownConfig(days=0),
    "Neonberry": CooldownConfig(days=7),
    "Red Extract": CooldownConfig(days=30),
    "Enzyme": CooldownConfig(days=30),
    "Blue Extract": CooldownConfig(days=30),
    "Oil": CooldownConfig(days=30),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("planter_special", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class PlanterSpecialView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this special planter combo panel"""
        embed = discord.Embed(
            title="Guaranteed Insane Special Drops",
            description=(
              "Certain planters have special placement combos that guarantee specific drops.\n"
              "Each combo has its own cooldown.\n\n"
              "⬇️ Use this chart for guaranteed placements."
            ),
            color=discord.Color.from_str("0xA7342B"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Planter#Permanent"
        )
        embed.set_author(
          name="Special Planter Combo Tracker",
          icon_url="https://cdn.discordapp.com/emojis/926225469827870782.webp?size=160"
        )
        embed.set_footer(
          text="If you just received the item, select the same item below to start its cooldown reminder.",
          icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/F22ZY-hmx5Q/maxresdefault.jpg")

        embed.add_field(
          name="Row 1",
              value=(
                  "`36 Days` <:item_smoothie:1464852505992106079> \+ <:plasticplanter:926225586244960359> → Any Fields\n"
                  "`14 Days` <:item_glue:1464852440527405056> \+ <:candyplanter:926225430174900224> → <:field_stump:1464670339756982363> x 3\n"
                  "`14 Days` <:item_stinger:1464852541073522698> \+ <:planter_redclay:1462393818480381952> → <:field_clover:1464671060011122883> → <:field_spider:1464671182182682840> → <:field_cactus:1464671315138187596>"
              ),
        )
        embed.add_field(
          name="Row 2",
              value=(
                  "`30 Days` <:item_loadeddice:1464852480851706060> \+ <:planter_tacky:1462393832820965520> → <:field_mountain:1464671464996208947>\n"
                  "`⠀7 Days` <:item_neonberry:1464852580160241837> \+ <:planter_pesticide:1462393806803697897> → <:field_stump:1464670339756982363> → <:field_mountain:1464671464996208947> → <:field_coconut:1464671533837451325>"
              ),
        )
        embed.add_field(
          name="Row 3",
              value=(
                  "`30 Days` <:item_redextract:1464852356419158303> \+ <:heattreatplanter:926225491403354112> → <:field_mushroom:1464670962833428768> → <:field_strawberry:1464671115786850476> → <:field_rose:1464671421861986420> → <:field_pepper:1464671501432389682>\n"
                  "`30 Days` <:item_enzyme:1464852397892309005> \+ <:heattreatplanter:926225491403354112> → <:field_pineapple:1464671271286472978> x 3"
              ),
        )
        embed.add_field(
          name="Row 4",
              value=(
                  "`30 Days` <:item_blueextract:1464852380582674719> \+ <:planter_hydroponic:1462393792832208927> → <:field_blueflower:1464671010711408742> → <:field_bamboo:1464671229167407187> → <:field_pinetree:1464671389737943142> → <:field_stump:1464670339756982363>\n"
                  "`30 Days` <:item_oil:1464852420818374770> \+ <:planter_hydroponic:1462393792832208927> → <:field_sunflower:1464670823863550095> x 3"
              ),
        )


    # Row 1: 4 buttons
    #? --------------- Row 1: 3 buttons ---------------
    @discord.ui.button(
      label="Super Smoothie",
      emoji=discord.PartialEmoji(name="item_smoothie", id=1464852505992106079),
      custom_id="planter_special:plastic_smoothie",
      row=0
    )
    async def plastic_smoothie_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Super Smoothie")

    @discord.ui.button(
      label="Glue",
      emoji=discord.PartialEmoji(name="item_glue", id=1464852440527405056),
      custom_id="planter_special:candy_glue",
      row=0
    )
    async def candy_glue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Glue")

    @discord.ui.button(
      label="Stinger",
      emoji=discord.PartialEmoji(name="item_stinger", id=1464852541073522698),
      custom_id="planter_special:red_stinger",
      row=0
    )
    async def red_stinger_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stinger")

    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
      label="Loaded Dice",
      emoji=discord.PartialEmoji(name="item_loadeddice", id=1464852480851706060),
      custom_id="planter_special:tacky_loadeddice",
      row=1
    )
    async def tacky_loadeddice_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Loaded Dice")

    @discord.ui.button(
      label="Neonberry",
      emoji=discord.PartialEmoji(name="item_neonberry", id=1464852580160241837),
      custom_id="planter_special:pesticide_neonberry",
      row=1
    )
    async def pesticide_neonberry_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Neonberry")

    #? --------------- Row 3: 2 buttons ---------------
    @discord.ui.button(
      label="Red Extract",
      emoji=discord.PartialEmoji(name="item_redextract", id=1464852356419158303),
      custom_id="planter_special:heat_redextract",
      row=2
    )
    async def heat_red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Red Extract")

    @discord.ui.button(
      label="Enzyme",
      emoji=discord.PartialEmoji(name="item_enzyme", id=1464852397892309005),
      custom_id="planter_special:heat_enzyme",
      row=2
    )
    async def heat_enzyme_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Enzyme")

    #? --------------- Row 4: 2 buttons ---------------
    @discord.ui.button(
      label="Blue Extracts",
      emoji=discord.PartialEmoji(name="item_blueextract", id=1464852380582674719),
      custom_id="planter_special:hydro_blueextract",
      row=3
    )
    async def hydro_blue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Blue Extract")

    @discord.ui.button(
      label="Oil",
      emoji=discord.PartialEmoji(name="item_oil", id=1464852420818374770),
      custom_id="planter_special:hydro_oil",
      row=3
    )
    async def hydro_oil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Oil")

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
            cooldown = PLANTER_COOLDOWNS.get(item)
            
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
                f"✅ Reminder set for special planter combo of **{item}**!\n"
                f"⏱️ You'll be pinged on {reminder_time_str} (in {cooldown_str}).",
                ephemeral=True
            )
            
            print(f"Special Planter Combo: {interaction.user.name} set reminder for {item} - reminder on {reminder_time_str} ({cooldown_str})")
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in planter special panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class PlanterSpecial(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("planter_special", reminder_service)

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-planter-special", description="Set up the Special Planter Combo panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Special Planter Combo panel"""
        embed = PlanterSpecialView.get_embed()
        view = PlanterSpecialView()
        await interaction.response.send_message(embed=embed, view=view)
        
        # Get the message that was sent
        message = await interaction.original_response()
        
        # Save panel message info for persistence
        save_panel_message(PANEL_NAME, interaction.channel.id, message.id)
        
        print(f"Special Planter Combo panel set up in #{interaction.channel.name} by {interaction.user.name} (Message ID: {message.id})")

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
                        view = PlanterSpecialView()
                        await message.edit(view=view)
                        print(f"Restored Special Planter Combo panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = PlanterSpecialView.get_embed()
                        view = PlanterSpecialView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Special Planter Combo panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(PlanterSpecialView())
    await bot.add_cog(PlanterSpecial(bot))
