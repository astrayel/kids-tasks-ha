# ============================================================================
# select.py
# ============================================================================

"""Select platform for Kids Tasks integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TASK_STATUSES, CATEGORIES, FREQUENCIES
from .coordinator import KidsTasksDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    # Add task status selects
    for task_id in coordinator.data.get("tasks", {}):
        entities.append(TaskStatusSelect(coordinator, task_id))
    
    async_add_entities(entities)


class TaskStatusSelect(CoordinatorEntity, SelectEntity):
    """Select entity for task status."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"KT_status_{task_id}"
        self._attr_entity_id = f"select.kt_status_{task_id}"
        self._attr_options = ["À faire", "En cours", "Terminé", "En attente validation", "Validé", "Échoué"]
        self._attr_icon = "mdi:format-list-bulleted"

    @property
    def name(self) -> str:
        """Return the name of the select."""
        task_name = self.coordinator.data["tasks"].get(self.task_id, {}).get("name", "Unknown Task")
        return f"Statut: {task_name}"

    @property
    def current_option(self) -> str:
        """Return the selected option."""
        status = self.coordinator.data["tasks"].get(self.task_id, {}).get("status", "todo")
        status_map = {
            "todo": "À faire",
            "in_progress": "En cours",
            "completed": "Terminé",
            "pending_validation": "En attente validation",
            "validated": "Validé",
            "failed": "Échoué",
        }
        return status_map.get(status, "À faire")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        option_map = {
            "À faire": "todo",
            "En cours": "in_progress",
            "Terminé": "completed",
            "En attente validation": "pending_validation",
            "Validé": "validated",
            "Échoué": "failed",
        }
        
        new_status = option_map.get(option, "todo")
        
        if self.task_id in self.coordinator.tasks:
            self.coordinator.tasks[self.task_id].status = new_status
            await self.coordinator.async_save_data()
            await self.coordinator.async_request_refresh()