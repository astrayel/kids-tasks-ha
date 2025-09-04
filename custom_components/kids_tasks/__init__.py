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
    coordinator = KidsTasksDataUpdateCoordinator(hass, store, entry.entry_id)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "store": store,
    }
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup services
    await async_setup_services(hass, coordinator)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Remove services when unloading
        services_to_remove = [
            "add_child", "add_task", "add_reward", "complete_task", 
            "validate_task", "claim_reward", "reset_task", "clear_all_data",
            "cleanup_old_entities", "reset_all_daily_tasks", "reset_all_weekly_tasks",
            "reset_all_monthly_tasks", "set_points", "set_coins", "set_level"
        ]
        
        for service_name in services_to_remove:
            if hass.services.has_service(DOMAIN, service_name):
                hass.services.async_remove(DOMAIN, service_name)
        
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry."""
    # This is called when the user removes the integration
    from .const import STORAGE_KEY
    
    # Clear the storage data when integration is removed
    storage = hass.helpers.storage.Store(1, STORAGE_KEY)
    await storage.async_remove()
    
    # Force removal of any remaining entities
    entity_registry = hass.data["entity_registry"]
    entities_to_remove = []
    
    for entity_id, entity_entry in entity_registry.entities.items():
        if entity_entry.config_entry_id == entry.entry_id:
            entities_to_remove.append(entity_id)
    
    for entity_id in entities_to_remove:
        entity_registry.async_remove(entity_id)
    
    _LOGGER.info("Kids Tasks integration removed, storage cleared, and %d entities removed", len(entities_to_remove))