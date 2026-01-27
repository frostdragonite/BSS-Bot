# Core Reminder Service

A reusable reminder service for all panels that supports flexible time units (days, hours, minutes).

## Centralized Configuration

All panel data is stored in a single `panel_config.json` file:

```json
{
  "destination_channel_id": 123456789,
  "panels": {
    "caustic": {
      "channel_id": 987654321,
      "message_id": 111222333
    },
    "swirled": {
      "channel_id": 987654321,
      "message_id": 444555666
    }
  },
  "reminders": {
    "Caustic Planter": {
      "user123:Plastic": { ... },
      "user456:Candy": { ... }
    }
  }
}
```

## Usage Example

```python
from core.reminder_service import ReminderService, CooldownConfig, get_reminder_checker
from core.config_service import get_destination_channel_id, get_panel_message, save_panel_message

# Initialize service for your panel (uses centralized config by default)
reminder_service = ReminderService("My Panel Name", use_centralized_config=True)

# Define cooldowns for each item
ITEM_COOLDOWNS = {
    "Item 1": CooldownConfig(days=36),                    # 36 days
    "Item 2": CooldownConfig(hours=1, minutes=30),        # 1 hour 30 minutes
    "Item 3": CooldownConfig(days=2, hours=5, minutes=15), # 2 days, 5 hours, 15 minutes
}

# In your button handler:
destination_id = get_destination_channel_id()  # Get from centralized config
cooldown = ITEM_COOLDOWNS.get(item_name, CooldownConfig(days=1))
reminder_time = reminder_service.create_reminder(
    user_id=interaction.user.id,
    item_name=item_name,
    cooldown=cooldown,
    channel_id=destination_id,
    username=interaction.user.name
)

# Save panel message:
save_panel_message("my_panel", channel_id, message_id)

# Load panel message:
panel_info = get_panel_message("my_panel")

# Register service in your Cog __init__:
class MyPanel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        reminder_checker = get_reminder_checker(bot)
        reminder_checker.register_service("My Panel Name", reminder_service)
```

## CooldownConfig Examples

- `CooldownConfig(days=36)` - 36 days
- `CooldownConfig(hours=1, minutes=30)` - 1 hour 30 minutes
- `CooldownConfig(minutes=45)` - 45 minutes
- `CooldownConfig(days=2, hours=5, minutes=15)` - 2 days, 5 hours, 15 minutes

The service automatically handles:
- ✅ Persistent storage (survives bot restarts)
- ✅ Background checking (every minute)
- ✅ User pinging when cooldown expires
- ✅ Multiple panels using the same checker
