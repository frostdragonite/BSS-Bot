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
PANEL_NAME = "favorite_panel"  # Panel identifier for config storage

COOLDOWN_MAP = {
    "clock": CooldownConfig(hours=1),
    "honeystorm": CooldownConfig(hours=4),
    "stickbug": CooldownConfig(days=1, hours=12),

    "kingbeetle": CooldownConfig(days=1),
    "tunnelbear": CooldownConfig(days=2),
    "coconutcrab": CooldownConfig(days=1, hours=12),
    "stumpsnail": CooldownConfig(days=4),

    "snowbear": CooldownConfig(hours=1, minutes=30),
    "roboparty": CooldownConfig(hours=3),
    "candle": CooldownConfig(hours=4),
    "samovar": CooldownConfig(hours=6),

    "meteor": CooldownConfig(hours=22),
    "glue_dispenser": CooldownConfig(hours=22),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("favorite_panel", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class FavoritePanelView(discord.ui.View):
    # ====================================================================
    def __init__(self):
        super().__init__(timeout=None)
    # ====================================================================

    #? --------------------------- Build Embed ---------------------------
    @staticmethod
    def get_embed():
        # ----------------------------------------------------------------
        """Create and return the embed for this favorite panel"""
        # ----------------------------------------------------------------
        embed = discord.Embed(
            title="Frequently Used Cooldown Reminders",
            description=(
              "This panel contains frequently used cooldown reminders.\n"
            ),
            color=discord.Color.from_str("0x99BFFF"),
        )
        embed.set_author(
            name="Favorite Panel",
            icon_url="https://cdn.discordapp.com/emojis/1468798834388762837.webp?size=64&quality=lossless"
        )
        embed.set_footer(
            text="Yeah, I put the stuff that I often use here. If you want your own custom panel, tell me and I'll implement it later.",
            icon_url="https://cdn.discordapp.com/emojis/1463915624244973609.webp?size=80"
        )
        embed.set_image(url="https://pbs.twimg.com/profile_banners/822099513397514240/1756452043/1500x500")
        

        # embed.add_field(
        #     name="\u200b",
        #     value=(
        #         "`1 Hour` → <:sticker_hourglass:1465022845800157255> Wealth Clock\n"
        #         "`4 Hours` → <:token_honey:1465023103477219329> Honey Storm\n"
        #         "`1 Days 12 Hours` → <:sticker_nymph:1465764975778861178> Stickbug"
        #     ),
        #     inline=False
        # )
        # embed.add_field(
        #     name="\u200b",
        #     value=(
        #         "`1 Day` → 🐞 King Beetle\n"
        #         "`2 Days` → <:sticker_stretchedbear:1465765080468558090> Tunnel Bear\n"
        #         "`1 Day 12 Hours` → 🦀 Coconut Crab\n"
        #         "`4 Days` → <:sticker_snail:1465765046301757555> Stump Snail"
        #     ),
        #     inline=False
        # )
        # embed.add_field(
        #     name="\u200b",
        #     value=(
        #         "`1 Hour 30 Minutes` → <:sticker_snowbear:1465028535629643867> Snow Bear (Panda Bear)\n"
        #         "`3 Hours` → <:sticker_partyrobo:1465026484300419074> Robo Party Cake (Robo Bear)\n"
        #         "`4 Hours` → <:beequip_candle:1465028727519051998> Honeyday Candle (Riley Bee)\n"
        #         "`6 Hours` → <:sticker_yellowmug:1465026671282356264> Samovar (Dapper Bear)"
        #     ),
        #     inline=False
        # )
        # embed.add_field(
        #     name="\u200b",
        #     value=(
        #         "`22 Hours` → ☄️ Mythic Meteor\n"
        #         "`22 Hours` → <:item_glue:1464852440527405056> Glue Dispenser"
        #     ),
        #     inline=False
        # )
        
        return embed
    # ====================================================================
    
    #? ------------------------ Row 1: 3 buttons -------------------------
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
            panel_name="station_base",
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
            panel_name="station_base",
            reminder_item_name="Honey Storm",
        )
    # ====================================================================
    @discord.ui.button(
        label="Stickbug", 
        emoji="<:sticker_nymph:1465764975778861178>",
        custom_id="mob_bosses:stickbug",
        row=0
    )
    async def boss_stickbug_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="stickbug",
            item_emoji="<:sticker_nymph:1465764975778861178>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="mob_bosses",
            reminder_item_name="Stickbug",
        )
    # ====================================================================

    #? ------------------------ Row 2: 2 buttons -------------------------
    @discord.ui.button(
        label="King Beetle",
        emoji="🐞",
        custom_id="mob_bosses:king_beetle",
        row=1
    )
    async def boss_king_beetle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="kingbeetle",
            item_emoji="🐞",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="mob_bosses",
            reminder_item_name="King Beetle",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Tunnel Bear",
        emoji="<:sticker_stretchedbear:1465765080468558090>",
        custom_id="mob_bosses:tunnel_bear",
        row=1
    )
    async def boss_tunnel_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="tunnelbear",
            item_emoji="<:sticker_stretchedbear:1465765080468558090>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="mob_bosses",
            reminder_item_name="Tunnel Bear",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Coconut Crab",
        emoji="🦀",
        custom_id="mob_bosses:coconut_crab",
        row=1
    )
    async def boss_coconut_crab_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="coconutcrab",
            item_emoji="🦀",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="mob_bosses",
            reminder_item_name="Coconut Crab",
            apply_cooldown_reduction=True,
        )
    # ====================================================================
    @discord.ui.button(
        label="Stump Snail",
        emoji="<:sticker_snail:1465765046301757555>",
        custom_id="mob_bosses:stump_snail",
        row=1
    )
    async def boss_stump_snail_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="stumpsnail",
            item_emoji="<:sticker_snail:1465765046301757555>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="mob_bosses",
            reminder_item_name="Stump Snail",
            apply_cooldown_reduction=True,
        )
    # ====================================================================

    #? ------------------------ Row 3: 4 buttons -------------------------
    @discord.ui.button(
        label="Snow Bear",
        emoji=discord.PartialEmoji(name="sticker_snowbear", id=1465028535629643867),
        custom_id="station_beesmas:snow_bear",
        row=2
    )
    async def snow_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="snowbear",
            item_emoji="<:sticker_snowbear:1465028535629643867>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="station_beesmas",
            reminder_item_name="Snow Bear",
        )
    # ====================================================================
    @discord.ui.button(
        label="Robo Party Cake",
        emoji=discord.PartialEmoji(name="sticker_partyrobo", id=1465026484300419074),
        custom_id="station_beesmas:robo_party",
        row=2
    )
    async def robo_party_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="roboparty",
            item_emoji="<:sticker_partyrobo:1465026484300419074>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="station_beesmas",
            reminder_item_name="Robo Party",
        )
    # ====================================================================
    @discord.ui.button(
        label="Honeyday Candle",
        emoji=discord.PartialEmoji(name="beequip_candle", id=1465028727519051998),
        custom_id="station_beesmas:riley_candle",
        row=2
    )
    async def riley_candle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="candle",
            item_emoji="<:beequip_candle:1465028727519051998>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="station_beesmas",
            reminder_item_name="Honeyday Candle",
        )
    # ====================================================================
    @discord.ui.button(
        label="Samovar",
        emoji=discord.PartialEmoji(name="sticker_yellowmug", id=1465026671282356264),
        custom_id="station_beesmas:samovar",
        row=2
    )
    async def samovar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="samovar",
            item_emoji="<:sticker_yellowmug:1465026671282356264>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="station_beesmas",
            reminder_item_name="Samovar",
        )
    # ====================================================================

    #? ------------------------ Row 4: 2 buttons -------------------------
    @discord.ui.button(
        label="Mythic Meteor",
        emoji="☄️",
        custom_id="station_base:meteor",
        row=3
    )
    async def meteor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="meteor",
            item_emoji="☄️",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="station_base",
            reminder_item_name="Mythic Meteor",
        )
    # ====================================================================
    @discord.ui.button(
        label="Glue Dispenser",
        emoji=discord.PartialEmoji(name="item_glue", id=1464852440527405056),
        custom_id="station_base:glue_dispenser",
        row=3
    )
    async def glue_dispenser_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_panel_click(
            interaction=interaction,
            item_key="glue_dispenser",
            item_emoji="<:item_glue:1464852440527405056>",
            cooldown_map=COOLDOWN_MAP,
            reminder_service=reminder_service,
            panel_name="station_base",
            reminder_item_name="Glue Dispenser",
        )



# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class FavoritePanel(commands.Cog):
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
                        view = FavoritePanelView()
                        await message.edit(view=view)
                        print(f"Restored Beesmas Station panel in #{channel.name} (Message ID: {message_id})")
                    except discord.NotFound:
                        # Message was deleted, create a new one
                        embed = FavoritePanelView.get_embed()
                        view = FavoritePanelView()
                        new_message = await channel.send(embed=embed, view=view)
                        save_panel_message(PANEL_NAME, channel_id, new_message.id)
                        print(f"Recreated Beesmas Station panel in #{channel.name} (old message was deleted)")
                    except Exception as e:
                        print(f"Error restoring panel message: {e}")
            except Exception as e:
                print(f"Error loading panel message info: {e}")

    @discord.app_commands.command(name="setup-favorite-panel-frosty", description="Set up the Favorite panel by Frosty")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Favorite panel"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = FavoritePanelView.get_embed()
            view = FavoritePanelView()
            
            sent_msg = await interaction.channel.send(embed=embed, view=view)

            try:
                save_panel_message(PANEL_NAME, interaction.channel.id, sent_msg.id)
            except Exception as e:
                print(f"Warning: failed to save panel message for {PANEL_NAME}: {e}")
            
            await interaction.followup.send(
                "✅ Favorite panel has been set up successfully!",
                ephemeral=True
            )
            print(f"Panel '{PANEL_NAME}' set up in #{interaction.channel.name}")

        except Exception as e:
            print(f"Error setting up panel '{PANEL_NAME}': {e}")
            await interaction.followup.send(
                f"❌ Error setting up panel '{PANEL_NAME}': {str(e)}",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    bot.add_view(FavoritePanelView())
    await bot.add_cog(FavoritePanel(bot))
