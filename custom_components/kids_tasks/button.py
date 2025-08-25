# ============================================================================
# button.py
# ============================================================================

"""Button platform for Kids Tasks integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    entities = []
    
    # Add task completion buttons for each active task
    for task_id, task_data in coordinator.data.get("tasks", {}).items():
        if task_data.get("active", True):
            entities.append(TaskCompleteButton(coordinator, task_id))
    
    # Add validation buttons for pending tasks
    for task_id, task_data in coordinator.data.get("tasks", {}).items():
        if task_data.get("status") == "pending_validation":
            entities.append(TaskValidateButton(coordinator, task_id))
    
    async_add_entities(entities)


class TaskCompleteButton(CoordinatorEntity, ButtonEntity):
    """Button to complete a task."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"{DOMAIN}_complete_{task_id}"
        self._attr_icon = "mdi:check"

    @property
    def name(self) -> str:
        """Return the name of the button."""
        task_name = self.coordinator.data["tasks"].get(self.task_id, {}).get("name", "Unknown Task")
        return f"Terminer: {task_name}"

    @property
    def available(self) -> bool:
        """Return if button is available."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        return task_data.get("status") in ["todo", "in_progress"]

    async def async_press(self) -> None:
        """Handle the button press."""
        # DEPRECATED: Generic task completion buttons are disabled
        # Task completion now requires specifying which child completed the task
        # Use the service with child_id parameter instead
        pass


class TaskValidateButton(CoordinatorEntity, ButtonEntity):
    """Button to validate a task."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, task_id: str) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.task_id = task_id
        self._attr_unique_id = f"{DOMAIN}_validate_{task_id}"
        self._attr_icon = "mdi:check-decagram"

    @property
    def name(self) -> str:
        """Return the name of the button."""
        task_name = self.coordinator.data["tasks"].get(self.task_id, {}).get("name", "Unknown Task")
        return f"Valider: {task_name}"

    @property
    def available(self) -> bool:
        """Return if button is available."""
        task_data = self.coordinator.data["tasks"].get(self.task_id, {})
        return task_data.get("status") == "pending_validation"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_validate_task(self.task_id)