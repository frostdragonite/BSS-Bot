from typing import Dict, Optional, Tuple, Union
from datetime import datetime
import discord
from discord.ui import Button, View
from core.config_service import get_destination_channel_id, get_user_cooldown_reduction
from core.reminder_service import ReminderService, CooldownConfig

# Cache last ephemeral message ID per (user_id, channel_id) so we can try to delete it
# when the user sets another reminder (reduces clutter). Discord may not allow deleting
# ephemeral messages via API; we try and ignore errors.
_last_ephemeral: Dict[Tuple[int, int], int] = {}  # (user_id, channel_id) -> message_id


def get_role_emoji(user: Union[discord.User, discord.Member], guild: Optional[discord.Guild] = None) -> Optional[str]:
    """
    Get emoji based on user's highest role icon (if available).
    
    Args:
        user: Discord user or member
        guild: Guild to check roles in (if user is not a Member)
    
    Returns:
        Role icon emoji string (custom emoji format) or None if no role icon found
    """
    # If user is a Member, we can check roles directly
    if isinstance(user, discord.Member) and user.guild:
        # Get roles sorted by position (highest first), excluding @everyone
        roles = [role for role in user.roles if role.name != "@everyone"]
        if roles:
            # Sort by position (highest first)
            roles.sort(key=lambda r: r.position, reverse=True)
            # Check each role for an icon/emoji
            for role in roles:
                if role.icon:
                    # Role has a custom icon (image)
                    # Discord.py doesn't expose icon URL directly, but we can use the icon property
                    # For custom emoji icons, we'd need the emoji object
                    if hasattr(role.icon, 'url'):
                        # This is an image icon, not an emoji
                        continue
                if role.unicode_emoji:
                    # Role has a Unicode emoji
                    return role.unicode_emoji
                # Check if role has a custom emoji icon (requires fetching)
                # Note: Role.icon can be Emoji, PartialEmoji, or Asset
                if role.icon and hasattr(role.icon, 'name') and hasattr(role.icon, 'id'):
                    # Custom emoji icon
                    return f"<:{role.icon.name}:{role.icon.id}>"
    
    # If user is not a Member but we have guild, try to fetch member
    if guild and isinstance(user, discord.User):
        # Note: This would require async, but we keep this function sync for simplicity
        # In practice, if you need this, you'd need to make the function async
        pass
    
    return None


async def get_user_role_emoji(user: Union[discord.User, discord.Member], guild: Optional[discord.Guild] = None) -> Optional[str]:
    """
    Get emoji based on user's highest role icon (async version that can fetch member if needed).
    
    Args:
        user: Discord user or member
        guild: Guild to check roles in (if user is not a Member)
    
    Returns:
        Role icon emoji string (custom emoji format) or None if no role icon found
    """
    # If user is a Member, we can check roles directly
    if isinstance(user, discord.Member) and user.guild:
        roles = [role for role in user.roles if role.name != "@everyone"]
        if roles:
            roles.sort(key=lambda r: r.position, reverse=True)
            for role in roles:
                # Check for Unicode emoji first (simplest)
                if role.unicode_emoji:
                    return role.unicode_emoji
                # Check for custom emoji icon
                if role.icon:
                    # Try to get emoji representation
                    try:
                        # If it's a custom emoji, format it
                        if hasattr(role.icon, 'name') and hasattr(role.icon, 'id'):
                            return f"<:{role.icon.name}:{role.icon.id}>"
                    except Exception:
                        pass
    
    # If user is not a Member but we have guild, try to fetch member
    if guild and isinstance(user, discord.User):
        try:
            member = await guild.fetch_member(user.id)
            if member:
                return await get_user_role_emoji(member, guild)
        except Exception:
            pass
    
    return None


async def _try_delete_last_ephemeral(interaction: discord.Interaction) -> None:
    """Try to delete the last ephemeral message we sent to this user in this channel."""
    key = (interaction.user.id, interaction.channel_id)
    if key not in _last_ephemeral:
        return
    msg_id = _last_ephemeral.pop(key, None)
    if not msg_id or not interaction.channel:
        return
    try:
        msg = await interaction.channel.fetch_message(msg_id)
        if msg and msg.author == interaction.client.user:
            await msg.delete()
    except Exception:
        pass  # Ephemeral messages often cannot be deleted via API; ignore


# ========================================================================
async def handle_panel_click(
    interaction: discord.Interaction,
    item_key: str,
    item_emoji: str,
    cooldown_map: Dict[str, CooldownConfig],
    reminder_service: ReminderService,
    panel_name: str,
    reminder_item_name: str,
    success_item_name: Optional[str] = None,
    apply_cooldown_reduction: bool = False
) -> None:
    # --------------------------------------------------------------------
    """
    Centralized handler for panel button clicks.
    
    Args:
        interaction: Discord interaction from button click
        item_key: The key name of the item/boss/station that was clicked
        item_emoji: The emoji of the item/boss/station that was clicked
        reminder_item_name: The item name that will be displayed in message
        cooldown_map: Dictionary mapping item names to CooldownConfig objects
        reminder_service: The ReminderService instance for creating reminders
        panel_name: Name of the panel for logging purposes
        success_item: The name of the item that will be in success message
        apply_cooldown_reduction: Whether to apply user's cooldown reduction (default: False)
    """
    # --------------------------------------------------------------------
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
    
    # When Favorite panel forwards to another panel (e.g. mob_bosses), store reminder under that panel
    storage_panel_override = panel_name if panel_name != reminder_service.panel_name else None

    try:
        # Check if user already has a reminder for this item (in the storage panel)
        existing_reminder = reminder_service.get_reminder_info(
            interaction.user.id, item_key, panel_name_override=storage_panel_override
        )

        if existing_reminder:
            # Reminder already exists - show options to cancel or reset
            await show_reminder_exists_prompt(
                interaction=interaction,
                item_emoji=item_emoji,
                reminder_item_name=reminder_item_name,
                existing_reminder=existing_reminder,
                user_id=interaction.user.id,
                item_key=item_key,
                cooldown_map=cooldown_map,
                reminder_service=reminder_service,
                destination_id=destination_id,
                panel_name=panel_name,
                storage_panel_name=storage_panel_override,
                success_item_name=success_item_name,
                apply_cooldown_reduction=apply_cooldown_reduction
            )
            return

        # Get cooldown for this specific item
        cooldown = cooldown_map.get(item_key)

        # Get user's cooldown reduction if applicable
        cooldown_reduction = 0
        if apply_cooldown_reduction:
            cooldown_reduction = get_user_cooldown_reduction(interaction.user.id, panel_name)

        # Create reminder using the core service with cooldown reduction (under storage panel)
        reminder_time = reminder_service.create_reminder(
            user_id=interaction.user.id,
            item_key=item_key,
            item_emoji=item_emoji,
            reminder_item_name=reminder_item_name,
            cooldown=cooldown,
            channel_id=destination_id,
            username=interaction.user.name,
            cooldown_reduction_percent=cooldown_reduction,
            storage_panel_override=storage_panel_override
        )
        
        # Format reminder time for display
        reminder_time_str = reminder_service.format_reminder_human_time(reminder_time)
        cooldown_str = reminder_service.format_reminder_human_time(reminder_time)

        reminder_time_unix_str = reminder_service.format_reminder_unix_time(reminder_time, type='F')
        cooldown_unix_str = reminder_service.format_reminder_unix_time(reminder_time, type='R')
        display_name = success_item_name or reminder_item_name

        # Try to delete previous ephemeral message for this user in this channel (if any)
        await _try_delete_last_ephemeral(interaction)

        # Format success message with emojis
        success_message = (
            f"✅ Reminder set for {item_emoji} **{display_name}**!\n"
            f"⏱️ You'll be pinged on {reminder_time_unix_str} (in {cooldown_unix_str})."
        )

        await interaction.response.send_message(
            success_message,
            ephemeral=True
        )
        try:
            orig = await interaction.original_response()
            if orig and getattr(orig, "id", None):
                _last_ephemeral[(interaction.user.id, interaction.channel_id)] = orig.id
        except Exception:
            pass
        
        print(f"{panel_name}: {interaction.user.name} set reminder for {item_key} - reminder on {reminder_time_str} ({cooldown_str})")
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )
        print(f"Error in {panel_name} panel: {e}")
# ========================================================================


# ========================================================================
# Reminder Action View
# ========================================================================
class ReminderActionView(View):
    # --------------------------------------------------------------------
    """View with Cancel and Reset buttons for existing reminders"""
    # ====================================================================
    def __init__(
        self, 
        user_id: int,
        item_key: str,
        item_emoji: str,
        reminder_item_name: str,
        existing_reminder: dict,
        cooldown_map: Dict[str, CooldownConfig],
        reminder_service: ReminderService,
        destination_id: int,
        panel_name: str,
        storage_panel_name: Optional[str] = None,
        success_item_name: Optional[str] = None,
        apply_cooldown_reduction: bool = False
    ):
        super().__init__()
        self.user_id = user_id
        self.item_key = item_key
        self.item_emoji = item_emoji
        self.reminder_item_name = reminder_item_name
        self.storage_panel_name = storage_panel_name
        self.existing_reminder = existing_reminder
        self.cooldown_map = cooldown_map
        self.reminder_service = reminder_service
        self.destination_id = destination_id
        self.panel_name = panel_name
        self.success_item_name = success_item_name
        self.apply_cooldown_reduction = apply_cooldown_reduction
    # ====================================================================
    

    # ====================================================================
    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger
    )
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        # ----------------------------------------------------------------
        """Cancel the existing reminder"""
        # ----------------------------------------------------------------
        try:
            reminders = self.reminder_service.load_reminders(panel_name_override=self.storage_panel_name)
            reminder_key = f"{self.user_id}:{self.item_key}"
            
            if reminder_key in reminders:
                del reminders[reminder_key]
                self.reminder_service.save_reminders(reminders, panel_name_override=self.storage_panel_name)

            await _try_delete_last_ephemeral(interaction)
            await interaction.response.send_message(
                f"❌ Reminder for {self.item_emoji} **{self.reminder_item_name}** has been cancelled.",
                ephemeral=True
            )
            try:
                orig = await interaction.original_response()
                if orig and getattr(orig, "id", None):
                    _last_ephemeral[(interaction.user.id, interaction.channel_id)] = orig.id
            except Exception:
                pass

            print(f"[{self.panel_name}] {interaction.user.name} cancelled reminder for {self.item_key}")
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error cancelling reminder: {str(e)}",
                ephemeral=True
            )
            print(f"Error cancelling reminder: {e}")
    # ====================================================================
    
    
    # ====================================================================
    @discord.ui.button(
        label="Reset",
        style=discord.ButtonStyle.primary
    )
    async def reset_button(self, interaction: discord.Interaction, button: Button):
        # ----------------------------------------------------------------
        """Reset the reminder to current time"""
        # ----------------------------------------------------------------
        try:
            # Get cooldown for this specific item
            cooldown = self.cooldown_map.get(self.item_key)
            
            # Get user's cooldown reduction if applicable
            cooldown_reduction = 0
            if self.apply_cooldown_reduction:
                cooldown_reduction = get_user_cooldown_reduction(self.user_id, self.panel_name)
            
            # Create new reminder (overwrites existing) with cooldown reduction
            reminder_time = self.reminder_service.create_reminder(
                user_id=self.user_id,
                item_key=self.item_key,
                item_emoji=self.item_emoji,
                reminder_item_name=self.reminder_item_name,
                cooldown=cooldown,
                channel_id=self.destination_id,
                username=interaction.user.name,
                cooldown_reduction_percent=cooldown_reduction,
                storage_panel_override=self.storage_panel_name
            )
            
            # Format reminder time for display
            reminder_time_unix_str = self.reminder_service.format_reminder_unix_time(reminder_time, type='F')
            cooldown_unix_str = self.reminder_service.format_reminder_unix_time(reminder_time, type='R')
            
            # Try to delete previous ephemeral, then send new message with emojis
            await _try_delete_last_ephemeral(interaction)
            display_name = self.success_item_name or self.reminder_item_name
            success_message = (
                f"🔄 Reminder reset for {self.item_emoji} **{display_name}**!\n"
                f"⏱️ You'll be pinged on {reminder_time_unix_str} (in {cooldown_unix_str})."
            )
            await interaction.response.send_message(
                success_message,
                ephemeral=True
            )
            try:
                orig = await interaction.original_response()
                if orig and getattr(orig, "id", None):
                    _last_ephemeral[(interaction.user.id, interaction.channel_id)] = orig.id
            except Exception:
                pass

            print(f"[{self.panel_name}] {interaction.user.name} reset reminder for {self.item_key}")
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error resetting reminder: {str(e)}",
                ephemeral=True
            )
            print(f"Error resetting reminder: {e}")
    # ========================================================================


# ========================================================================
async def show_reminder_exists_prompt(
    interaction: discord.Interaction,
    item_emoji: str,
    reminder_item_name: str,
    existing_reminder: dict,
    user_id: int,
    item_key: str,
    cooldown_map: Dict[str, CooldownConfig],
    reminder_service: ReminderService,
    destination_id: int,
    panel_name: str,
    storage_panel_name: Optional[str] = None,
    success_item_name: Optional[str] = None,
    apply_cooldown_reduction: bool = False
) -> None:
    # ====================================================================
    """Show prompt for user when reminder already exists"""
    # ====================================================================
    try:
        reminder_time = datetime.fromisoformat(existing_reminder["reminder_time"])
        reminder_time_unix_str = reminder_service.format_reminder_unix_time(reminder_time, type='F')

        await _try_delete_last_ephemeral(interaction)

        message_template = (
            f"⏰ You already have a reminder set for {item_emoji} **{reminder_item_name}**!\n"
            f"⏱️ Currently set to trigger on {reminder_time_unix_str}\n"
            f"*Dismiss this message to keep the existing reminder*"
        )

        view = ReminderActionView(
            user_id=user_id,
            item_key=item_key,
            item_emoji=item_emoji,
            reminder_item_name=reminder_item_name,
            existing_reminder=existing_reminder,
            cooldown_map=cooldown_map,
            reminder_service=reminder_service,
            destination_id=destination_id,
            panel_name=panel_name,
            storage_panel_name=storage_panel_name,
            success_item_name=success_item_name,
            apply_cooldown_reduction=apply_cooldown_reduction
        )

        await interaction.response.send_message(
            message_template,
            view=view,
            ephemeral=True
        )
        try:
            orig = await interaction.original_response()
            if orig and getattr(orig, "id", None):
                _last_ephemeral[(interaction.user.id, interaction.channel_id)] = orig.id
        except Exception:
            pass
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )
        print(f"Error in show_reminder_exists_prompt: {e}")
# ========================================================================
