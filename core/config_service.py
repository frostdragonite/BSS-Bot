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
