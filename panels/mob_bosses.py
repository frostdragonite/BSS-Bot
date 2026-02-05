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
PANEL_NAME = "mob_bosses"  # Panel identifier for config storage

# Cooldown configuration for each boss
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
COOLDOWN_MAP = {
    "kingbeetle": CooldownConfig(days=1),
    "tunnelbear": CooldownConfig(days=2),
    "coconutcrab": CooldownConfig(days=1, hours=12),
    "stumpsnail": CooldownConfig(days=4),
    "commandochick": CooldownConfig(minutes=30),
    "stickbug": CooldownConfig(days=1, hours=12),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("mob_bosses", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class MobBossesView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================
    
    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this bosses panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Boss Respawn Reminders",
            description=(
                "Track respawn timers across all base game bosses.\n"
                "Most bosses follows a fixed respawn interval after being defeated.\n\n"
                "Use `/set-respawn-timer` to apply your personal respawn reduction.\n"
                "Example: `/set-respawn-timer 15` from Gifted Vicious Bee.\n\n"
                "⬇️ Use this chart to view each boss respawn timer."
            ),
            color=discord.Color.from_str("0x747474"),
            url="https://bee-swarm-simulator.fandom.com/wiki/Mobs#Bosses"
        )
        embed.set_author(
            name="Boss Tracker",
            icon_url="https://media.discordapp.net/attachments/1464545436353433674/1465764093205155890/latest.png?ex=697a4ab0&is=6978f930&hm=a7c78d70eb8af663fd43efe51cb46c1292534873a156da47368a02d072a66f79&=&format=webp&quality=lossless&width=230&height=230"
        )
        embed.set_footer(
            text="If you just defeated a boss, select it below to start its respawn reminder.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://i.ytimg.com/vi/iFQykTs5Whw/maxresdefault.jpg")
        

        embed.add_field(
            name="\u200b",
            value=(
                "`1 Day` → 🐞 King Beetle\n"
                "`2 Days` → <:sticker_stretchedbear:1465765080468558090> Tunnel Bear\n"
                "`1 Day 12 Hours` → 🦀 Coconut Crab\n"
                "`4 Days` → <:sticker_snail:1465765046301757555> Stump Snail"
            ),
            inline=False
        )
        embed.add_field(
            name="\u200b",
            value=(
                "`30 mins` → <:sticker_tnt:1465765003792748697> Commando Chick\n"
                "`1 Days 12 Hours` → <:sticker_nymph:1465764975778861178> Stickbug"
            ),
            inline=False
        )

        return embed
    # ====================================================================

    #? ------------------------ Row 1: 5 buttons -------------------------
    @discord.ui.button(
        label="King Beetle",
        emoji="🐞",
        custom_id="mob_bosses:king_beetle",
        row=0
    )
    async def boss_king_beetle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="kingbeetle",
            item_emoji="🐞",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="King Beetle",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Tunnel Bear",
        emoji="<:sticker_stretchedbear:1465765080468558090>",
        custom_id="mob_bosses:tunnel_bear",
        row=0
    )
    async def boss_tunnel_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="tunnelbear",
            item_emoji="<:sticker_stretchedbear:1465765080468558090>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Tunnel Bear",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Coconut Crab",
        emoji="🦀",
        custom_id="mob_bosses:coconut_crab",
        row=0
    )
    async def boss_coconut_crab_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="coconutcrab",
            item_emoji="🦀",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Coconut Crab",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Stump Snail",
        emoji="<:sticker_snail:1465765046301757555>",
        custom_id="mob_bosses:stump_snail",
        row=0
    )
    async def boss_stump_snail_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="stumpsnail",
            item_emoji="<:sticker_snail:1465765046301757555>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Stump Snail",
            apply_cooldown_reduction=True,
        )
    # ====================================================================

    #? ------------------------ Row 2: 2 buttons -------------------------
    @discord.ui.button(
        label="Commando Chick",
        emoji="<:sticker_tnt:1465765003792748697>",
        custom_id="mob_bosses:commando_chick",
        row=1
    )
    async def boss_commando_chick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="commandochick",
            item_emoji="<:sticker_tnt:1465765003792748697>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Commando Chick",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Stickbug", 
        emoji="<:sticker_nymph:1465764975778861178>",
        custom_id="mob_bosses:stickbug",
        row=1
    )
    async def boss_stickbug_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="stickbug",
            item_emoji="<:sticker_nymph:1465764975778861178>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name=PANEL_NAME,
            reminder_item_name="Stickbug",
        )
    


# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class MobBosses(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service(PANEL_NAME, reminder_service)

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
                        view = MobBossesView()
                        await message.edit(view=view)
                        print(f"Restored Bosses panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = MobBossesView.get_embed()
                        view = MobBossesView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Bosses panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

async def setup(bot: commands.Bot):
    bot.add_view(MobBossesView())
    await bot.add_cog(MobBosses(bot))
