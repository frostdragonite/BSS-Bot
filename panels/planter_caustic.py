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
PANEL_NAME = "planter_caustic"  # Panel identifier for config storage

# Cooldown configuration for each planter
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
COOLDOWN_MAP = {
    "plastic": CooldownConfig(days=36),
    "candy": CooldownConfig(days=36),
    "tacky": CooldownConfig(days=36),
    "pesticide": CooldownConfig(days=36),
    "redclay": CooldownConfig(days=36),
    "blueclay": CooldownConfig(days=36),
    "heat": CooldownConfig(days=36),
    "hydro": CooldownConfig(days=36),
    "petal": CooldownConfig(days=36),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("planter_caustic", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class PlanterCausticView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    

    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this caustic wax planter panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Guaranteed Caustic Wax Placements",
            description=(
                "Each planter placed in its specific field is guaranteed to drop 1 Caustic Wax.\n"
                "This can only occur once per planter per month.\n\n"
                "⏱️ **Cooldown Duration:** estimated 36 days\n\n"
                "⬇️ Use this chart to place each planter in its guaranteed field."
            ),
            color=discord.Color.from_str("0x89DC85"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Caustic_Wax"
        )
        embed.set_author(
            name="Caustic Wax Planter Tracker",
            icon_url="https://beeswarmtools.netlify.app/static/media/CausticWax.e80e5ee95baaf56154d0.png"
        )
        embed.set_footer(
            text="If you just received Caustic Wax, select the same planter below to start its cooldown reminder.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/hPIhZNpmZUs/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "<:planter_plastic:1462393814911029271> → <:field_rose:1464671421861986420> Rose\n"
                "<:planter_candy:1462393769801289840> → <:field_mountain:1464671464996208947> Mountain\n"
                "<:planter_tacky:1462393832820965520> → <:field_bamboo:1464671229167407187> Bamboo\n"
                "<:planter_pesticide:1462393806803697897> → <:field_bamboo:1464671229167407187> or <:field_strawberry:1464671115786850476>"
            ),
            inline=True
        )
        embed.add_field(
            name="\u200b",
            value=(
                "<:planter_redclay:1462393818480381952> → <:field_clover:1464671060011122883> Clover\n"
                "<:planter_blueclay:1462393764453679289> → <:field_clover:1464671060011122883> Clover"
            ),
            inline=True
        )
        embed.add_field(
            name="\u200b",
            value=(
                "<:planter_heattreated:1462393789447536862> → <:field_coconut:1464671533837451325> Coconut\n"
                "<:planter_hydroponic:1462393792832208927> → <:field_coconut:1464671533837451325> Coconut\n"
                "<:planter_petal:1462393808476963051> → <:field_dandelion:1464670893270892887> Dandelion"
            ),
            inline=True
        )

        return embed
    # ====================================================================

    #? ------------------------ Row 1: 5 buttons -------------------------
    @discord.ui.button(
        label="Plastic",
        emoji=discord.PartialEmoji(name="planter_plastic", id=1462393814911029271),
        custom_id="planter_caustic:plastic",
        row=0
    )
    async def caustic_plastic_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="plastic",
            item_emoji="<:planter_plastic:1462393814911029271>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Plastic Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Candy",
        emoji=discord.PartialEmoji(name="planter_candy", id=1462393769801289840),
        custom_id="planter_caustic:candy",
        row=0
    )
    async def caustic_candy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="candy",
            item_emoji="<:planter_candy:1462393769801289840>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Candy Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Tacky",
        emoji=discord.PartialEmoji(name="planter_tacky", id=1462393832820965520),
        custom_id="planter_caustic:tacky",
        row=0
    )
    async def caustic_tacky_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="tacky",
            item_emoji="<:planter_tacky:1462393832820965520>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Tacky Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Pesticide",
        emoji=discord.PartialEmoji(name="planter_pesticide", id=1462393806803697897),
        custom_id="planter_caustic:pesticide",
        row=0
    )
    async def caustic_pesticide_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="pesticide",
            item_emoji="<:planter_pesticide:1462393806803697897>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Pesticide Planter"
        )
    # ====================================================================

    #? ------------------------ Row 2: 2 buttons -------------------------
    @discord.ui.button(
        label="Red Clay",
        emoji=discord.PartialEmoji(name="planter_redclay", id=1462393818480381952),
        custom_id="planter_caustic:red",
        row=1
    )
    async def caustic_red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="red",
            item_emoji="<:planter_redclay:1462393818480381952>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Red Clay Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Blue Clay",
        emoji=discord.PartialEmoji(name="planter_blueclay", id=1462393764453679289),
        custom_id="planter_caustic:blue",
        row=1
    )
    async def caustic_blue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="blue",
            item_emoji="<:planter_blueclay:1462393764453679289>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Blue Clay Planter"
        )

    #? ------------------------ Row 3: 3 buttons -------------------------
    @discord.ui.button(
        label="Heat-Treated",
        emoji=discord.PartialEmoji(name="planter_heattreated", id=1462393789447536862),
        custom_id="planter_caustic:heat",
        row=2
    )
    async def caustic_heat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="heat",
            item_emoji="<:planter_heattreated:1462393789447536862>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Heat-Treated Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Hydroponic",
        emoji=discord.PartialEmoji(name="planter_hydroponic", id=1462393792832208927),
        custom_id="planter_caustic:hydro",
        row=2
    )
    async def caustic_hydro_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="hydro",
            item_emoji="<:planter_hydroponic:1462393792832208927>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Hydroponic Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Petal",
        emoji=discord.PartialEmoji(name="planter_petal", id=1462393808476963051),
        custom_id="planter_caustic:petal",
        row=2
    )
    async def caustic_petal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction,
            item_key="petal",
            item_emoji="<:planter_petal:1462393808476963051>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Caustic Wax",
            success_item_name="Caustic Wax : Petal Planter"
        )



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class PlanterCaustic(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("planter_caustic", reminder_service)

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-planter-caustic", description="Set up the Caustic Planter panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Caustic Planter panel"""
        embed = PlanterCausticView.get_embed()
        view = PlanterCausticView()
        await interaction.response.send_message(embed=embed, view=view)
        
        # Get the message that was sent
        message = await interaction.original_response()
        
        # Save panel message info for persistence
        save_panel_message(PANEL_NAME, interaction.channel.id, message.id)
        
        print(f"Caustic Planter panel set up in #{interaction.channel.name} by {interaction.user.name} (Message ID: {message.id})")

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
                        view = PlanterCausticView()
                        await message.edit(view=view)
                        print(f"Restored Caustic Planter panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = PlanterCausticView.get_embed()
                        view = PlanterCausticView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Caustic Planter panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(PlanterCausticView())
    await bot.add_cog(PlanterCaustic(bot))
