"""Persistent storage and schema migration for the Kids Tasks integration.

Home Assistant's :class:`~homeassistant.helpers.storage.Store` checks the
version written in the ``.storage`` file *before* handing the payload back.
When that version is older than the one requested it calls
``_async_migrate_func()``, whose default implementation raises
``NotImplementedError``. A migration performed on the *result* of
``async_load()`` is therefore never reached on an existing installation.

This module owns the migration so it runs where Home Assistant expects it.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)


def migrate_payload(data: dict[str, Any], from_version: int) -> dict[str, Any]:
    """Bring a stored payload up to :data:`STORAGE_VERSION`.

    Safe to call on data that is already current: every step is guarded and
    idempotent. An empty payload is returned untouched so a first install is
    not mistaken for a migration.
    """
    if not data:
        return data

    if from_version < 2:
        data = _migrate_v1_to_v2(data)

    data["version"] = STORAGE_VERSION
    return data


def _migrate_v1_to_v2(data: dict[str, Any]) -> dict[str, Any]:
    """v1 → v2: single assigned child becomes a list, children gain coins."""
    tasks = data.get("tasks") or {}
    for task in tasks.values():
        legacy_id = task.pop("assigned_child_id", None)
        if "assigned_child_ids" not in task:
            task["assigned_child_ids"] = [legacy_id] if legacy_id else []

    children = data.get("children") or {}
    for child in children.values():
        child.setdefault("coins", 0)

    _LOGGER.info(
        "Migrated Kids Tasks storage v1 to v2 (%d tasks, %d children)",
        len(tasks),
        len(children),
    )
    return data


class KidsTasksStore(Store[dict[str, Any]]):
    """Store that migrates its own payload when the schema version changes."""

    async def _async_migrate_func(
        self,
        old_major_version: int,
        old_minor_version: int,
        old_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Upgrade a payload written by an older version of the integration."""
        _LOGGER.info(
            "Kids Tasks storage migration: v%s.%s -> v%s",
            old_major_version,
            old_minor_version,
            STORAGE_VERSION,
        )
        return migrate_payload(old_data, old_major_version)


def async_get_store(hass: HomeAssistant) -> KidsTasksStore:
    """Return the storage handler for this integration."""
    return KidsTasksStore(hass, STORAGE_VERSION, STORAGE_KEY)
