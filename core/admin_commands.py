"""
Admin slash commands (e.g. dump panel config for backup) and user commands (e.g. my reminders).
"""
from datetime import datetime

import discord
from discord.ext import commands

from core.config_service import CONFIG_FILE, load_config

# Friendly names for embed field titles (Favorite panel omitted; its reminders live under the actual panels)
PANEL_DISPLAY_NAMES = {
    "planter_caustic": "Caustic Planter",
    "planter_swirled": "Swirled Planter",
    "planter_special": "Special Planter Combo",
    "mob_bosses": "Bosses",
    "periodic_timer": "Periodic Timers",
    "station_memory": "Memory Match",
    "station_base": "Base Station",
    "station_beesmas": "Beesmas Station",
}

# Panels to skip in my-reminders (e.g. Favorite is a shortcut; reminders are under other panels)
MY_REMINDERS_SKIP_PANELS = {"favorite_panel"}


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="dump-panel-config",
        description="Send the current panel_config.json file (admin only, for backup)."
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def dump_panel_config(self, interaction: discord.Interaction):
        """Send panel_config.json as a downloadable file."""
        import os
        await interaction.response.defer(ephemeral=True)
        if not os.path.exists(CONFIG_FILE):
            await interaction.followup.send(
                "No panel config file found yet (nothing has been saved).",
                ephemeral=True
            )
            return
        try:
            await interaction.followup.send(
                "Here is your current `panel_config.json`:",
                file=discord.File(CONFIG_FILE, filename="panel_config.json"),
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"Failed to read config file: {e}",
                ephemeral=True
            )

    @discord.app_commands.command(
        name="my-reminders",
        description="List all your active reminders, grouped by panel."
    )
    async def my_reminders(self, interaction: discord.Interaction):
        """Send an ephemeral embed with all reminders for the invoking user."""
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        config = load_config()
        reminders_by_panel = config.get("reminders", {})

        fields = []
        for panel_name, panel_reminders in reminders_by_panel.items():
            if panel_name in MY_REMINDERS_SKIP_PANELS or not isinstance(panel_reminders, dict):
                continue
            entries = []
            for key, data in panel_reminders.items():
                if not isinstance(data, dict) or data.get("user_id") != user_id:
                    continue
                try:
                    reminder_time = data.get("reminder_time")
                    if not reminder_time:
                        continue
                    dt = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))
                    unix_ts = int(dt.timestamp())
                    emoji = data.get("item_emoji", "")
                    item_name = data.get("reminder_item_name", "?")
                    entries.append((unix_ts, f"<t:{unix_ts}:R> - {emoji} {item_name}"))
                except (ValueError, TypeError):
                    continue
            if entries:
                entries.sort(key=lambda e: e[0])
                lines = [e[1] for e in entries]
                display_name = PANEL_DISPLAY_NAMES.get(panel_name, panel_name)
                value = "\n".join(lines)
                if len(value) > 1024:
                    value = value[:1021] + "..."
                fields.append((display_name, value))

        if not fields:
            await interaction.followup.send(
                "You don't have any reminders set.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Your reminders",
            description="All your active reminders by panel.",
            color=discord.Color.blue(),
        )
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
