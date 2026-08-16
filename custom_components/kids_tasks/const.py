# ============================================================================
# const.py
# ============================================================================

"""Constants for the Kids Tasks integration."""

DOMAIN = "kids_tasks"
STORAGE_VERSION = 2
STORAGE_KEY = f"{DOMAIN}.storage"

# Default configuration
# 60s rather than 30s: every entity is re-evaluated and written to the
# recorder on each cycle, and nothing here changes faster than a child can
# tap a button — completions push a refresh immediately anyway.
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_VALIDATION_REQUIRED = True
DEFAULT_NOTIFICATIONS_ENABLED = True

# Task statuses
TASK_STATUS_TODO = "todo"
TASK_STATUS_IN_PROGRESS = "in_progress"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_PENDING_VALIDATION = "pending_validation"
TASK_STATUS_VALIDATED = "validated"
TASK_STATUS_FAILED = "failed"
# Day the task is not scheduled on — neither owed nor earned.
TASK_STATUS_NOT_APPLICABLE = "not_applicable"

TASK_STATUSES = [
    TASK_STATUS_TODO,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_PENDING_VALIDATION,
    TASK_STATUS_VALIDATED,
    TASK_STATUS_FAILED,
    TASK_STATUS_NOT_APPLICABLE,
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
    "bedroom": "mdi:bed",
    "hygiene": "mdi:shower",
    "kitchen": "mdi:silverware-fork-knife",
    "homework": "mdi:book-open-variant",
    "music": "mdi:music",
    "outdoor": "mdi:tree",
    "other": "mdi:clipboard-list",
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
    "fun": "mdi:gamepad-variant",
    "screen_time": "mdi:monitor",
    "outing": "mdi:car",
    "privilege": "mdi:crown",
    "toy": "mdi:toy-brick",
    "treat": "mdi:food-apple",
}

# Events
EVENT_TASK_COMPLETED = f"{DOMAIN}_task_completed"
EVENT_TASK_VALIDATED = f"{DOMAIN}_task_validated"
EVENT_LEVEL_UP = f"{DOMAIN}_level_up"
EVENT_REWARD_CLAIMED = f"{DOMAIN}_reward_claimed"