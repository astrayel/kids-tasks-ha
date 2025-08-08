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
from homeassistant.components.frontend import add_extra_js_url

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
    
    # Register frontend resources - works for both HACS and manual installs
    integration_dir = os.path.dirname(__file__)
    
    # Try to register with HACS paths first, fallback to integration directory
    try:
        # HACS style registration
        add_extra_js_url(hass, f"/hacsfiles/{DOMAIN}/kids-tasks-card.js")
        add_extra_js_url(hass, f"/hacsfiles/{DOMAIN}/kids-tasks-manager.js") 
        add_extra_js_url(hass, f"/hacsfiles/{DOMAIN}/kids-tasks-forms.js")
        add_extra_js_url(hass, f"/hacsfiles/{DOMAIN}/kids-tasks-data.js")
        add_extra_js_url(hass, f"/hacsfiles/{DOMAIN}/kids-tasks-complete.js")
        _LOGGER.info("Registered frontend resources via HACS paths")
    except Exception as e:
        _LOGGER.warning(f"Could not register HACS paths, trying direct paths: {e}")
        # Fallback to direct paths
        try:
            add_extra_js_url(hass, f"/local/{DOMAIN}/kids-tasks-card.js")
            add_extra_js_url(hass, f"/local/{DOMAIN}/kids-tasks-manager.js")
            add_extra_js_url(hass, f"/local/{DOMAIN}/kids-tasks-forms.js") 
            add_extra_js_url(hass, f"/local/{DOMAIN}/kids-tasks-data.js")
            add_extra_js_url(hass, f"/local/{DOMAIN}/kids-tasks-complete.js")
            _LOGGER.info("Registered frontend resources via local paths")
        except Exception as e2:
            _LOGGER.error(f"Failed to register frontend resources: {e2}")
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok