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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def get_safe_child_name(coordinator, child_id: str) -> str:
    """Get a safe name for entity_id from child data."""
    import re
    child_data = coordinator.children.get(child_id, {})
    child_name = child_data.name if hasattr(child_data, 'name') else str(child_data.get('name', f'child_{child_id[:8]}'))
    safe_child_name = child_name.lower().replace(' ', '_').replace('-', '_').replace('é', 'e').replace('è', 'e').replace('à', 'a').replace('ç', 'c')
    # Remove special characters and keep only alphanumeric and underscores
    safe_child_name = re.sub(r'[^a-z0-9_]', '', safe_child_name)
    return safe_child_name


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    _LOGGER.info("🔧 NOUVELLE VERSION SENSOR - Setting up sensor platform with TaskSensor support")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    # Store the add_entities callback for dynamic entity creation
    hass.data[DOMAIN][config_entry.entry_id]["async_add_entities"] = async_add_entities
    
    entities = []
    
    # Add child sensors
    for child_id, child_data in coordinator.data.get("children", {}).items():
        entities.extend([
            ChildPointsSensor(coordinator, child_id),
            ChildLevelSensor(coordinator, child_id),
            ChildTasksCompletedTodaySensor(coordinator, child_id),
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
    ])
    
    async_add_entities(entities)


class ChildPointsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for child points."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        # Use child name for both unique_id and entity_id (safe for HA compatibility)
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_points"
        self._attr_device_class = None  # Remove problematic device class
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_icon = "mdi:star"
        self._attr_native_unit_of_measurement = "points"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_points"

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
            "avatar": child_data.get("avatar", "👶"),
            "person_entity_id": child_data.get("person_entity_id"),
            "avatar_type": child_data.get("avatar_type", "emoji"),
            "avatar_data": child_data.get("avatar_data"),
            "card_gradient_start": child_data.get("card_gradient_start"),
            "card_gradient_end": child_data.get("card_gradient_end")
        }


class ChildLevelSensor(CoordinatorEntity, SensorEntity):
    """Sensor for child level."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, child_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.child_id = child_id
        # Use child name for both unique_id and entity_id (safe for HA compatibility)
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_level"
        self._attr_icon = "mdi:trophy"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_level"

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
        # Use child name for both unique_id and entity_id (safe for HA compatibility)
        safe_child_name = get_safe_child_name(coordinator, child_id)
        self._attr_unique_id = f"kidtasks_{safe_child_name}_tasks_today"
        self._attr_icon = "mdi:check-circle"
        self.entity_id = f"sensor.kidtasks_{safe_child_name}_tasks_today"

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
        
        from .const import (
            CATEGORIES, FREQUENCIES, CATEGORY_LABELS, CATEGORY_ICONS,
            REWARD_CATEGORIES, REWARD_CATEGORY_LABELS, REWARD_CATEGORY_ICONS
        )
        
        return {
            "pending_tasks": pending_tasks,
            "available_categories": CATEGORIES,
            "available_frequencies": FREQUENCIES,
            "category_labels": CATEGORY_LABELS,
            "category_icons": CATEGORY_ICONS,
            "available_reward_categories": REWARD_CATEGORIES,
            "reward_category_labels": REWARD_CATEGORY_LABELS,
            "reward_category_icons": REWARD_CATEGORY_ICONS
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
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Total Tâches Aujourd'hui"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        today = datetime.now().date()
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


class AllTasksListSensor(CoordinatorEntity, SensorEntity):
    """Sensor that shows all tasks with their details."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"kidtasks_all_tasks_list"
        self._attr_icon = "mdi:format-list-bulleted"
        self.entity_id = f"sensor.kidtasks_all_tasks_list"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Liste de Toutes les Tâches"

    @property
    def native_value(self) -> int:
        """Return the total number of tasks."""
        return len(self.coordinator.data.get("tasks", {}))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes with all tasks details."""
        all_tasks = []
        
        for task_id, task_data in self.coordinator.data.get("tasks", {}).items():
            # Get child name if assigned
            child_name = "Non assigné"
            if task_data.get("assigned_child_id"):
                child_data = self.coordinator.data.get("children", {}).get(task_data["assigned_child_id"], {})
                child_name = child_data.get("name", "Enfant inconnu")
            
            # Format status for display
            status_display = {
                "todo": "À faire",
                "in_progress": "En cours", 
                "completed": "Terminé",
                "pending_validation": "En attente de validation",
                "validated": "Validé",
                "failed": "Échoué"
            }.get(task_data.get("status", "todo"), "Statut inconnu")
            
            # Format frequency for display
            frequency_display = {
                "daily": "Quotidienne",
                "weekly": "Hebdomadaire",
                "monthly": "Mensuelle",
                "once": "Une fois"
            }.get(task_data.get("frequency", "daily"), "Inconnue")
            
            all_tasks.append({
                "task_id": task_id,
                "name": task_data.get("name", "Tâche sans nom"),
                "description": task_data.get("description", ""),
                "category": task_data.get("category", "other").title(),
                "points": task_data.get("points", 0),
                "frequency": frequency_display,
                "status": status_display,
                "assigned_child": child_name,
                "validation_required": task_data.get("validation_required", False),
                "active": task_data.get("active", True),
                "created_at": task_data.get("created_at"),
                "last_completed_at": task_data.get("last_completed_at"),
                "completion_count": task_data.get("completion_count", 0)
            })
        
        # Sort by name for consistent display
        all_tasks.sort(key=lambda x: x["name"])
        
        return {
            "tasks": all_tasks,
            "total_count": len(all_tasks),
            "active_count": sum(1 for task in all_tasks if task["active"]),
            "completed_today_count": len([
                task for task in all_tasks 
                if task["last_completed_at"] and 
                task["last_completed_at"].startswith(datetime.now().strftime("%Y-%m-%d"))
            ])
        }


class AllRewardsListSensor(CoordinatorEntity, SensorEntity):
    """Sensor that shows all rewards with their details."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"kidtasks_all_rewards_list"
        self._attr_icon = "mdi:gift"
        self.entity_id = f"sensor.kidtasks_all_rewards_list"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Liste de Toutes les Récompenses"

    @property
    def native_value(self) -> int:
        """Return the total number of rewards."""
        return len(self.coordinator.data.get("rewards", {}))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes with all rewards details."""
        all_rewards = []
        
        for reward_id, reward_data in self.coordinator.data.get("rewards", {}).items():
            all_rewards.append({
                "reward_id": reward_id,
                "name": reward_data.get("name", "Récompense sans nom"),
                "description": reward_data.get("description", ""),
                "cost": reward_data.get("cost", 50),
                "category": reward_data.get("category", "fun").title(),
                "active": reward_data.get("active", True),
                "limited_quantity": reward_data.get("limited_quantity"),
                "remaining_quantity": reward_data.get("remaining_quantity"),
                "is_available": reward_data.get("remaining_quantity") is None or reward_data.get("remaining_quantity", 0) > 0,
            })
        
        # Sort by cost for logical display
        all_rewards.sort(key=lambda x: x["cost"])
        
        return {
            "rewards": all_rewards,
            "total_count": len(all_rewards),
            "active_count": sum(1 for reward in all_rewards if reward["active"]),
            "available_count": sum(1 for reward in all_rewards if reward["is_available"] and reward["active"])
        }


class TaskSensor(CoordinatorEntity, SensorEntity):
    """Individual sensor for each task."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"kidtasks_task_{task_id}"
        # L'icône sera définie dynamiquement dans la propriété icon
        # Force the entity_id format we want (replace hyphens with underscores for HA compatibility)
        safe_task_id = task_id.replace("-", "_")
        self.entity_id = f"sensor.kidtasks_task_{safe_task_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        task_name = task_data.get("name", "Tâche inconnue")
        return f"Tâche: {task_name}"

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
        
        # Get child name if assigned
        child_name = "Non assigné"
        if task_data.get("assigned_child_id"):
            child_data = self.coordinator.data.get("children", {}).get(task_data["assigned_child_id"], {})
            child_name = child_data.get("name", "Enfant inconnu")
        
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
            "assigned_child_name": child_name,
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
        # L'icône sera définie dynamiquement dans la propriété icon
        # Force the entity_id format we want (replace hyphens with underscores for HA compatibility)
        safe_reward_id = reward_id.replace("-", "_")
        self.entity_id = f"sensor.kidtasks_reward_{safe_reward_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        reward_data = self.coordinator.data["rewards"].get(self.reward_id, {})
        reward_name = reward_data.get("name", "Récompense inconnue")
        return f"Récompense: {reward_name}"

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
        
        return {
            "reward_id": self.reward_id,
            "reward_name": reward_data.get("name", ""),
            "description": reward_data.get("description", ""),
            "cost": reward_data.get("cost", 50),
            "coin_cost": reward_data.get("coin_cost", 0),
            "category": reward_data.get("category", "fun"),
            "icon": reward_data.get("icon"),
            "active": reward_data.get("active", True),
            "limited_quantity": reward_data.get("limited_quantity"),
            "remaining_quantity": reward_data.get("remaining_quantity"),
            "is_available": reward_data.get("remaining_quantity") is None or reward_data.get("remaining_quantity", 0) > 0,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.reward_id in self.coordinator.data.get("rewards", {})