"""Services for Kids Tasks integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import config_validation as cv

from ..const import DOMAIN
from ..permissions import build_registrar
from ._child_services import register_child_services
from ._task_services import register_task_services
from ._reward_services import register_reward_services

if TYPE_CHECKING:
    from ..coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_BACKUP_DATA = "backup_data"
SERVICE_RESTORE_DATA = "restore_data"
SERVICE_CLEAR_ALL_DATA = "clear_all_data"

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
    coordinator: KidsTasksDataUpdateCoordinator,
) -> None:
    """Set up all services."""
    register_child_services(hass, coordinator)
    register_task_services(hass, coordinator)
    register_reward_services(hass, coordinator)
    _register_system_services(hass, coordinator)


def _register_system_services(
    hass: HomeAssistant,
    coordinator: KidsTasksDataUpdateCoordinator,
) -> None:
    """Register backup/restore/clear system services."""

    register = build_registrar(hass, coordinator)

    async def backup_data_service(call: ServiceCall) -> ServiceResponse:
        """Return the full backup as the service response.

        Previously the payload was only written to the log, truncated to its
        first 100 characters, which made it impossible to actually recover.
        """
        include_history = call.data.get("include_history", True)
        backup = await coordinator.async_backup_data(include_history)
        _LOGGER.info("Data backup created (%d bytes)", len(backup))
        return {
            "backup_data": backup,
            "children": len(coordinator.children),
            "tasks": len(coordinator.tasks),
            "rewards": len(coordinator.rewards),
        }

    async def restore_data_service(call: ServiceCall) -> None:
        await coordinator.async_restore_data(call.data["backup_data"])

    async def clear_all_data_service(call: ServiceCall) -> None:
        try:
            _LOGGER.info("Starting to clear all data...")
            await coordinator.async_clear_all_data()
            _LOGGER.info("All data cleared successfully")
        except Exception as e:
            _LOGGER.error("Failed to clear data: %s", e)
            raise

    register(
        SERVICE_BACKUP_DATA,
        backup_data_service,
        schema=SERVICE_BACKUP_DATA_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    register(SERVICE_RESTORE_DATA, restore_data_service, schema=SERVICE_RESTORE_DATA_SCHEMA)
    register(SERVICE_CLEAR_ALL_DATA, clear_all_data_service)
