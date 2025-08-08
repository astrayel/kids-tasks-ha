# ============================================================================
# sensor.py
# ============================================================================

"""Sensor platform for Kids Tasks integration."""
from __future__ import annotations

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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KidsTasksDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    # Add child sensors
    for child_id, child_data in coordinator.data.get("children", {}).items():
        entities.extend([
            ChildPointsSensor(coordinator, child_id),
            ChildLevelSensor(coordinator, child_id),
            ChildTasksCompletedTodaySensor(coordinator, child_id),
        ])
    
    # Add general sensors
    entities.extend([
        PendingValidationsSensor(coordinator),
        TotalTasksCompletedTodaySensor(coordinator),
        ActiveTasksSensor(coordinator),
    ])
    
    async_add_entities(entities)


class ChildPointsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for child points."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        self._attr_unique_id = f"{DOMAIN}_{child_id}_points"
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_icon = "mdi:star"

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
            "avatar": child_data.get("avatar", "👶"),
        }


class ChildLevelSensor(CoordinatorEntity, SensorEntity):
    """Sensor for child level."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        self._attr_unique_id = f"{DOMAIN}_{child_id}_level"
        self._attr_icon = "mdi:trophy"

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
        self._attr_unique_id = f"{DOMAIN}_{child_id}_tasks_today"
        self._attr_icon = "mdi:check-circle"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        child_name = self.coordinator.data["children"].get(self.child_id, {}).get("name", "Unknown")
        return f"{child_name} Tâches Aujourd'hui"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        today = datetime.now().date()
        count = 0
        
        for task_data in self.coordinator.data.get("tasks", {}).values():
            if (task_data.get("assigned_child_id") == self.child_id and 
                task_data.get("status") == "validated" and
                task_data.get("last_completed_at")):
                try:
                    completed_date = datetime.fromisoformat(task_data["last_completed_at"]).date()
                    if completed_date == today:
                        count += 1
                except (ValueError, TypeError):
                    continue
        
        return count


class PendingValidationsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for pending validations."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_pending_validations"
        self._attr_icon = "mdi:clock-alert"

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
                child_name = "Unknown"
                if task_data.get("assigned_child_id"):
                    child_data = self.coordinator.data["children"].get(task_data["assigned_child_id"], {})
                    child_name = child_data.get("name", "Unknown")
                
                pending_tasks.append({
                    "task_id": task_id,
                    "name": task_data.get("name", ""),
                    "child": child_name,
                    "points": task_data.get("points", 0),
                })
        
        return {"pending_tasks": pending_tasks}


class TotalTasksCompletedTodaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for total tasks completed today."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_total_tasks_today"
        self._attr_icon = "mdi:check-all"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Total Tâches Aujourd'hui"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        today = datetime.now().date()
        count = 0
        
        for task_data in self.coordinator.data.get("tasks", {}).values():
            if (task_data.get("status") == "validated" and
                task_data.get("last_completed_at")):
                try:
                    completed_date = datetime.fromisoformat(task_data["last_completed_at"]).date()
                    if completed_date == today:
                        count += 1
                except (ValueError, TypeError):
                    continue
        
        return count


class ActiveTasksSensor(CoordinatorEntity, SensorEntity):
    """Sensor for active tasks."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_active_tasks"
        self._attr_icon = "mdi:format-list-checks"

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