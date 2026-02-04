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
PANEL_NAME = "planter_swirled"  # Panel identifier for config storage

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
reminder_service = ReminderService("planter_swirled", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class PlanterSwirledView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this swirled wax planter panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Guaranteed Swirled Wax Placements",
            description=(
                "Each planter placed in its specific field is guaranteed to drop 1 Swirled Wax.\n"
                "This can only occur once per planter per month.\n\n"
                "⏱️ **Cooldown Duration:** estimated 36 days\n\n"
                "⬇️ Use this chart to place each planter in its guaranteed field."
            ),
            color=discord.Color.from_str("0xD7DB59"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Swirled_Wax"
        )
        embed.set_author(
            name="Swirled Wax Planter Tracker",
            icon_url="https://beeswarmtools.netlify.app/static/media/SwirledWax.c31ef0dcfe6622beeb44.png"
        )
        embed.set_footer(
            text="If you just received Swirled Wax, select the same planter below to start its cooldown reminder.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/4kakWbUpg34/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "<:planter_plastic:1462393814911029271> → <:field_coconut:1464671533837451325> Coconut\n"
                "<:planter_candy:1462393769801289840> → <:field_cactus:1464671315138187596> Cactus\n"
                "<:planter_tacky:1462393832820965520> → <:field_pumpkin:1464671357592670229> Pumpkin\n"
                "<:planter_pesticide:1462393806803697897> → <:field_strawberry:1464671115786850476> Strawberry"
            ),
            inline=True
        )
        embed.add_field(
            name="\u200b",
            value=(
                "<:planter_redclay:1462393818480381952> → <:field_sunflower:1464670823863550095> Sunflower\n"
                "<:planter_blueclay:1462393764453679289> → <:field_spider:1464671182182682840> Spider"
            ),
            inline=True
        )
        embed.add_field(
            name="\u200b",
            value=(
                "<:planter_heattreated:1462393789447536862> → <:field_blueflower:1464671010711408742> Blue Flower\n"
                "<:planter_hydroponic:1462393792832208927> → <:field_mushroom:1464670962833428768> Mushroom\n"
                "<:planter_petal:1462393808476963051> → <:field_strawberry:1464671115786850476> Strawberry"
            ),
            inline=True
        )

        return embed
    # ====================================================================

    #? ------------------------ Row 1: 5 buttons -------------------------
    @discord.ui.button(
        label="Plastic",
        emoji=discord.PartialEmoji(name="planter_plastic", id=1462393814911029271),
        custom_id="planter_swirled:plastic",
        row=0
    )
    async def swirled_plastic_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="plastic",
            item_emoji="<:planter_plastic:1462393814911029271>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Plastic Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Candy",
        emoji=discord.PartialEmoji(name="planter_candy", id=1462393769801289840),
        custom_id="planter_swirled:candy",
        row=0
    )
    async def swirled_candy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="candy",
            item_emoji="<:planter_candy:1462393769801289840>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Candy Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Tacky",
        emoji=discord.PartialEmoji(name="planter_tacky", id=1462393832820965520),
        custom_id="planter_swirled:tacky",
        row=0
    )
    async def swirled_tacky_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="tacky",
            item_emoji="<:planter_tacky:1462393832820965520>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Tacky Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Pesticide",
        emoji=discord.PartialEmoji(name="planter_pesticide", id=1462393806803697897),
        custom_id="planter_swirled:pesticide",
        row=0
    )
    async def swirled_pesticide_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="pesticide",
            item_emoji="<:planter_pesticide:1462393806803697897>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Pesticide Planter"
        )
    # ====================================================================

    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
        label="Red Clay",
        emoji=discord.PartialEmoji(name="planter_redclay", id=1462393818480381952),
        custom_id="planter_swirled:red",
        row=1
    )
    async def swirled_red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="redclay",
            item_emoji="<:planter_redclay:1462393818480381952>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Red Clay Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Blue Clay",
        emoji=discord.PartialEmoji(name="planter_blueclay", id=1462393764453679289),
        custom_id="planter_swirled:blue",
        row=1
    )
    async def swirled_blue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="blueclay",
            item_emoji="<:planter_blueclay:1462393764453679289>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Blue Clay Planter"
        )
    # ====================================================================

    #? --------------- Row 3: 3 buttons ---------------
    @discord.ui.button(
        label="heat",
        emoji=discord.PartialEmoji(name="planter_heattreated", id=1462393789447536862),
        custom_id="planter_swirled:heat",
        row=2
    )
    async def swirled_heat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="Heat-Treated",
            item_emoji="<:planter_heattreated:1462393789447536862>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Heat-Treated Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Hydroponic",
        emoji=discord.PartialEmoji(name="planter_hydroponic", id=1462393792832208927),
        custom_id="planter_swirled:hydro",
        row=2
        )
    async def swirled_hydro_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="hydro",
            item_emoji="<:planter_hydroponic:1462393792832208927>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Hydroponic Planter"
        )
    # ====================================================================
    @discord.ui.button(
        label="Petal",
        emoji=discord.PartialEmoji(name="planter_petal", id=1462393808476963051),
        custom_id="planter_swirled:petal",
        row=2
    )
    async def swirled_petal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="petal",
            item_emoji="<:planter_petal:1462393808476963051>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Swirled Wax",
            success_item_name="Swirled Wax : Petal Planter"
        )



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class PlanterSwirled(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("planter_swirled", reminder_service)

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
                        view = PlanterSwirledView()
                        await message.edit(view=view)
                        print(f"Restored Swirled Planter panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = PlanterSwirledView.get_embed()
                        view = PlanterSwirledView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Swirled Planter panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(PlanterSwirledView())
    await bot.add_cog(PlanterSwirled(bot))
