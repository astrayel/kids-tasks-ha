# ============================================================================
# const.py
# ============================================================================

"""Constants for the Kids Tasks integration."""

DOMAIN = "kids_tasks"
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"

# Default configuration
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_VALIDATION_REQUIRED = True
DEFAULT_NOTIFICATIONS_ENABLED = True

# Task statuses
TASK_STATUS_TODO = "todo"
TASK_STATUS_IN_PROGRESS = "in_progress"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_PENDING_VALIDATION = "pending_validation"
TASK_STATUS_VALIDATED = "validated"
TASK_STATUS_FAILED = "failed"

TASK_STATUSES = [
    TASK_STATUS_TODO,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_PENDING_VALIDATION,
    TASK_STATUS_VALIDATED,
    TASK_STATUS_FAILED,
]

# Task frequencies
FREQUENCY_DAILY = "daily"
FREQUENCY_WEEKLY = "weekly"
FREQUENCY_MONTHLY = "monthly"
FREQUENCY_ONCE = "once"
FREQUENCY_NONE = "none"

FREQUENCIES = [
    FREQUENCY_DAILY,
    FREQUENCY_WEEKLY,
    FREQUENCY_MONTHLY,
    FREQUENCY_ONCE,
    FREQUENCY_NONE,
]

# Task categories
CATEGORIES = [
    "bedroom",
    "hygiene",
    "kitchen",
    "homework",
    "outdoor",
    "music",
    "other",
]

CATEGORY_ICONS = {
    "bedroom": "🛏️",
    "hygiene": "🛁",
    "kitchen": "🍽️",
    "homework": "📚",
    "music": "🎵",
    "outdoor": "🌳",
    "other": "📋",
}

# Reward categories
REWARD_CATEGORIES = [
    "fun",
    "screen_time",
    "outing",
    "privilege",
    "toy",
    "treat",
]

REWARD_CATEGORY_ICONS = {
    "fun": "🎉",
    "screen_time": "📱",
    "outing": "🚗",
    "privilege": "👑",
    "toy": "🧸",
    "treat": "🍭",
}

# Events
EVENT_TASK_COMPLETED = f"{DOMAIN}_task_completed"
EVENT_TASK_VALIDATED = f"{DOMAIN}_task_validated"
EVENT_LEVEL_UP = f"{DOMAIN}_level_up"
EVENT_REWARD_CLAIMED = f"{DOMAIN}_reward_claimed"