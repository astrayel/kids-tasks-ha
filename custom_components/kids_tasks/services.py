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
SERVICE_REJECT_TASK = "reject_task"
SERVICE_CLAIM_REWARD = "claim_reward"
SERVICE_RESET_TASK = "reset_task"
SERVICE_ADD_POINTS = "add_points"
SERVICE_REMOVE_POINTS = "remove_points"
SERVICE_UPDATE_CHILD = "update_child"
SERVICE_REMOVE_CHILD = "remove_child"
SERVICE_UPDATE_TASK = "update_task"
SERVICE_REMOVE_TASK = "remove_task"
SERVICE_UPDATE_REWARD = "update_reward"
SERVICE_REMOVE_REWARD = "remove_reward"
SERVICE_RESET_ALL_DAILY_TASKS = "reset_all_daily_tasks"
SERVICE_BACKUP_DATA = "backup_data"
SERVICE_RESTORE_DATA = "restore_data"
SERVICE_CLEAR_ALL_DATA = "clear_all_data"
SERVICE_LIST_TASKS = "list_tasks"
SERVICE_LIST_CHILDREN = "list_children"
SERVICE_CLEANUP_OLD_ENTITIES = "cleanup_old_entities"

SERVICE_ADD_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("avatar"): cv.string,
        vol.Optional("initial_points", default=0): vol.Coerce(int),
        vol.Optional("person_entity_id"): cv.string,
        vol.Optional("avatar_type", default="emoji"): vol.In(["emoji", "url", "inline", "person_entity"]),
        vol.Optional("avatar_data"): cv.string,
        vol.Optional("card_gradient_start"): cv.string,
        vol.Optional("card_gradient_end"): cv.string,
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
        vol.Optional("limited_quantity"): vol.Any(vol.Coerce(int), None),
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

SERVICE_REJECT_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_ADD_POINTS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("points"): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_REMOVE_POINTS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("points"): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_UPDATE_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("avatar"): cv.string,
    }
)

SERVICE_REMOVE_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Optional("force_remove_entities", default=False): cv.boolean,
    }
)

SERVICE_UPDATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("points"): vol.Coerce(int),
        vol.Optional("category"): vol.In(CATEGORIES),
        vol.Optional("frequency"): vol.In(FREQUENCIES),
        vol.Optional("assigned_child_id"): cv.string,
        vol.Optional("validation_required"): cv.boolean,
        vol.Optional("active"): cv.boolean,
    }
)

SERVICE_REMOVE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_UPDATE_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("reward_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("cost"): vol.Coerce(int),
        vol.Optional("category"): cv.string,
        vol.Optional("limited_quantity"): vol.Any(vol.Coerce(int), None),
        vol.Optional("remaining_quantity"): vol.Any(vol.Coerce(int), None),
        vol.Optional("active"): cv.boolean,
    }
)

SERVICE_REMOVE_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("reward_id"): cv.string,
    }
)

SERVICE_BACKUP_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("include_history", default=True): cv.boolean,
    }
)

SERVICE_RESTORE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("backup_data"): cv.string,
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
            person_entity_id=call.data.get("person_entity_id"),
            avatar_type=call.data.get("avatar_type", "emoji"),
            avatar_data=call.data.get("avatar_data"),
            card_gradient_start=call.data.get("card_gradient_start"),
            card_gradient_end=call.data.get("card_gradient_end"),
        )
        await coordinator.async_add_child(child)
    
    async def add_task_service(call: ServiceCall) -> None:
        """Add a new task."""
        try:
            _LOGGER.info("🔧 NOUVELLE VERSION - Creating new task with data: %s", call.data)
            
            # Validate assigned child exists if provided
            assigned_child_id = call.data.get("assigned_child_id")
            if assigned_child_id and assigned_child_id not in coordinator.children:
                _LOGGER.error("Assigned child ID %s does not exist", assigned_child_id)
                available_children = list(coordinator.children.keys())
                _LOGGER.error("Available child IDs: %s", available_children)
                for child_id, child in coordinator.children.items():
                    _LOGGER.error("Child: %s (ID: %s)", child.name, child_id)
                raise ValueError(f"Child with ID {assigned_child_id} does not exist")
            
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                name=call.data["name"],
                description=call.data.get("description", ""),
                category=call.data.get("category", "other"),
                points=call.data.get("points", 10),
                frequency=call.data.get("frequency", "daily"),
                assigned_child_id=assigned_child_id,
                validation_required=call.data.get("validation_required", True),
            )
            
            _LOGGER.info("Task object created: %s", task.to_dict())
            await coordinator.async_add_task(task)
            _LOGGER.info("Task successfully added with ID: %s", task_id)
            
        except Exception as e:
            _LOGGER.error("Failed to create task: %s", e)
            _LOGGER.error("Task data was: %s", call.data)
            raise
    
    async def add_reward_service(call: ServiceCall) -> None:
        """Add a new reward."""
        try:
            _LOGGER.info("Creating new reward with data: %s", call.data)
            
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
            
            _LOGGER.info("Reward object created: %s", reward.to_dict())
            await coordinator.async_add_reward(reward)
            _LOGGER.info("Reward successfully added with ID: %s", reward_id)
            
        except Exception as e:
            _LOGGER.error("Failed to create reward: %s", e)
            _LOGGER.error("Reward data was: %s", call.data)
            raise
    
    async def complete_task_service(call: ServiceCall) -> None:
        """Complete a task."""
        await coordinator.async_complete_task(
            call.data["task_id"],
            call.data.get("validation_required")
        )
    
    async def validate_task_service(call: ServiceCall) -> None:
        """Validate a task."""
        task_id = call.data["task_id"]
        _LOGGER.info("🔧 Validating task: %s", task_id)
        success = await coordinator.async_validate_task(task_id)
        if success:
            _LOGGER.info("✅ Task validation successful: %s", task_id)
        else:
            _LOGGER.warning("❌ Task validation failed: %s", task_id)
    
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
    
    async def reject_task_service(call: ServiceCall) -> None:
        """Reject a task."""
        await coordinator.async_reject_task(call.data["task_id"])
    
    async def add_points_service(call: ServiceCall) -> None:
        """Add points to a child."""
        child_id = call.data["child_id"]
        points = call.data["points"]
        await coordinator.async_add_points(child_id, points)
    
    async def remove_points_service(call: ServiceCall) -> None:
        """Remove points from a child."""
        child_id = call.data["child_id"]
        points = call.data["points"]
        await coordinator.async_remove_points(child_id, points)
    
    async def update_child_service(call: ServiceCall) -> None:
        """Update a child."""
        child_id = call.data["child_id"]
        updates = {k: v for k, v in call.data.items() if k != "child_id"}
        await coordinator.async_update_child(child_id, updates)
    
    async def remove_child_service(call: ServiceCall) -> None:
        """Remove a child."""
        await coordinator.async_remove_child(
            call.data["child_id"],
            call.data.get("force_remove_entities", False)
        )
    
    async def update_task_service(call: ServiceCall) -> None:
        """Update a task."""
        try:
            task_id = call.data["task_id"]
            updates = {k: v for k, v in call.data.items() if k != "task_id"}
            
            _LOGGER.info("Updating task with ID: %s", task_id)
            _LOGGER.info("Updates to apply: %s", updates)
            
            # Check if task exists
            if task_id not in coordinator.tasks:
                _LOGGER.error("Task with ID %s does not exist", task_id)
                available_tasks = list(coordinator.tasks.keys())
                _LOGGER.error("Available task IDs: %s", available_tasks)
                raise ValueError(f"Task with ID {task_id} does not exist")
            
            await coordinator.async_update_task(task_id, updates)
            _LOGGER.info("Task %s updated successfully", task_id)
            
        except Exception as e:
            _LOGGER.error("Failed to update task: %s", e)
            _LOGGER.error("Task data was: %s", call.data)
            raise
    
    async def remove_task_service(call: ServiceCall) -> None:
        """Remove a task."""
        await coordinator.async_remove_task(call.data["task_id"])
    
    async def update_reward_service(call: ServiceCall) -> None:
        """Update a reward."""
        reward_id = call.data["reward_id"]
        updates = {k: v for k, v in call.data.items() if k != "reward_id"}
        await coordinator.async_update_reward(reward_id, updates)
    
    async def remove_reward_service(call: ServiceCall) -> None:
        """Remove a reward."""
        await coordinator.async_remove_reward(call.data["reward_id"])
    
    async def reset_all_daily_tasks_service(call: ServiceCall) -> None:
        """Reset all daily tasks."""
        await coordinator.async_reset_all_daily_tasks()
    
    async def backup_data_service(call: ServiceCall) -> None:
        """Backup data."""
        include_history = call.data.get("include_history", True)
        backup = await coordinator.async_backup_data(include_history)
        _LOGGER.info("Data backup created: %s", backup[:100] + "...")
    
    async def restore_data_service(call: ServiceCall) -> None:
        """Restore data."""
        backup_data = call.data["backup_data"]
        await coordinator.async_restore_data(backup_data)
    
    # Register all services
    hass.services.async_register(
        DOMAIN, SERVICE_REJECT_TASK, reject_task_service, schema=SERVICE_REJECT_TASK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_POINTS, add_points_service, schema=SERVICE_ADD_POINTS_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_POINTS, remove_points_service, schema=SERVICE_REMOVE_POINTS_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_CHILD, update_child_service, schema=SERVICE_UPDATE_CHILD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_CHILD, remove_child_service, schema=SERVICE_REMOVE_CHILD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_TASK, update_task_service, schema=SERVICE_UPDATE_TASK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_TASK, remove_task_service, schema=SERVICE_REMOVE_TASK_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_REWARD, update_reward_service, schema=SERVICE_UPDATE_REWARD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_REWARD, remove_reward_service, schema=SERVICE_REMOVE_REWARD_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_ALL_DAILY_TASKS, reset_all_daily_tasks_service
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_BACKUP_DATA, backup_data_service, schema=SERVICE_BACKUP_DATA_SCHEMA
    )
    
    hass.services.async_register(
        DOMAIN, SERVICE_RESTORE_DATA, restore_data_service, schema=SERVICE_RESTORE_DATA_SCHEMA
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
    
    async def list_tasks_service(call: ServiceCall) -> None:
        """List all tasks with details."""
        try:
            tasks_list = []
            for task_id, task in coordinator.tasks.items():
                # Get child name if assigned
                child_name = "Non assigné"
                if task.assigned_child_id and task.assigned_child_id in coordinator.children:
                    child_name = coordinator.children[task.assigned_child_id].name
                
                tasks_list.append({
                    "task_id": task_id,
                    "name": task.name,
                    "description": task.description,
                    "category": task.category,
                    "points": task.points,
                    "frequency": task.frequency,
                    "status": task.status,
                    "assigned_child": child_name,
                    "validation_required": task.validation_required,
                    "active": task.active
                })
            
            _LOGGER.info("Tasks list retrieved: %d tasks found", len(tasks_list))
            # Log each task for visibility in Home Assistant logs
            for task in tasks_list:
                _LOGGER.info("Task: %s | Assigned: %s | Status: %s | Points: %d", 
                           task["name"], task["assigned_child"], task["status"], task["points"])
                           
        except Exception as e:
            _LOGGER.error("Failed to list tasks: %s", e)
            raise
    
    hass.services.async_register(
        DOMAIN, SERVICE_LIST_TASKS, list_tasks_service
    )
    
    async def list_children_service(call: ServiceCall) -> None:
        """List all children with details."""
        try:
            children_list = []
            for child_id, child in coordinator.children.items():
                children_list.append({
                    "child_id": child_id,
                    "name": child.name,
                    "points": child.points,
                    "level": child.level,
                    "avatar": child.avatar
                })
            
            _LOGGER.info("Children list retrieved: %d children found", len(children_list))
            # Log each child for visibility in Home Assistant logs
            for child in children_list:
                _LOGGER.info("Child: %s | ID: %s | Points: %d | Level: %d", 
                           child["name"], child["child_id"], child["points"], child["level"])
                           
        except Exception as e:
            _LOGGER.error("Failed to list children: %s", e)
            raise
    
    hass.services.async_register(
        DOMAIN, SERVICE_LIST_CHILDREN, list_children_service
    )
    
    async def cleanup_old_entities_service(call: ServiceCall) -> None:
        """Cleanup old entity formats and recreate with new format."""
        try:
            from homeassistant.helpers import entity_registry
            
            # Get entity registry
            er = entity_registry.async_get(hass)
            
            # Find and remove old format entities
            old_entities_removed = []
            
            for entity_id, entity_entry in er.entities.items():
                # Remove old tache_ format entities
                if (entity_id.startswith('sensor.tache_') and 
                    entity_entry.config_entry_id and 
                    entity_entry.config_entry_id in hass.data.get(DOMAIN, {})):
                    er.async_remove(entity_id)
                    old_entities_removed.append(entity_id)
                    _LOGGER.info("Removed old entity: %s", entity_id)
                    
                # Remove old button entities with old naming
                elif (entity_id.startswith('button.') and 
                      'tache' in entity_id and
                      entity_entry.config_entry_id and 
                      entity_entry.config_entry_id in hass.data.get(DOMAIN, {})):
                    er.async_remove(entity_id)
                    old_entities_removed.append(entity_id)
                    _LOGGER.info("Removed old button entity: %s", entity_id)
            
            _LOGGER.info("🧹 Cleanup completed - Removed %d old entities", len(old_entities_removed))
            
            # Force recreate entities with new format by triggering setup
            config_entries = [entry for entry in hass.config_entries.async_entries(DOMAIN)]
            for entry in config_entries:
                await hass.config_entries.async_reload(entry.entry_id)
                
            _LOGGER.info("✅ Integration reloaded - New entities should be created with correct format")
                           
        except Exception as e:
            _LOGGER.error("Failed to cleanup old entities: %s", e)
            raise
    
    hass.services.async_register(
        DOMAIN, SERVICE_CLEANUP_OLD_ENTITIES, cleanup_old_entities_service
    )