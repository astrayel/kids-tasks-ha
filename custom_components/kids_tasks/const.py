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

FREQUENCIES = [
    FREQUENCY_DAILY,
    FREQUENCY_WEEKLY,
    FREQUENCY_MONTHLY,
    FREQUENCY_ONCE,
]

# Task categories
CATEGORIES = [
    "bedroom",
    "bathroom",
    "kitchen",
    "homework",
    "outdoor",
    "pets",
    "other",
]

# Events
EVENT_TASK_COMPLETED = f"{DOMAIN}_task_completed"
EVENT_TASK_VALIDATED = f"{DOMAIN}_task_validated"
EVENT_LEVEL_UP = f"{DOMAIN}_level_up"
EVENT_REWARD_CLAIMED = f"{DOMAIN}_reward_claimed"