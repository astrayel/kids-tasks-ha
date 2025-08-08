# ============================================================================
# __init__.py
# ============================================================================

"""The Kids Tasks integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
import os

from .const import DOMAIN, STORAGE_VERSION, STORAGE_KEY
from .coordinator import KidsTasksDataUpdateCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kids Tasks from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize storage
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    
    # Create coordinator
    coordinator = KidsTasksDataUpdateCoordinator(hass, store)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "store": store,
    }
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup services
    await async_setup_services(hass, coordinator)
    
    # Register frontend resources
    integration_dir = os.path.dirname(__file__)
    hass.http.register_static_path(
        f"/{DOMAIN}",
        integration_dir,
        cache_headers=False
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok