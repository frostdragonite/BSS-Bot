from typing import Dict, Optional
from datetime import datetime
import discord
from discord.ui import Button, View
from core.config_service import get_destination_channel_id, get_user_cooldown_reduction
from core.reminder_service import ReminderService, CooldownConfig

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
    
    try:
        # Check if user already has a reminder for this item
        existing_reminder = reminder_service.get_reminder_info(interaction.user.id, item_key)
        
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
        
        # Create reminder using the core service with cooldown reduction
        reminder_time = reminder_service.create_reminder(
            user_id=interaction.user.id,
            item_key=item_key,
            item_emoji=item_emoji,
            reminder_item_name=reminder_item_name,
            cooldown=cooldown,
            channel_id=destination_id,
            username=interaction.user.name,
            cooldown_reduction_percent=cooldown_reduction
        )
        
        # Format reminder time for display
        reminder_time_str = reminder_service.format_reminder_human_time(reminder_time)
        cooldown_str = reminder_service.format_reminder_human_time(reminder_time)

        reminder_time_unix_str = reminder_service.format_reminder_unix_time(reminder_time, type='F')
        cooldown_unix_str = reminder_service.format_reminder_unix_time(reminder_time, type='R')
        
        # Format success message
        success_message_template: str = "✅ Reminder set for **{success_item}**!\n⏱️ You'll be pinged on {reminder_time_unix_str} (in {cooldown_unix_str})."
        success_message = success_message_template.format(
            success_item=success_item_name or reminder_item_name,
            reminder_time_unix_str=reminder_time_unix_str,
            cooldown_unix_str=cooldown_unix_str
        )
        
        await interaction.response.send_message(
            success_message,
            ephemeral=True
        )
        
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
        success_item_name: Optional[str] = None,
        apply_cooldown_reduction: bool = False
    ):
        super().__init__()
        self.user_id = user_id
        self.item_key = item_key
        self.item_emoji = item_emoji
        self.reminder_item_name = reminder_item_name
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
            reminders = self.reminder_service.load_reminders()
            reminder_key = f"{self.user_id}:{self.item_key}"
            
            if reminder_key in reminders:
                del reminders[reminder_key]
                self.reminder_service.save_reminders(reminders)
            
            await interaction.response.send_message(
                f"❌ Reminder for **{self.reminder_item_name}** has been cancelled.",
                ephemeral=True
            )
            
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
                cooldown_reduction_percent=cooldown_reduction
            )
            
            # Format reminder time for display
            reminder_time_unix_str = self.reminder_service.format_reminder_unix_time(reminder_time, type='F')
            cooldown_unix_str = self.reminder_service.format_reminder_unix_time(reminder_time, type='R')
            
            # Format success message
            success_message_template: str = "🔄 Reminder reset for **{success_item}**!\n⏱️ You'll be pinged on {reminder_time} (in {cooldown})."
            success_message = success_message_template.format(
                success_item=self.success_item_name or self.reminder_item_name,
                reminder_time=reminder_time_unix_str,
                cooldown=cooldown_unix_str
            )
            
            await interaction.response.send_message(
                success_message,
                ephemeral=True
            )
            
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
    success_item_name: Optional[str] = None,
    apply_cooldown_reduction: bool = False
) -> None:
    # ====================================================================
    """Show prompt for user when reminder already exists"""
    # ====================================================================
    try:
        reminder_time = datetime.fromisoformat(existing_reminder["reminder_time"])
        reminder_time_unix_str = reminder_service.format_reminder_unix_time(reminder_time, type='F')
        reminder_time_human_str = reminder_service.format_reminder_unix_time(reminder_time, type='F')
        
        message_template = (
            f"⏰ You already have a reminder set for **{reminder_item_name}**!\n"
            f"⏱️ Currently set to trigger on {reminder_time_unix_str} ({reminder_time_human_str})\n\n"
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
            success_item_name=success_item_name,
            apply_cooldown_reduction=apply_cooldown_reduction
        )
        
        await interaction.response.send_message(
            message_template,
            view=view,
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )
        print(f"Error in show_reminder_exists_prompt: {e}")
# ========================================================================
