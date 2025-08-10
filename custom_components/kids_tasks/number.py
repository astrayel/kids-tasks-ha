# ============================================================================
# number.py
# ============================================================================

"""Number platform for Kids Tasks integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
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
    """Set up number platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    # Add task points numbers
    for task_id in coordinator.data.get("tasks", {}):
        entities.append(TaskPointsNumber(coordinator, task_id))
    
    async_add_entities(entities)


class TaskPointsNumber(CoordinatorEntity, NumberEntity):
    """Number entity for task points."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"KT_points_{task_id}"
        self._attr_entity_id = f"number.kt_points_{task_id}"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_icon = "mdi:star"

    @property
    def name(self) -> str:
        """Return the name of the number."""
        task_name = self.coordinator.data["tasks"].get(self.task_id, {}).get("name", "Unknown Task")
        return f"Points: {task_name}"

    @property
    def native_value(self) -> float:
        """Return the value of the number."""
        return self.coordinator.data["tasks"].get(self.task_id, {}).get("points", 10)

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        if self.task_id in self.coordinator.tasks:
            self.coordinator.tasks[self.task_id].points = int(value)
            await self.coordinator.async_save_data()
            await self.coordinator.async_request_refresh()