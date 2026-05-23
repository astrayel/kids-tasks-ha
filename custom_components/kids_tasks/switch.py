"""Switch platform for Kids Tasks — toggle to complete/reset a task."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CATEGORY_ICONS, TASK_STATUS_VALIDATED, TASK_STATUS_TODO
from .coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform and register a listener for new tasks/children."""
    coordinator: KidsTasksDataUpdateCoordinator = entry.runtime_data.coordinator

    def _add_new_switches() -> None:
        registry = er.async_get(hass)
        existing = {
            e.unique_id
            for e in er.async_entries_for_config_entry(registry, entry.entry_id)
            if e.domain == "switch"
        }
        new_entities = []
        for task_id, task in coordinator.tasks.items():
            for child_id in task.assigned_child_ids:
                uid = f"kidtasks_switch_{task_id}_{child_id}"
                if uid not in existing:
                    new_entities.append(TaskSwitch(coordinator, task_id, child_id))
        if new_entities:
            async_add_entities(new_entities)

    _add_new_switches()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_switches))


class TaskSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to complete or reset a task for a specific child.

    ON  = task validated (or completed pending validation)
    OFF = task reset to todo
    """

    def __init__(
        self,
        coordinator: KidsTasksDataUpdateCoordinator,
        task_id: str,
        child_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._task_id = task_id
        self._child_id = child_id
        self._attr_unique_id = f"kidtasks_switch_{task_id}_{child_id}"

    @property
    def _task(self) -> dict[str, Any]:
        return self.coordinator.data.get("tasks", {}).get(self._task_id, {})

    @property
    def _child(self) -> dict[str, Any]:
        return self.coordinator.data.get("children", {}).get(self._child_id, {})

    @property
    def _child_status(self) -> dict[str, Any]:
        return self._task.get("child_statuses", {}).get(self._child_id, {})

    @property
    def name(self) -> str:
        task_name = self._task.get("name", "Tâche")
        child_name = self._child.get("name", "Enfant")
        return f"{task_name} — {child_name}"

    @property
    def entity_id(self) -> str:
        return f"switch.kidtasks_{self._task_id[:8]}_{self._child_id[:8]}"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        pass

    @property
    def icon(self) -> str:
        cat = self._task.get("category", "other")
        return f"mdi:{'check-circle' if self.is_on else 'circle-outline'}"

    @property
    def is_on(self) -> bool:
        status = self._child_status.get("status") or self._task.get("status", TASK_STATUS_TODO)
        return status in (TASK_STATUS_VALIDATED, "completed", "pending_validation")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        status = self._child_status.get("status") or self._task.get("status", TASK_STATUS_TODO)
        return {
            "task_id": self._task_id,
            "child_id": self._child_id,
            "task_name": self._task.get("name"),
            "child_name": self._child.get("name"),
            "status": status,
            "points": self._task.get("points", 0),
            "category": self._task.get("category", "other"),
            "validation_required": self._task.get("validation_required", True),
        }

    @property
    def device_info(self) -> DeviceInfo:
        child_name = self._child.get("name", "Enfant")
        return DeviceInfo(
            identifiers={(DOMAIN, self._child_id)},
            name=f"Kids Tasks — {child_name}",
            manufacturer="Kids Tasks",
            model="Child",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Complete the task for this child."""
        await self.coordinator.async_complete_task(
            self._task_id,
            self._child_id,
            validation_required=self._task.get("validation_required", True),
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Reset the task to todo for this child."""
        task = self.coordinator.tasks.get(self._task_id)
        if task:
            task.reset()
            await self.coordinator.async_save_data()
            await self.coordinator.async_request_refresh()
