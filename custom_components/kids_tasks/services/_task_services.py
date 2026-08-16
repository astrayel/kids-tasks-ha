"""Task-related services for Kids Tasks."""
from __future__ import annotations

import uuid
import logging
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from ..const import DOMAIN, CATEGORIES, FREQUENCIES
from ..models import Task, TaskChildStatus

if TYPE_CHECKING:
    from ..coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_TASK = "add_task"
SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_VALIDATE_TASK = "validate_task"
SERVICE_REJECT_TASK = "reject_task"
SERVICE_RESET_TASK = "reset_task"
SERVICE_UPDATE_TASK = "update_task"
SERVICE_REMOVE_TASK = "remove_task"
SERVICE_SUSPEND_TASK = "suspend_task"
SERVICE_RESUME_TASK = "resume_task"
SERVICE_LIST_TASKS = "list_tasks"
SERVICE_RESET_ALL_DAILY_TASKS = "reset_all_daily_tasks"
SERVICE_RESET_ALL_WEEKLY_TASKS = "reset_all_weekly_tasks"
SERVICE_RESET_ALL_MONTHLY_TASKS = "reset_all_monthly_tasks"
SERVICE_CLEANUP_OLD_ENTITIES = "cleanup_old_entities"

SERVICE_ADD_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("category"): vol.In(CATEGORIES),
        vol.Optional("icon"): vol.Any(cv.string, None),
        vol.Optional("points", default=10): vol.Coerce(int),
        vol.Optional("coins", default=0): vol.Coerce(int),
        vol.Optional("frequency", default="daily"): vol.In(FREQUENCIES),
        vol.Optional("assigned_child_ids"): [cv.string],
        vol.Optional("validation_required", default=True): cv.boolean,
        vol.Optional("weekly_days"): vol.Any([cv.string], None),
        vol.Optional("deadline_time"): cv.string,
        vol.Optional("penalty_points", default=0): vol.Coerce(int),
    }
)

SERVICE_COMPLETE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Required("child_id"): cv.string,
        vol.Optional("validation_required"): cv.boolean,
    }
)

SERVICE_VALIDATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        # Omit to validate every child waiting on this task.
        vol.Optional("child_id"): cv.string,
    }
)

SERVICE_REJECT_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        # Omit to reject the task for every assigned child.
        vol.Optional("child_id"): cv.string,
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_RESET_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_UPDATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("points"): vol.Coerce(int),
        vol.Optional("coins"): vol.Coerce(int),
        vol.Optional("category"): vol.In(CATEGORIES),
        vol.Optional("icon"): vol.Any(cv.string, None),
        vol.Optional("frequency"): vol.In(FREQUENCIES),
        vol.Optional("assigned_child_ids"): [cv.string],
        vol.Optional("validation_required"): cv.boolean,
        vol.Optional("active"): cv.boolean,
        vol.Optional("weekly_days"): vol.Any([cv.string], None),
        vol.Optional("deadline_time"): cv.string,
        vol.Optional("penalty_points"): vol.Coerce(int),
    }
)

SERVICE_REMOVE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_SUSPEND_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("until_date"): cv.string,
    }
)

SERVICE_RESUME_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_RESET_PENALTIES_SCHEMA = vol.Schema({})


def register_task_services(
    hass: HomeAssistant,
    coordinator: KidsTasksDataUpdateCoordinator,
) -> None:
    """Register all task-related services."""

    async def add_task_service(call: ServiceCall) -> None:
        try:
            _LOGGER.info("Creating new task with data: %s", call.data)
            assigned_child_ids = call.data.get("assigned_child_ids", [])
            for child_id in assigned_child_ids:
                if child_id not in coordinator.children:
                    available = list(coordinator.children.keys())
                    _LOGGER.error(
                        "Assigned child ID %s does not exist. Available: %s",
                        child_id, available,
                    )
                    raise ValueError(f"Child with ID {child_id} does not exist")

            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                name=call.data["name"],
                description=call.data.get("description", ""),
                category=call.data.get("category", "other"),
                icon=call.data.get("icon"),
                points=call.data.get("points", 10),
                frequency=call.data.get("frequency", "daily"),
                assigned_child_ids=assigned_child_ids,
                validation_required=call.data.get("validation_required", True),
                weekly_days=call.data.get("weekly_days"),
                deadline_time=call.data.get("deadline_time"),
                penalty_points=call.data.get("penalty_points", 0),
            )
            for child_id in assigned_child_ids:
                task.child_statuses[child_id] = TaskChildStatus(child_id=child_id)

            await coordinator.async_add_task(task)
            _LOGGER.info("Task successfully added with ID: %s", task_id)
        except Exception as e:
            _LOGGER.error("Failed to create task: %s | data: %s", e, call.data)
            raise

    async def complete_task_service(call: ServiceCall) -> None:
        await coordinator.async_complete_task(
            call.data["task_id"],
            call.data["child_id"],
            call.data.get("validation_required"),
        )

    async def validate_task_service(call: ServiceCall) -> None:
        task_id = call.data["task_id"]
        child_id = call.data.get("child_id")
        success = await coordinator.async_validate_task(task_id, child_id)
        if not success:
            _LOGGER.warning(
                "Task validation failed: %s (child: %s)", task_id, child_id or "all"
            )

    async def reject_task_service(call: ServiceCall) -> None:
        success = await coordinator.async_reject_task(
            call.data["task_id"],
            call.data.get("child_id"),
            call.data.get("reason"),
        )
        if not success:
            _LOGGER.warning("Task rejection failed: %s", call.data["task_id"])

    async def reset_task_service(call: ServiceCall) -> None:
        task_id = call.data["task_id"]
        if task_id in coordinator.tasks:
            coordinator.tasks[task_id].reset()
            await coordinator.async_save_data()
            await coordinator.async_request_refresh()

    async def update_task_service(call: ServiceCall) -> None:
        try:
            task_id = call.data["task_id"]
            updates = {k: v for k, v in call.data.items() if k != "task_id"}
            if task_id not in coordinator.tasks:
                available = list(coordinator.tasks.keys())
                _LOGGER.error("Task %s does not exist. Available: %s", task_id, available)
                raise ValueError(f"Task with ID {task_id} does not exist")
            await coordinator.async_update_task(task_id, updates)
            _LOGGER.info("Task %s updated successfully", task_id)
        except Exception as e:
            _LOGGER.error("Failed to update task: %s | data: %s", e, call.data)
            raise

    async def remove_task_service(call: ServiceCall) -> None:
        await coordinator.async_remove_task(call.data["task_id"])

    async def suspend_task_service(call: ServiceCall) -> None:
        until_date = None
        until_date_str = call.data.get("until_date")
        if until_date_str:
            try:
                from datetime import datetime
                until_date = datetime.fromisoformat(until_date_str)
            except ValueError:
                _LOGGER.error("Invalid date format for until_date: %s", until_date_str)
                return
        await coordinator.async_suspend_task(call.data["task_id"], until_date)

    async def resume_task_service(call: ServiceCall) -> None:
        await coordinator.async_resume_task(call.data["task_id"])

    async def list_tasks_service(call: ServiceCall) -> None:
        try:
            tasks_list = []
            for task_id, task in coordinator.tasks.items():
                child_names = [
                    coordinator.children[cid].name
                    for cid in task.assigned_child_ids
                    if cid in coordinator.children
                ]
                tasks_list.append({
                    "task_id": task_id,
                    "name": task.name,
                    "description": task.description,
                    "category": task.category,
                    "points": task.points,
                    "frequency": task.frequency,
                    "status": task.status,
                    "assigned_child": ", ".join(child_names) if child_names else "Non assigné",
                    "validation_required": task.validation_required,
                    "active": task.active,
                })
            _LOGGER.info("Tasks list retrieved: %d tasks found", len(tasks_list))
            for task in tasks_list:
                _LOGGER.info(
                    "Task: %s | Assigned: %s | Status: %s | Points: %d",
                    task["name"], task["assigned_child"], task["status"], task["points"],
                )
        except Exception as e:
            _LOGGER.error("Failed to list tasks: %s", e)
            raise

    async def reset_all_daily_tasks_service(call: ServiceCall) -> None:
        await coordinator.async_reset_all_daily_tasks()

    async def reset_all_weekly_tasks_service(call: ServiceCall) -> None:
        await coordinator.async_reset_all_weekly_tasks()

    async def reset_all_monthly_tasks_service(call: ServiceCall) -> None:
        await coordinator.async_reset_all_monthly_tasks()

    async def reset_penalties_service(call: ServiceCall) -> None:
        try:
            tasks_updated = 0
            for task in coordinator.tasks.values():
                if task.penalty_points > 0:
                    task.penalty_points = 0
                    tasks_updated += 1
            await coordinator.async_save_data()
            await coordinator.async_request_refresh()
            _LOGGER.info("Reset penalty_points to 0 for %d tasks", tasks_updated)
        except Exception as e:
            _LOGGER.error("Failed to reset penalties: %s", e)
            raise

    async def cleanup_old_entities_service(call: ServiceCall) -> None:
        try:
            from homeassistant.helpers import entity_registry
            er = entity_registry.async_get(hass)
            old_entities_removed = []
            for entity_id, entity_entry in er.entities.items():
                if (
                    entity_id.startswith("sensor.tache_")
                    and entity_entry.config_entry_id
                    and entity_entry.config_entry_id in hass.data.get(DOMAIN, {})
                ):
                    er.async_remove(entity_id)
                    old_entities_removed.append(entity_id)
                    _LOGGER.info("Removed old entity: %s", entity_id)
                elif (
                    entity_id.startswith("button.")
                    and "tache" in entity_id
                    and entity_entry.config_entry_id
                    and entity_entry.config_entry_id in hass.data.get(DOMAIN, {})
                ):
                    er.async_remove(entity_id)
                    old_entities_removed.append(entity_id)
                    _LOGGER.info("Removed old button entity: %s", entity_id)
            _LOGGER.info("Cleanup completed - Removed %d old entities", len(old_entities_removed))
            for entry in hass.config_entries.async_entries(DOMAIN):
                await hass.config_entries.async_reload(entry.entry_id)
            _LOGGER.info("Integration reloaded with new entity format")
        except Exception as e:
            _LOGGER.error("Failed to cleanup old entities: %s", e)
            raise

    hass.services.async_register(DOMAIN, SERVICE_ADD_TASK, add_task_service, schema=SERVICE_ADD_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_TASK, complete_task_service, schema=SERVICE_COMPLETE_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_VALIDATE_TASK, validate_task_service, schema=SERVICE_VALIDATE_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REJECT_TASK, reject_task_service, schema=SERVICE_REJECT_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_RESET_TASK, reset_task_service, schema=SERVICE_RESET_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_TASK, update_task_service, schema=SERVICE_UPDATE_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_TASK, remove_task_service, schema=SERVICE_REMOVE_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SUSPEND_TASK, suspend_task_service, schema=SERVICE_SUSPEND_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_RESUME_TASK, resume_task_service, schema=SERVICE_RESUME_TASK_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_LIST_TASKS, list_tasks_service)
    hass.services.async_register(DOMAIN, SERVICE_RESET_ALL_DAILY_TASKS, reset_all_daily_tasks_service)
    hass.services.async_register(DOMAIN, SERVICE_RESET_ALL_WEEKLY_TASKS, reset_all_weekly_tasks_service)
    hass.services.async_register(DOMAIN, SERVICE_RESET_ALL_MONTHLY_TASKS, reset_all_monthly_tasks_service)
    hass.services.async_register(DOMAIN, "reset_penalties", reset_penalties_service, schema=SERVICE_RESET_PENALTIES_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CLEANUP_OLD_ENTITIES, cleanup_old_entities_service)
