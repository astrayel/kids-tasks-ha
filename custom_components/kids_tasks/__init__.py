# ============================================================================
# __init__.py
# ============================================================================

"""The Kids Tasks integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN
from .coordinator import KidsTasksDataUpdateCoordinator
from .services import async_setup_services
from .sensor import CHILD_SUFFIXES, child_unique_id
from .storage import async_get_store

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CALENDAR,
    Platform.SWITCH,
]

# Platforms this integration used to provide, purged from the registry on
# setup so no stale, unavailable rows are left behind.
#
# number/select wrote straight to the coordinator, bypassing the permission
# guard entirely — a child could set a task to "validated" or raise its points
# from the entity UI. button only ever created its entities at startup, so a
# task added later had none, and the validate button was only created for
# tasks already pending at boot. With three children and twenty tasks these
# three platforms tripled the entity count for no benefit the cards don't
# cover better.
REMOVED_PLATFORMS: set[str] = {"number", "select", "button"}

@dataclass
class KidsTasksData:
    """Runtime data stored on the config entry."""
    coordinator: KidsTasksDataUpdateCoordinator


KidsTasksConfigEntry = ConfigEntry[KidsTasksData]


async def async_setup_entry(hass: HomeAssistant, entry: KidsTasksConfigEntry) -> bool:
    """Set up Kids Tasks from a config entry."""
    store = async_get_store(hass)
    coordinator = KidsTasksDataUpdateCoordinator(hass, store, entry.entry_id)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = KidsTasksData(coordinator=coordinator)

    _async_migrate_child_unique_ids(hass, entry)
    _async_purge_removed_platforms(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass, coordinator)

    return True


def _async_migrate_child_unique_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Re-key child sensors from the child's name to the child's id.

    Child sensors used to be identified by a slug of the child's name, so
    renaming a child created a fresh set of entities and orphaned the old
    ones — losing their recorded history. The child is recovered from the
    entity's device, whose identifier already carries the immutable child id,
    so this works even for a child renamed before the migration ran.
    """
    registry = er.async_get(hass)
    devices = dr.async_get(hass)
    migrated = 0

    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity.domain != "sensor" or entity.unique_id.startswith("kidtasks_child_"):
            continue
        if entity.device_id is None:
            continue

        device = devices.async_get(entity.device_id)
        if device is None:
            continue

        child_id = next(
            (ident for domain, ident in device.identifiers
             if domain == DOMAIN and ident != DOMAIN),
            None,
        )
        if child_id is None:
            continue

        suffix = next(
            (s for s in CHILD_SUFFIXES if entity.unique_id.endswith(f"_{s}")), None
        )
        if suffix is None:
            continue

        new_unique_id = child_unique_id(child_id, suffix)
        if registry.async_get_entity_id("sensor", DOMAIN, new_unique_id):
            continue  # already migrated on a previous run

        registry.async_update_entity(entity.entity_id, new_unique_id=new_unique_id)
        migrated += 1

    if migrated:
        _LOGGER.info("Re-keyed %d child sensors to id-based unique_ids", migrated)


def _async_purge_removed_platforms(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Drop registry entries belonging to platforms we no longer provide."""
    registry = er.async_get(hass)
    stale = [
        entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        if entity.domain in REMOVED_PLATFORMS
    ]
    for entity_id in stale:
        registry.async_remove(entity_id)
    if stale:
        _LOGGER.info("Removed %d entities from retired platforms", len(stale))


async def async_unload_entry(hass: HomeAssistant, entry: KidsTasksConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        for service_name in list(hass.services.async_services().get(DOMAIN, {}).keys()):
            hass.services.async_remove(DOMAIN, service_name)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove a config entry.

    Only called when the integration is deleted by the user — never on a
    reload — so wiping the store here is intentional.
    """
    storage = async_get_store(hass)
    await storage.async_remove()

    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    for entity_entry in entries:
        registry.async_remove(entity_entry.entity_id)

    _LOGGER.info("Kids Tasks integration removed, storage cleared, and %d entities removed", len(entries))