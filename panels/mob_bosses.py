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
PANEL_NAME = "mob_bosses"  # Panel identifier for config storage

# Cooldown configuration for each boss
# You can use days, hours, and minutes in any combination
# Examples:
#   CooldownConfig(days=36)                    # 36 days
#   CooldownConfig(hours=1, minutes=30)        # 1 hour 30 minutes
#   CooldownConfig(days=2, hours=5, minutes=15) # 2 days, 5 hours, 15 minutes
BOSS_COOLDOWNS = {
    "King Beetle": CooldownConfig(days=1),
    "Tunnel Bear": CooldownConfig(days=2),
    "Coconut Crab": CooldownConfig(days=1, hours=12),
    "Stump Snail": CooldownConfig(days=4),
    "Commando Chick": CooldownConfig(minutes=30),
    # "mondochick": CooldownConfig(days=36),  # Special
    "Stickbug": CooldownConfig(days=1, hours=12),
}

# Initialize reminder service (uses centralized config by default)
reminder_service = ReminderService("mob_bosses", use_centralized_config=True)

# ===========================================================================
# ========================= PANEL VIEW =========================
# ===========================================================================
class MobBossesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    #? --------------- Build Embed ---------------
    @staticmethod
    def get_embed():
        """Create and return the embed for this bosses panel"""
        
        embed = discord.Embed(
            title="Boss Respawn Reminders",
            description=(
              "Track boss respawn timers across all base game bosses.\n"
              "Each boss follows a fixed respawn interval after being defeated.\n\n"
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

    #? --------------- Row 1: 4 buttons ---------------
    @discord.ui.button(
      label="King Beetle",
      emoji="🐞",
      custom_id="mob_bosses:king_beetle",
      row=0
    )
    async def boss_king_beetle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "King Beetle")

    @discord.ui.button(
      label="Tunnel Bear",
      emoji="🐻",
      custom_id="mob_bosses:tunnel_bear",
      row=0
    )
    async def boss_tunnel_bear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Tunnel Bear")

    @discord.ui.button(
      label="Coconut Crab",
      emoji="🦀",
      custom_id="mob_bosses:coconut_crab",
      row=0
    )
    async def boss_coconut_crab_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Coconut Crab")

    @discord.ui.button(
      label="Stump Snail",
      emoji="🐌",
      custom_id="mob_bosses:stump_snail",
      row=0
    )
    async def boss_stump_snail_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stump Snail")

    #? --------------- Row 2: 2 buttons ---------------
    @discord.ui.button(
      label="Commando Chick",
      emoji="💣",
      custom_id="mob_bosses:commando_chick",
      row=1
    )
    async def boss_commando_chick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Commando Chick")
        
    @discord.ui.button(
      label="Mondo Chick",
      emoji="🐣",
      custom_id="mob_bosses:mondo_chick",
      row=1
    )
    async def boss_mondo_chick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Mondo Chick")

    @discord.ui.button(
      label="Stickbug", 
      emoji="🦗",
      custom_id="mob_bosses:stickbug",
      row=1
    )
    async def boss_stickbug_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "Stickbug")
    
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
            # Get cooldown for bosses
            cooldown = BOSS_COOLDOWNS.get(item)
            
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
            
            print(f"Mob Bosses: {interaction.user.name} set reminder for {item} - reminder on {reminder_time_str} ({cooldown_str})")
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
            print(f"Error in mob bosses panel: {e}")

# ===========================================================================
# ========================= COG SETUP =========================
# ===========================================================================
class MobBosses(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register this panel's reminder service with the global checker
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("mob_bosses", reminder_service)

    #? --------------- Setup Panel Command ---------------
    @discord.app_commands.command(name="setup-panel-mob-bosses", description="Set up the Bosses panel")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(self, interaction: discord.Interaction):
        """Set up the Bosses panel"""
        embed = MobBossesView.get_embed()
        view = MobBossesView()
        await interaction.response.send_message(embed=embed, view=view)
        
        # Get the message that was sent
        message = await interaction.original_response()
        
        # Save panel message info for persistence
        save_panel_message(PANEL_NAME, interaction.channel.id, message.id)

        print(f"Bosses panel set up in #{interaction.channel.name} by {interaction.user.name}")

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
