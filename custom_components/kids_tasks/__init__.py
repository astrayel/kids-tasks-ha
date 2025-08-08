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
import shutil
from pathlib import Path
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


async def _setup_frontend_resources(hass: HomeAssistant) -> None:
    """Setup frontend resources - copy JS files and register them."""
    integration_dir = Path(__file__).parent
    js_files = [
        "kids-tasks-card.js",
        "kids-tasks-manager.js", 
        "kids-tasks-forms.js",
        "kids-tasks-data.js",
        "kids-tasks-complete.js"
    ]
    
    # Try HACS directory first
    hacs_dir = Path(hass.config.path("www/community", DOMAIN))
    local_dir = Path(hass.config.path("www", DOMAIN))
    
    target_dir = None
    
    # Check if HACS directory exists (preferred)
    if hacs_dir.parent.exists():
        target_dir = hacs_dir
        url_prefix = f"/hacsfiles/{DOMAIN}"
    else:
        target_dir = local_dir
        url_prefix = f"/local/{DOMAIN}"
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy JS files
    copied_files = []
    for js_file in js_files:
        source_file = integration_dir / js_file
        target_file = target_dir / js_file
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                copied_files.append(js_file)
                _LOGGER.debug(f"Copied {js_file} to {target_file}")
            except Exception as e:
                _LOGGER.error(f"Failed to copy {js_file}: {e}")
        else:
            _LOGGER.warning(f"Source file not found: {source_file}")
    
    # Register the copied files
    for js_file in copied_files:
        try:
            add_extra_js_url(hass, f"{url_prefix}/{js_file}")
            _LOGGER.debug(f"Registered {url_prefix}/{js_file}")
        except Exception as e:
            _LOGGER.error(f"Failed to register {js_file}: {e}")
    
    _LOGGER.info(f"Frontend setup complete: copied {len(copied_files)} files to {target_dir}")


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
    
    # Setup frontend resources - copy JS files and register them
    await _setup_frontend_resources(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok