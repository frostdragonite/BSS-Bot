"""
Core Reminder Service
A reusable service for managing reminders with flexible time units (days, hours, minutes).
Can be used by any panel in the bot.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from discord.ext import tasks, commands

# ========================================================================
# Cooldown Configuration - Days, Hours, Minutes
# ========================================================================
class CooldownConfig:
    # --------------------------------------------------------------------
    """
    Create a flexible cooldown configuration that supports days, hours, and minutes.
    
    Parameters
    ------------
    days: Optional[:class:`int`]
        Number of days
    hours: Optional[:class:`int`]
        Number of hours
    minutes: Optional[:class:`int`]
        Number of minutes

    Parameters
    ------------
    1 hour, 30 minutes
        cooldown = `CooldownConfig(hours=1, minutes=30)`
    36 days
        cooldown = `CooldownConfig(days=36)`
    2 days, 5 hours, 15 minutes
        cooldown = `CooldownConfig(days=2, hours=5, minutes=15)`
    """
    # ====================================================================
    def __init__(self, days: int = 0, hours: int = 0, minutes: int = 0):
        self.days = days
        self.hours = hours
        self.minutes = minutes
    # ====================================================================
    

    # ====================================================================
    def to_timedelta(self) -> timedelta:
        # ----------------------------------------------------------------
        """Convert to Python timedelta object"""
        # ----------------------------------------------------------------
        return timedelta(days=self.days, hours=self.hours, minutes=self.minutes)
    # ====================================================================
    

    # ====================================================================
    def total_seconds(self) -> float:
        # ----------------------------------------------------------------
        """Get total cooldown in seconds"""
        # ----------------------------------------------------------------
        return self.to_timedelta().total_seconds()
    # ====================================================================
    

    # ====================================================================
    def to_dict(self) -> dict:
        # ----------------------------------------------------------------
        """Convert to dictionary for JSON storage"""
        # ----------------------------------------------------------------
        return {
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes
        }
    # ====================================================================


    # ====================================================================
    @classmethod
    def from_dict(cls, data: dict) -> 'CooldownConfig':
        # ----------------------------------------------------------------
        """Create from dictionary"""
        # ----------------------------------------------------------------
        return cls(
            days=data.get("days", 0),
            hours=data.get("hours", 0),
            minutes=data.get("minutes", 0)
        )
    # ====================================================================
    

    # ====================================================================
    def __str__(self) -> str:
        # ----------------------------------------------------------------
        """Human-readable string representation"""
        # ----------------------------------------------------------------
        parts = []
        if self.days > 0:
            parts.append(f"{self.days} day{'s' if self.days != 1 else ''}")
        if self.hours > 0:
            parts.append(f"{self.hours} hour{'s' if self.hours != 1 else ''}")
        if self.minutes > 0:
            parts.append(f"{self.minutes} minute{'s' if self.minutes != 1 else ''}")
        
        if not parts:
            return "0 minutes"
        
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return f"{', '.join(parts[:-1])}, and {parts[-1]}"
    # ====================================================================


# ========================================================================
# Reminder Service
# ========================================================================
class ReminderService:
    # --------------------------------------------------------------------
    """
    Initialize reminder service for a panel.
    
    Args:
        panel_name: Name of the panel (for logging/debugging)
        use_centralized_config: If True, use centralized panel_config.json. If False, use separate file.
    """
    # ====================================================================
    def __init__(self, panel_name: str, use_centralized_config: bool = True):
        self.panel_name = panel_name
        self.use_centralized_config = use_centralized_config
        
        if not use_centralized_config:
            # Legacy mode: use separate file
            self.reminders_file = f"{panel_name.lower().replace(' ', '_')}_reminders.json"
    # ====================================================================
    

    # ====================================================================
    def load_reminders(self) -> Dict:
        # ----------------------------------------------------------------
        """Load reminders from storage"""
        # ----------------------------------------------------------------
        if self.use_centralized_config:
            from core.config_service import get_reminders
            return get_reminders(self.panel_name)
        else:
            # Legacy mode: load from separate file
            if os.path.exists(self.reminders_file):
                try:
                    with open(self.reminders_file, 'r') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading reminders for {self.panel_name}: {e}")
                    return {}
            return {}
    # ====================================================================
    

    # ====================================================================
    def save_reminders(self, reminders: Dict):
        # ----------------------------------------------------------------
        """Save reminders to storage"""
        # ----------------------------------------------------------------
        if self.use_centralized_config:
            from core.config_service import save_reminders
            save_reminders(self.panel_name, reminders)
        else:
            # Legacy mode: save to separate file
            try:
                with open(self.reminders_file, 'w') as f:
                    json.dump(reminders, f, indent=2)
            except IOError as e:
                print(f"Error saving reminders for {self.panel_name}: {e}")
    # ====================================================================

    
    # ====================================================================
    def create_reminder(
        self,
        user_id: int,
        item_key: str,
        item_emoji: str,
        reminder_item_name: str,
        cooldown: CooldownConfig,
        channel_id: int,
        username: str = None,
        cooldown_reduction_percent: int = 0
    ) -> datetime:
        # ----------------------------------------------------------------
        """
        Create a new reminder.
        
        Parameters
        ------------
        user_id: :class:`int`
            Discord user ID
        item_key: :class:`str`
            Key for the item
        item_emoji: :class:`str`
            Emoji of the item, (e.g., 🐞)
        reminder_item_name: :class:`str`
            Name of the item (e.g., "Plastic", "Candy")
        cooldown: :class:`.CooldownConfig`
            CooldownConfig object
        channel_id: :class:`int`
            Channel ID where reminder should be sent
        username: Optional[:class:`str`]
            Optional username for logging
        cooldown_reduction_percent: Optional[:class:`int`]
            Cooldown reduction percentage (0-50). Defaults to 0.
            
        Returns
        ------------
        :class:`datetime`
            When the reminder will trigger
        """
        # ----------------------------------------------------------------
        reminders = self.load_reminders()
        reminder_key = f"{user_id}:{item_key}"
        
        # Apply cooldown reduction if provided
        total_seconds = cooldown.to_timedelta().total_seconds()
        reduced_seconds = total_seconds * (1 - cooldown_reduction_percent / 100)
        reduced_timedelta = timedelta(seconds=reduced_seconds)
        
        reminder_time = datetime.now() + reduced_timedelta
        
        reminders[reminder_key] = {
            "user_id": str(user_id),
            "username": username or str(user_id),
            "item_emoji": item_emoji,
            "reminder_item_name": reminder_item_name,
            "reminder_time": reminder_time.isoformat(),
            "channel_id": str(channel_id),
            "created_at": datetime.now().isoformat(),
            "cooldown": cooldown.to_dict(),
            "cooldown_reduction_percent": cooldown_reduction_percent
        }
        
        self.save_reminders(reminders)
        return reminder_time
    # ====================================================================
    
    
    # ====================================================================
    def _round_up_to_minute(self, dt: datetime) -> datetime:
        # ----------------------------------------------------------------
        """Round up datetime to the next minute"""
        # ----------------------------------------------------------------
        if dt.second > 0 or dt.microsecond > 0:
            # Round up to next minute
            return (dt + timedelta(minutes=1)).replace(second=0, microsecond=0)
        else:
            # Already at the top of a minute
            return dt
    # ====================================================================

    # ====================================================================
    def format_reminder_unix_time(self, reminder_time: datetime, type: str) -> str:
        # ----------------------------------------------------------------
        """Format reminder time for display as Discord timestamp"""
        # ----------------------------------------------------------------
        rounded_time = self._round_up_to_minute(reminder_time)
        unix_timestamp = int(rounded_time.timestamp())
        return f"<t:{unix_timestamp}:{type}>"
    # ====================================================================
    

    # ====================================================================
    def format_reminder_human_time(self, reminder_time: datetime) -> str:
        # ----------------------------------------------------------------
        """Format reminder time for display"""
        # ----------------------------------------------------------------
        rounded_time = self._round_up_to_minute(reminder_time)
        return rounded_time.strftime("%B %d, %Y at %I:%M %p")
    # ====================================================================
    

    # ====================================================================
    def get_reminder_info(self, user_id: int, item_key: str) -> Optional[Dict]:
        # ----------------------------------------------------------------
        """Get existing reminder info if it exists"""
        # ----------------------------------------------------------------
        reminders = self.load_reminders()
        reminder_key = f"{user_id}:{item_key}"
        return reminders.get(reminder_key)
    # ====================================================================


# ========================================================================
# Reminder Checker Background Task
# ========================================================================
class ReminderChecker(commands.Cog):
    # --------------------------------------------------------------------
    """Background task manager for checking and sending reminders"""
    # ====================================================================
    def __init__(self, bot: commands.Bot, check_interval: float = 1.0):
        self.bot = bot
        self.reminder_services: Dict[str, ReminderService] = {}
        self.reminder_check.change_interval(minutes=check_interval)
        self.reminder_check.start()
        # Track last minute processed for timer pings to avoid duplicates
        self._last_timer_minute: Optional[int] = None
    # ====================================================================
    

    # ====================================================================
    def register_service(self, panel_name: str, service: ReminderService):
        # ----------------------------------------------------------------
        """Register a reminder service to check"""
        # ----------------------------------------------------------------
        self.reminder_services[panel_name] = service
        print(f"Registered reminder service for {panel_name}")
    # ====================================================================
    
    
    # ====================================================================
    def cog_unload(self):
        # ----------------------------------------------------------------
        """Stop the reminder check task when cog is unloaded"""
        # ----------------------------------------------------------------
        self.reminder_check.cancel()
    # ====================================================================
    

    # ====================================================================
    @tasks.loop()
    async def reminder_check(self):
        # ----------------------------------------------------------------
        """Check for expired reminders and ping users"""
        # ----------------------------------------------------------------
        if not self.bot.is_ready():
            return

        # ------------------------ Timer pings (global) ------------------------
        try:
            from core.config_service import get_users_with_timer_flag, get_destination_channel_id

            current_time = datetime.now()
            minute = current_time.minute

            # Only process timers once per minute
            if self._last_timer_minute != minute:
                self._last_timer_minute = minute

                destination_id = get_destination_channel_id()
                if destination_id:
                    channel = self.bot.get_channel(destination_id)
                    if channel:
                        # Timer metadata
                        timers = {
                            "mondo_timer": {"emoji": "🐣", "name": "Mondo Timer"},
                            "puffshroom_timer": {"emoji": "<:sticker_puffshroom:1468791392816988293>", "name": "Puffshroom Timer"}
                        }
                        
                        # Check Mondo Timer (every :00)
                        if minute == 0:
                            mondo_users = get_users_with_timer_flag("mondo_timer")
                            if mondo_users:
                                timer_info = timers["mondo_timer"]
                                mentions = " ".join([f"<@{user_id}>" for user_id in mondo_users])
                                unix_timestamp = int(current_time.timestamp())
                                await channel.send(
                                    f"🔔 <t:{unix_timestamp}:t> - {timer_info['emoji']} **{timer_info['name']}** timer is ready!\n"
                                    f"{mentions}"
                                )

                        # Check Puffshroom Timer (every :15 and :45)
                        if minute in (15, 45):
                            puff_users = get_users_with_timer_flag("puffshroom_timer")
                            if puff_users:
                                timer_info = timers["puffshroom_timer"]
                                mentions = " ".join([f"<@{user_id}>" for user_id in puff_users])
                                unix_timestamp = int(current_time.timestamp())
                                await channel.send(
                                    f"🔔 <t:{unix_timestamp}:t> - {timer_info['emoji']} **{timer_info['name']}** timer is ready!\n"
                                    f"{mentions}"
                                )

        except Exception as e:
            print(f"Error during timer check: {e}")

        for panel_name, service in self.reminder_services.items():
            try:
                reminders = service.load_reminders()
                current_time = datetime.now()
                expired_reminders = []
                
                for reminder_key, reminder_data in list(reminders.items()):
                    reminder_time = datetime.fromisoformat(reminder_data["reminder_time"])
                    
                    if current_time >= reminder_time:
                        expired_reminders.append((reminder_key, reminder_data))
                
                # Send reminders for expired ones
                for reminder_key, reminder_data in expired_reminders:
                    try:
                        user_id = int(reminder_data["user_id"])
                        channel_id = int(reminder_data["channel_id"])
                        item_emoji = reminder_data["item_emoji"]
                        item_name = reminder_data["reminder_item_name"]
                        
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            user = self.bot.get_user(user_id)
                            if user:
                                await channel.send(
                                    f"🔔 {user.mention} - {item_emoji} **{item_name}** cooldown is ready!\n"
                                    f"You can now use it again."
                                )
                                print(f"[{panel_name}] Reminder sent: {reminder_data.get('username', user_id)} - {item_name} ready")
                            else:
                                # User not cached, use mention format
                                await channel.send(
                                    f"🔔 <@{user_id}> - {item_emoji} **{item_name}** cooldown is ready!\n"
                                    f"You can now use it again."
                                )
                                print(f"[{panel_name}] Reminder sent (user not cached): {user_id} - {item_name} ready")
                        
                        # Remove expired reminder
                        del reminders[reminder_key]
                        
                    except Exception as e:
                        print(f"[{panel_name}] Error sending reminder for {reminder_key}: {e}")
                        # Remove problematic reminder
                        del reminders[reminder_key]
                
                # Save updated reminders
                if expired_reminders:
                    service.save_reminders(reminders)
                    
            except Exception as e:
                print(f"[{panel_name}] Error in reminder_check: {e}")
    # ====================================================================
    

    # ====================================================================
    @reminder_check.before_loop
    async def before_reminder_check(self):
        # ----------------------------------------------------------------
        """Wait until bot is ready before starting the task"""
        # ----------------------------------------------------------------
        await self.bot.wait_until_ready()
    # ====================================================================


# ========================================================================
def get_reminder_checker(bot: commands.Bot) -> ReminderChecker:
    # --------------------------------------------------------------------
    """Get or create the global reminder checker instance"""
    # --------------------------------------------------------------------
    global reminder_checker
    if reminder_checker is None:
        reminder_checker = ReminderChecker(bot)
    return reminder_checker
# ========================================================================


# Global reminder checker instance (will be initialized in bot.py)
reminder_checker: Optional[ReminderChecker] = None