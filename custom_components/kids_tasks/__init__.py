# ============================================================================
# __init__.py
# ============================================================================

"""The Kids Tasks integration."""
from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_VERSION, STORAGE_KEY
from .coordinator import KidsTasksDataUpdateCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.CALENDAR,
    Platform.SWITCH,
]


@dataclass
class KidsTasksData:
    """Runtime data stored on the config entry."""
    coordinator: KidsTasksDataUpdateCoordinator


KidsTasksConfigEntry = ConfigEntry[KidsTasksData]


def _deploy_frontend(config_dir: str) -> None:
    """Copy the bundled JS card file to the HA www directory."""
    src = Path(__file__).parent / "lovelace" / "kids-tasks-card.js"
    dst = Path(config_dir) / "www" / "kids_tasks" / "kids-tasks-card.js"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


async def async_setup_entry(hass: HomeAssistant, entry: KidsTasksConfigEntry) -> bool:
    """Set up Kids Tasks from a config entry."""
    await hass.async_add_executor_job(_deploy_frontend, hass.config.config_dir)

    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    coordinator = KidsTasksDataUpdateCoordinator(hass, store, entry.entry_id)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = KidsTasksData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: KidsTasksConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        for service_name in list(hass.services.async_services().get(DOMAIN, {}).keys()):
            hass.services.async_remove(DOMAIN, service_name)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry."""
    storage = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    await storage.async_remove()

    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    for entity_entry in entries:
        registry.async_remove(entity_entry.entity_id)

    _LOGGER.info("Kids Tasks integration removed, storage cleared, and %d entities removed", len(entries))