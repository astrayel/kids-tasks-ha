# ============================================================================
# number.py
# ============================================================================

"""Number platform for Kids Tasks integration."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KidsTasksDataUpdateCoordinator

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
    """Set up number platform."""
    coordinator: KidsTasksDataUpdateCoordinator = config_entry.runtime_data.coordinator

    async_add_entities([
        TaskPointsNumber(coordinator, task_id)
        for task_id in coordinator.data.get("tasks", {})
    ])


class TaskPointsNumber(CoordinatorEntity, NumberEntity):
    """Number entity for task points."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"{DOMAIN}_points_{task_id}"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_icon = "mdi:star"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return _SYSTEM_DEVICE_INFO

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
