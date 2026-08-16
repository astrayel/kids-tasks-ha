# ============================================================================
# sensor.py
# ============================================================================

"""Sensor platform for Kids Tasks integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CATEGORIES, FREQUENCIES, CATEGORY_ICONS, REWARD_CATEGORIES, REWARD_CATEGORY_ICONS
from .coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def get_safe_child_name(coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> str:
    """Get a safe name for entity_id from child data."""
    import re
    child_data = coordinator.children.get(child_id, {})
    child_name = child_data.name if hasattr(child_data, 'name') else str(child_data.get('name', f'child_{child_id[:8]}'))
    safe_child_name = child_name.lower().replace(' ', '_').replace('-', '_').replace('é', 'e').replace('è', 'e').replace('à', 'a').replace('ç', 'c')
    safe_child_name = re.sub(r'[^a-z0-9_]', '', safe_child_name)
    return safe_child_name


def _child_device_info(coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> DeviceInfo:
    """Return DeviceInfo for a child profile device."""
    child_data = coordinator.data["children"].get(child_id, {})
    return DeviceInfo(
        identifiers={(DOMAIN, child_id)},
        name=child_data.get("name", "Child"),
        manufacturer="Kids Tasks",
        model="Child Profile",
        via_device=(DOMAIN, "kids_tasks"),
    )


_SYSTEM_DEVICE_INFO = DeviceInfo(
    identifiers={(DOMAIN, "kids_tasks")},
    name="Kids Tasks",
    manufacturer="Kids Tasks",
    model="Task Manager",
    entry_type=DeviceEntryType.SERVICE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: KidsTasksDataUpdateCoordinator = config_entry.runtime_data.coordinator
    coordinator.async_register_platform("sensor", async_add_entities)

    entities = []
    
    # Add child sensors
    for child_id, child_data in coordinator.data.get("children", {}).items():
        entities.extend([
            ChildPointsSensor(coordinator, child_id),
            ChildLevelSensor(coordinator, child_id),
            ChildTasksCompletedTodaySensor(coordinator, child_id),
            ChildPointsHistorySensor(coordinator, child_id),
        ])
    
    # Add individual task sensors
    for task_id, task_data in coordinator.data.get("tasks", {}).items():
        entities.append(TaskSensor(coordinator, task_id))
    
    # Add individual reward sensors
    for reward_id, reward_data in coordinator.data.get("rewards", {}).items():
        entities.append(RewardSensor(coordinator, reward_id))
    
    # Add only essential general sensors (keep for statistics)
    entities.extend([
        PendingValidationsSensor(coordinator),
        TotalTasksCompletedTodaySensor(coordinator),
        ActiveTasksSensor(coordinator),
        AllChildrenListSensor(coordinator),
    ])
    
    async_add_entities(entities)


class ChildPointsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for child points."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_points"
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_icon = "mdi:star"
        self._attr_native_unit_of_measurement = "points"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_points"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _child_device_info(self.coordinator, self.child_id)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        child_name = self.coordinator.data["children"].get(self.child_id, {}).get("name", "Unknown")
        return f"{child_name} Points"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data["children"].get(self.child_id, {}).get("points", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        child_data = self.coordinator.data["children"].get(self.child_id, {})
        level = child_data.get("level", 1)
        points = child_data.get("points", 0)
        return {
            "type": "child",  # Add type for card detection
            "level": level,
            "points_to_next_level": (level * 100) - points,
            "child_id": self.child_id,
            "name": child_data.get("name", "Unknown"),
            "coins": child_data.get("coins", 0),
            "avatar": child_data.get("avatar", ""),
            "person_entity_id": child_data.get("person_entity_id"),
            "avatar_type": child_data.get("avatar_type", "emoji"),
            "avatar_data": child_data.get("avatar_data"),
            "card_gradient_start": child_data.get("card_gradient_start"),
            "card_gradient_end": child_data.get("card_gradient_end"),
            # Cosmetics the child owns and wears — the cards need both to tell
            # "bought but not worn" from "not bought yet".
            "cosmetic_collection": child_data.get("cosmetic_collection", {}),
            "active_cosmetics": child_data.get("active_cosmetics", {}),
            "cosmetic_items": child_data.get("cosmetic_items", []),
        }


class ChildLevelSensor(CoordinatorEntity, SensorEntity):
    """Sensor for child level."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_level"
        self._attr_icon = "mdi:trophy"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_level"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _child_device_info(self.coordinator, self.child_id)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        child_name = self.coordinator.data["children"].get(self.child_id, {}).get("name", "Unknown")
        return f"{child_name} Niveau"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.data["children"].get(self.child_id, {}).get("level", 1)


class ChildTasksCompletedTodaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for child tasks completed today."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_tasks_today"
        self._attr_icon = "mdi:check-circle"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_tasks_today"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _child_device_info(self.coordinator, self.child_id)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        child_name = self.coordinator.data["children"].get(self.child_id, {}).get("name", "Unknown")
        return f"{child_name} Tâches Aujourd'hui"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        today = dt_util.now().date()
        count = 0
        
        for task_data in self.coordinator.data.get("tasks", {}).values():
            # Check if this child is assigned to the task
            assigned_child_ids = task_data.get("assigned_child_ids", [])
            if self.child_id in assigned_child_ids:
                # Check the child's individual status
                child_statuses = task_data.get("child_statuses", {})
                if self.child_id in child_statuses:
                    child_status = child_statuses[self.child_id]
                    if (child_status.get("status") == "validated" and 
                        child_status.get("validated_at")):
                        try:
                            validated_date = datetime.fromisoformat(child_status["validated_at"]).date()
                            if validated_date == today:
                                count += 1
                        except (ValueError, TypeError):
                            continue
        
        return count


class PendingValidationsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for pending validations."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"kidtasks_pending_validations"
        self._attr_icon = "mdi:clock-alert"
        self.entity_id = f"sensor.kidtasks_pending_validations"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _SYSTEM_DEVICE_INFO

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Tâches en Attente de Validation"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        count = 0
        for task_data in self.coordinator.data.get("tasks", {}).values():
            if task_data.get("status") == "pending_validation":
                count += 1
        return count

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        pending_tasks = []
        for task_id, task_data in self.coordinator.data.get("tasks", {}).items():
            if task_data.get("status") == "pending_validation":
                assigned_child_ids = task_data.get("assigned_child_ids") or []

                child_names = []
                for cid in assigned_child_ids:
                    name = self.coordinator.data["children"].get(cid, {}).get("name")
                    if name:
                        child_names.append(name)

                pending_tasks.append({
                    "task_id": task_id,
                    "name": task_data.get("name", ""),
                    "child": ", ".join(child_names) if child_names else "Unknown",
                    "child_ids": assigned_child_ids,
                    "category": task_data.get("category", "other"),
                    "points": task_data.get("points", 0),
                })
        
        return {
            "pending_tasks": pending_tasks,
            "available_categories": CATEGORIES,
            "available_frequencies": FREQUENCIES,
            "category_icons": CATEGORY_ICONS,
            "available_reward_categories": REWARD_CATEGORIES,
            "reward_category_icons": REWARD_CATEGORY_ICONS,
        }


class TotalTasksCompletedTodaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for total tasks completed today."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"kidtasks_total_tasks_today"
        self._attr_icon = "mdi:check-all"
        self.entity_id = f"sensor.kidtasks_total_tasks_today"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _SYSTEM_DEVICE_INFO

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Total Tâches Aujourd'hui"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        today = dt_util.now().date()
        count = 0
        
        for task_data in self.coordinator.data.get("tasks", {}).values():
            # Count individual child validations, not global task status
            child_statuses = task_data.get("child_statuses", {})
            for child_id, child_status in child_statuses.items():
                if (child_status.get("status") == "validated" and 
                    child_status.get("validated_at")):
                    try:
                        validated_date = datetime.fromisoformat(child_status["validated_at"]).date()
                        if validated_date == today:
                            count += 1
                    except (ValueError, TypeError):
                        continue
        
        return count


class ActiveTasksSensor(CoordinatorEntity, SensorEntity):
    """Sensor for active tasks."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"kidtasks_active_tasks"
        self._attr_icon = "mdi:format-list-checks"
        self.entity_id = f"sensor.kidtasks_active_tasks"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _SYSTEM_DEVICE_INFO

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Tâches Actives"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        count = 0
        for task_data in self.coordinator.data.get("tasks", {}).values():
            if task_data.get("active", True):
                count += 1
        return count


class AllChildrenListSensor(CoordinatorEntity, SensorEntity):
    """Sensor exposing all children as attributes for card dropdowns."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = "kidtasks_all_children_list"
        self._attr_icon = "mdi:account-group"
        self.entity_id = "sensor.kidtasks_all_children_list"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Liste de Tous les Enfants"

    @property
    def native_value(self) -> int:
        """Return the total number of children."""
        return len(self.coordinator.data.get("children", {}))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes with all children details."""
        children = []
        for child_id, child_data in self.coordinator.data.get("children", {}).items():
            children.append({
                "id": child_id,
                "name": child_data.get("name", ""),
                "avatar": child_data.get("avatar", ""),
                "avatar_type": child_data.get("avatar_type", "emoji"),
                "level": child_data.get("level", 1),
                "points": child_data.get("points", 0),
                "coins": child_data.get("coins", 0),
            })
        children.sort(key=lambda x: x["name"])
        return {"children": children, "total_count": len(children)}


class TaskSensor(CoordinatorEntity, SensorEntity):
    """Individual sensor for each task."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"kidtasks_task_{task_id}"
        safe_task_id = task_id.replace("-", "_")
        self.entity_id = f"sensor.kidtasks_task_{safe_task_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _SYSTEM_DEVICE_INFO

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        task_name = task_data.get("name", "Tâche inconnue")
        return f"{task_name}"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        custom_icon = task_data.get("icon")
        if custom_icon:
            return custom_icon
        # Fallback vers l'icône par défaut
        return "mdi:clipboard-check"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor (task status)."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        return task_data.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        
        # Get child names
        assigned_child_ids = task_data.get("assigned_child_ids") or []
        child_names = [
            self.coordinator.data.get("children", {}).get(cid, {}).get("name")
            for cid in assigned_child_ids
        ]
        child_name = ", ".join(n for n in child_names if n) or "Non assigné"
        
        # Prepare child statuses for frontend
        child_statuses_for_frontend = {}
        child_statuses = task_data.get("child_statuses", {})
        
        # Convert child statuses to a simple format for frontend
        for child_id, status_data in child_statuses.items():
            child_data = self.coordinator.data.get("children", {}).get(child_id, {})
            child_name = child_data.get("name", "Enfant inconnu")
            child_statuses_for_frontend[child_id] = {
                "child_name": child_name,
                "status": status_data.get("status", "todo"),
                "completed_at": status_data.get("completed_at"),
                "validated_at": status_data.get("validated_at"),
                "penalty_applied_at": status_data.get("penalty_applied_at"),
                "penalty_applied": status_data.get("penalty_applied", False),
            }

        return {
            "task_id": self.task_id,
            "task_name": task_data.get("name", ""),
            "description": task_data.get("description", ""),
            "category": task_data.get("category", "other"),
            "icon": task_data.get("icon"),
            "points": task_data.get("points", 0),
            "coins": task_data.get("coins", 0),
            "frequency": task_data.get("frequency", "daily"),
            "assigned_child_ids": task_data.get("assigned_child_ids", []),
            "validation_required": task_data.get("validation_required", False),
            "active": task_data.get("active", True),
            "created_at": task_data.get("created_at"),
            "last_completed_at": task_data.get("last_completed_at"),
            "weekly_days": task_data.get("weekly_days"),
            "deadline_time": task_data.get("deadline_time"),
            "deadline_passed": task_data.get("deadline_passed", False),
            "penalty_points": task_data.get("penalty_points", 0),
            "completed_by_child_id": task_data.get("completed_by_child_id"),
            "child_statuses": child_statuses_for_frontend,  # Nouveaux statuts individuels
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.task_id in self.coordinator.data.get("tasks", {})


class RewardSensor(CoordinatorEntity, SensorEntity):
    """Individual sensor for each reward."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, reward_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.reward_id = reward_id
        self._attr_unique_id = f"kidtasks_reward_{reward_id}"
        safe_reward_id = reward_id.replace("-", "_")
        self.entity_id = f"sensor.kidtasks_reward_{safe_reward_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _SYSTEM_DEVICE_INFO

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        reward_data = self.coordinator.data["rewards"].get(self.reward_id, {})
        reward_name = reward_data.get("name", "Récompense inconnue")
        return f"{reward_name}"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        reward_data = self.coordinator.data["rewards"].get(self.reward_id, {})
        custom_icon = reward_data.get("icon")
        if custom_icon:
            return custom_icon
        # Fallback vers l'icône par défaut
        return "mdi:gift"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor (reward cost)."""
        reward_data = self.coordinator.data["rewards"].get(self.reward_id, {})
        return reward_data.get("cost", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        reward_data = self.coordinator.data["rewards"].get(self.reward_id, {})
        
        attributes = {
            "reward_id": self.reward_id,
            "reward_name": reward_data.get("name", ""),
            "description": reward_data.get("description", ""),
            "cost": reward_data.get("cost", 0),
            "coin_cost": reward_data.get("coin_cost", 0),
            "category": reward_data.get("category", "fun"),
            "icon": reward_data.get("icon"),
            "active": reward_data.get("active", True),
            "limited_quantity": reward_data.get("limited_quantity"),
            "remaining_quantity": reward_data.get("remaining_quantity"),
            "is_available": reward_data.get("remaining_quantity") is None or reward_data.get("remaining_quantity", 0) > 0,
            "reward_type": reward_data.get("reward_type", "real"),
            "min_level": reward_data.get("min_level", 1),
        }
        
        # Add cosmetic data if available
        cosmetic_data = reward_data.get("cosmetic_data")
        if cosmetic_data:
            attributes["cosmetic_data"] = cosmetic_data
        
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.reward_id in self.coordinator.data.get("rewards", {})


class ChildPointsHistorySensor(CoordinatorEntity, SensorEntity):
    """Sensor for child points history."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_points_history"
        self._attr_device_class = None
        self._attr_state_class = None
        self._attr_icon = "mdi:history"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_points_history"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _child_device_info(self.coordinator, self.child_id)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        child_data = self.coordinator.data["children"].get(self.child_id, {})
        child_name = child_data.get("name", "Enfant inconnu")
        return f"Historique Points: {child_name}"

    @property
    def native_value(self) -> int:
        """Return the number of history entries."""
        child_data = self.coordinator.data["children"].get(self.child_id, {})
        points_history = child_data.get("points_history", [])
        return len(points_history)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes with points history."""
        child_data = self.coordinator.data["children"].get(self.child_id, {})
        points_history = child_data.get("points_history", [])
        
        # Format the history for display
        formatted_history = []
        for entry in points_history[:20]:  # Limit to 20 entries
            formatted_entry = {
                "timestamp": entry.get("timestamp"),
                "action_type": entry.get("action_type", "unknown"),
                "points_delta": entry.get("points_delta", 0),
                "description": entry.get("description", ""),
                "related_entity_name": entry.get("related_entity_name"),
            }
            formatted_history.append(formatted_entry)
        
        return {
            "child_id": self.child_id,
            "child_name": child_data.get("name", "Enfant inconnu"),
            "total_entries": len(points_history),
            "points_history": formatted_history,
            "last_update": points_history[0].get("timestamp") if points_history else None,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.child_id in self.coordinator.data.get("children", {})