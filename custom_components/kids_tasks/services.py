# ============================================================================
# services.py
# ============================================================================

"""Services for Kids Tasks integration."""
from __future__ import annotations

import uuid
import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CATEGORIES, FREQUENCIES
from .coordinator import KidsTasksDataUpdateCoordinator
from .models import Child, Task, Reward

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_CHILD = "add_child"
SERVICE_ADD_TASK = "add_task"
SERVICE_ADD_REWARD = "add_reward"
SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_VALIDATE_TASK = "validate_task"
SERVICE_CLAIM_REWARD = "claim_reward"
SERVICE_RESET_TASK = "reset_task"
SERVICE_CLEAR_ALL_DATA = "clear_all_data"

SERVICE_ADD_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("avatar"): cv.string,
        vol.Optional("initial_points", default=0): vol.Coerce(int),
    }
)

SERVICE_ADD_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("category"): vol.In(CATEGORIES),
        vol.Optional("points", default=10): vol.Coerce(int),
        vol.Optional("frequency", default="daily"): vol.In(FREQUENCIES),
        vol.Optional("assigned_child_id"): cv.string,
        vol.Optional("validation_required", default=True): cv.boolean,
    }
)

SERVICE_ADD_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("cost", default=50): vol.Coerce(int),
        vol.Optional("category", default="fun"): cv.string,
        vol.Optional("limited_quantity"): vol.Coerce(int),
    }
)

SERVICE_COMPLETE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("validation_required"): cv.boolean,
    }
)

SERVICE_VALIDATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_CLAIM_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("reward_id"): cv.string,
        vol.Required("child_id"): cv.string,
    }
)

SERVICE_RESET_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)


async def async_setup_services(
    hass: HomeAssistant, 
    coordinator: KidsTasksDataUpdateCoordinator
) -> None:
    """Set up services."""
    
    async def add_child_service(call: ServiceCall) -> None:
        """Add a new child."""
        child_id = str(uuid.uuid4())
        child = Child(
            id=child_id,
            name=call.data["name"],
            avatar=call.data.get("avatar"),
            points=call.data.get("initial_points", 0),
        )
        await coordinator.async_add_child(child)
    
    async def add_task_service(call: ServiceCall) -> None:
        """Add a new task."""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=call.data["name"],
            description=call.data.get("description", ""),
            category=call.data.get("category", "other"),
            points=call.data.get("points", 10),
            frequency=call.data.get("frequency", "daily"),
            assigned_child_id=call.data.get("assigned_child_id"),
            validation_required=call.data.get("validation_required", True),
        )
        await coordinator.async_add_task(task)
    
    async def add_reward_service(call: ServiceCall) -> None:
        """Add a new reward."""
        reward_id = str(uuid.uuid4())
        reward = Reward(
            id=reward_id,
            name=call.data["name"],
            description=call.data.get("description", ""),
            cost=call.data.get("cost", 50),
            category=call.data.get("category", "fun"),
            limited_quantity=call.data.get("limited_quantity"),
            remaining_quantity=call.data.get("limited_quantity"),
        )
        await coordinator.async_add_reward(reward)
    
    async def complete_task_service(call: ServiceCall) -> None:
        """Complete a task."""
        await coordinator.async_complete_task(
            call.data["task_id"],
            call.data.get("validation_required")
        )
    
    async def validate_task_service(call: ServiceCall) -> None:
        """Validate a task."""
        await coordinator.async_validate_task(call.data["task_id"])
    
    async def claim_reward_service(call: ServiceCall) -> None:
        """Claim a reward."""
        await coordinator.async_claim_reward(
            call.data["reward_id"],
            call.data["child_id"]
        )
    
    async def reset_task_service(call: ServiceCall) -> None:
        """Reset a task."""
        task_id = call.data["task_id"]
        if task_id in coordinator.tasks:
            coordinator.tasks[task_id].reset()
            await coordinator.async_save_data()
            await coordinator.async_request_refresh()
    
    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_CHILD, add_child_service, schema=SERVICE_ADD_CHILD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_TASK, add_task_service, schema=SERVICE_ADD_TASK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_REWARD, add_reward_service, schema=SERVICE_ADD_REWARD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_COMPLETE_TASK, complete_task_service, schema=SERVICE_COMPLETE_TASK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_VALIDATE_TASK, validate_task_service, schema=SERVICE_VALIDATE_TASK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_CLAIM_REWARD, claim_reward_service, schema=SERVICE_CLAIM_REWARD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_TASK, reset_task_service, schema=SERVICE_RESET_TASK_SCHEMA
    )
    
    async def clear_all_data_service(call: ServiceCall) -> None:
        """Clear all data."""
        try:
            _LOGGER.info("Starting to clear all data...")
            await coordinator.async_clear_all_data()
            _LOGGER.info("All data cleared successfully")
        except Exception as e:
            _LOGGER.error("Failed to clear data: %s", e)
            raise
    
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_ALL_DATA, clear_all_data_service
    )