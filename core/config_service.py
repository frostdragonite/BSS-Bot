"""
Centralized Configuration Service
Manages all panel configurations in a single panel_config.json file
"""
import json
import os
from typing import Optional, Dict, Any

CONFIG_FILE = "panel_config.json"

def load_config() -> Dict[str, Any]:
    """Load the entire configuration file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return {}
    return {
        "destination_channel_id": None,
        "panels": {},
        "reminders": {}
    }

def save_config(config: Dict[str, Any]):
    """Save the entire configuration file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Error saving config: {e}")

def get_destination_channel_id() -> Optional[int]:
    """Get the destination channel ID"""
    config = load_config()
    return config.get("destination_channel_id")

def set_destination_channel_id(channel_id: int):
    """Set the destination channel ID"""
    config = load_config()
    config["destination_channel_id"] = channel_id
    save_config(config)

def get_panel_message(panel_name: str) -> Optional[Dict[str, Any]]:
    """Get panel message info for a specific panel"""
    config = load_config()
    panels = config.get("panels", {})
    return panels.get(panel_name)

def save_panel_message(panel_name: str, channel_id: int, message_id: int):
    """Save panel message info for a specific panel"""
    config = load_config()
    if "panels" not in config:
        config["panels"] = {}
    
    config["panels"][panel_name] = {
        "channel_id": channel_id,
        "message_id": message_id
    }
    save_config(config)

def get_reminders(panel_name: str) -> Dict[str, Any]:
    """Get reminders for a specific panel"""
    config = load_config()
    reminders = config.get("reminders", {})
    return reminders.get(panel_name, {})

def save_reminders(panel_name: str, reminders: Dict[str, Any]):
    """Save reminders for a specific panel"""
    config = load_config()
    if "reminders" not in config:
        config["reminders"] = {}
    
    config["reminders"][panel_name] = reminders
    save_config(config)

def get_user_cooldown_reduction(user_id: int, panel_name: str = None) -> int:
    """Get cooldown reduction percentage for a user for a specific panel (0-50)"""
    config = load_config()
    user_settings = config.get("user_settings", {})
    user_data = user_settings.get(str(user_id), {})
    
    if panel_name:
        # Panel-specific cooldown reduction
        panel_reductions = user_data.get("panel_cooldown_reductions", {})
        return panel_reductions.get(panel_name, 0)
    else:
        # Global fallback (for backwards compatibility)
        return user_data.get("cooldown_reduction", 0)

def set_user_cooldown_reduction(user_id: int, percentage: int, panel_name: str = None):
    """Set cooldown reduction percentage for a user for a specific panel (0-50)"""
    if not 0 <= percentage <= 50:
        raise ValueError("Cooldown reduction must be between 0 and 50")
    
    config = load_config()
    if "user_settings" not in config:
        config["user_settings"] = {}
    
    if str(user_id) not in config["user_settings"]:
        config["user_settings"][str(user_id)] = {}
    
    if panel_name:
        # Panel-specific cooldown reduction
        if "panel_cooldown_reductions" not in config["user_settings"][str(user_id)]:
            config["user_settings"][str(user_id)]["panel_cooldown_reductions"] = {}
        config["user_settings"][str(user_id)]["panel_cooldown_reductions"][panel_name] = percentage
    else:
        # Global cooldown reduction
        config["user_settings"][str(user_id)]["cooldown_reduction"] = percentage
    
    save_config(config)


def get_user_timer_flags(user_id: int) -> Dict[str, bool]:
    """Get all timer flags for a user (returns dict of timer_name -> bool)"""
    config = load_config()
    user_settings = config.get("user_settings", {})
    user_data = user_settings.get(str(user_id), {})
    return user_data.get("timers", {})


def is_user_timer_enabled(user_id: int, timer_name: str) -> bool:
    """Return True if the specified timer is enabled for the user"""
    timers = get_user_timer_flags(user_id)
    return bool(timers.get(timer_name, False))


def toggle_user_timer_flag(user_id: int, timer_name: str) -> bool:
    """Toggle a user's timer flag and return the new state (True=enabled)"""
    config = load_config()
    if "user_settings" not in config:
        config["user_settings"] = {}

    if str(user_id) not in config["user_settings"]:
        config["user_settings"][str(user_id)] = {}

    if "timers" not in config["user_settings"][str(user_id)]:
        config["user_settings"][str(user_id)]["timers"] = {}

    current = config["user_settings"][str(user_id)]["timers"].get(timer_name, False)
    new_state = not bool(current)
    config["user_settings"][str(user_id)]["timers"][timer_name] = new_state
    save_config(config)
    return new_state


def get_users_with_timer_flag(timer_name: str) -> list:
    """Return list of user IDs (ints) who have the timer flag enabled"""
    config = load_config()
    user_settings = config.get("user_settings", {})
    result = []
    for user_id_str, data in user_settings.items():
        timers = data.get("timers", {})
        if timers.get(timer_name):
            try:
                result.append(int(user_id_str))
            except ValueError:
                continue
    return result