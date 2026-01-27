"""
Core Reminder Service
A reusable service for managing reminders with flexible time units (days, hours, minutes).
Can be used by any panel in the bot.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from discord.ext import tasks, commands
import discord


class CooldownConfig:
    """Configuration for a cooldown period"""
    def __init__(self, days: int = 0, hours: int = 0, minutes: int = 0):
        """
        Create a cooldown configuration.
        
        Args:
            days: Number of days
            hours: Number of hours
            minutes: Number of minutes
            
        Example:
            # 1 hour 30 minutes
            cooldown = CooldownConfig(hours=1, minutes=30)
            
            # 36 days
            cooldown = CooldownConfig(days=36)
            
            # 2 days, 5 hours, 15 minutes
            cooldown = CooldownConfig(days=2, hours=5, minutes=15)
        """
        self.days = days
        self.hours = hours
        self.minutes = minutes
    
    def to_timedelta(self) -> timedelta:
        """Convert to Python timedelta object"""
        return timedelta(days=self.days, hours=self.hours, minutes=self.minutes)
    
    def total_seconds(self) -> float:
        """Get total cooldown in seconds"""
        return self.to_timedelta().total_seconds()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON storage"""
        return {
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CooldownConfig':
        """Create from dictionary"""
        return cls(
            days=data.get("days", 0),
            hours=data.get("hours", 0),
            minutes=data.get("minutes", 0)
        )
    
    def __str__(self) -> str:
        """Human-readable string representation"""
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


class ReminderService:
    """Core service for managing reminders across all panels"""
    
    def __init__(self, panel_name: str, use_centralized_config: bool = True):
        """
        Initialize reminder service for a panel.
        
        Args:
            panel_name: Name of the panel (for logging/debugging)
            use_centralized_config: If True, use centralized panel_config.json. If False, use separate file.
        """
        self.panel_name = panel_name
        self.use_centralized_config = use_centralized_config
        
        if not use_centralized_config:
            # Legacy mode: use separate file
            self.reminders_file = f"{panel_name.lower().replace(' ', '_')}_reminders.json"
    
    def load_reminders(self) -> Dict:
        """Load reminders from storage"""
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
    
    def save_reminders(self, reminders: Dict):
        """Save reminders to storage"""
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
    
    def create_reminder(
        self,
        user_id: int,
        item_name: str,
        cooldown: CooldownConfig,
        channel_id: int,
        username: str = None
    ) -> datetime:
        """
        Create a new reminder.
        
        Args:
            user_id: Discord user ID
            item_name: Name of the item (e.g., "Plastic", "Candy")
            cooldown: CooldownConfig object
            channel_id: Channel ID where reminder should be sent
            username: Optional username for logging
            
        Returns:
            datetime: When the reminder will trigger
        """
        reminders = self.load_reminders()
        reminder_key = f"{user_id}:{item_name}"
        
        reminder_time = datetime.now() + cooldown.to_timedelta()
        
        reminders[reminder_key] = {
            "user_id": str(user_id),
            "username": username or str(user_id),
            "item": item_name,
            "reminder_time": reminder_time.isoformat(),
            "channel_id": str(channel_id),
            "created_at": datetime.now().isoformat(),
            "cooldown": cooldown.to_dict()
        }
        
        self.save_reminders(reminders)
        return reminder_time
    
    def format_reminder_time(self, reminder_time: datetime) -> str:
        """Format reminder time for display"""
        return reminder_time.strftime("%B %d, %Y at %I:%M %p")
    
    def get_reminder_info(self, user_id: int, item_name: str) -> Optional[Dict]:
        """Get existing reminder info if it exists"""
        reminders = self.load_reminders()
        reminder_key = f"{user_id}:{item_name}"
        return reminders.get(reminder_key)


class ReminderChecker(commands.Cog):
    """Background task manager for checking and sending reminders"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_interval = 1.0  # Check every minute
        self.reminder_services: Dict[str, ReminderService] = {}
        self.reminder_check.start()
    
    def register_service(self, panel_name: str, service: ReminderService):
        """Register a reminder service to check"""
        self.reminder_services[panel_name] = service
        print(f"Registered reminder service for {panel_name}")
    
    def cog_unload(self):
        """Stop the reminder check task when cog is unloaded"""
        self.reminder_check.cancel()
    
    @tasks.loop(minutes=1.0)
    async def reminder_check(self):
        """Check for expired reminders and ping users"""
        if not self.bot.is_ready():
            return
        
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
                        item = reminder_data["item"]
                        
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            user = self.bot.get_user(user_id)
                            if user:
                                await channel.send(
                                    f"🔔 {user.mention} Your **{item}** cooldown is ready! "
                                    f"You can now use it again."
                                )
                                print(f"[{panel_name}] Reminder sent: {reminder_data.get('username', user_id)} - {item} ready")
                            else:
                                # User not cached, use mention format
                                await channel.send(
                                    f"🔔 <@{user_id}> Your **{item}** cooldown is ready! "
                                    f"You can now use it again."
                                )
                                print(f"[{panel_name}] Reminder sent (user not cached): {user_id} - {item} ready")
                        
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
    
    @reminder_check.before_loop
    async def before_reminder_check(self):
        """Wait until bot is ready before starting the task"""
        await self.bot.wait_until_ready()


# Global reminder checker instance (will be initialized in bot.py)
reminder_checker: Optional[ReminderChecker] = None


def get_reminder_checker(bot: commands.Bot) -> ReminderChecker:
    """Get or create the global reminder checker instance"""
    global reminder_checker
    if reminder_checker is None:
        reminder_checker = ReminderChecker(bot)
    return reminder_checker
