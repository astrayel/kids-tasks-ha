"""Tests for storage migration and the save guard (BUG-002)."""
from __future__ import annotations

import json

import pytest

from custom_components.kids_tasks.const import STORAGE_VERSION
from custom_components.kids_tasks.storage import (
    KidsTasksStore,
    migrate_payload,
)


def _v1_payload() -> dict:
    """A payload as written by version 1 of the integration."""
    return {
        "version": 1,
        "children": {
            "child-1": {
                "id": "child-1",
                "name": "Léo",
                "points": 320,
                "level": 4,
                "created_at": "2024-01-01T08:00:00",
            }
        },
        "tasks": {
            "task-1": {
                "id": "task-1",
                "name": "Ranger la chambre",
                "assigned_child_id": "child-1",
                "created_at": "2024-01-01T08:00:00",
            },
            "task-2": {
                "id": "task-2",
                "name": "Tâche sans enfant",
                "created_at": "2024-01-01T08:00:00",
            },
        },
        "rewards": {},
    }


# ---------------------------------------------------------------------------
# migrate_payload
# ---------------------------------------------------------------------------

class TestMigratePayload:
    def test_v1_task_gains_assigned_child_ids_list(self):
        data = migrate_payload(_v1_payload(), 1)
        assert data["tasks"]["task-1"]["assigned_child_ids"] == ["child-1"]

    def test_v1_legacy_key_is_dropped(self):
        data = migrate_payload(_v1_payload(), 1)
        assert "assigned_child_id" not in data["tasks"]["task-1"]

    def test_v1_task_without_child_gets_empty_list(self):
        data = migrate_payload(_v1_payload(), 1)
        assert data["tasks"]["task-2"]["assigned_child_ids"] == []

    def test_v1_child_gains_coins(self):
        data = migrate_payload(_v1_payload(), 1)
        assert data["children"]["child-1"]["coins"] == 0

    def test_existing_data_is_preserved(self):
        data = migrate_payload(_v1_payload(), 1)
        assert data["children"]["child-1"]["points"] == 320
        assert data["children"]["child-1"]["name"] == "Léo"
        assert data["tasks"]["task-1"]["name"] == "Ranger la chambre"

    def test_version_is_bumped(self):
        data = migrate_payload(_v1_payload(), 1)
        assert data["version"] == STORAGE_VERSION

    def test_empty_payload_is_untouched(self):
        assert migrate_payload({}, 1) == {}

    def test_is_idempotent(self):
        once = migrate_payload(_v1_payload(), 1)
        twice = migrate_payload(json.loads(json.dumps(once)), STORAGE_VERSION)
        assert once == twice

    def test_v2_payload_keeps_its_child_list(self):
        payload = {
            "version": 2,
            "tasks": {"t": {"id": "t", "assigned_child_ids": ["a", "b"]}},
        }
        data = migrate_payload(payload, 2)
        assert data["tasks"]["t"]["assigned_child_ids"] == ["a", "b"]

    def test_existing_coins_are_not_reset(self):
        payload = {"version": 1, "children": {"c": {"id": "c", "coins": 42}}}
        data = migrate_payload(payload, 1)
        assert data["children"]["c"]["coins"] == 42


# ---------------------------------------------------------------------------
# KidsTasksStore — the migration must run where Home Assistant calls it
# ---------------------------------------------------------------------------

class TestKidsTasksStore:
    async def test_migrate_func_upgrades_v1_data(self, mock_hass):
        store = KidsTasksStore.__new__(KidsTasksStore)
        migrated = await store._async_migrate_func(1, 0, _v1_payload())
        assert migrated["tasks"]["task-1"]["assigned_child_ids"] == ["child-1"]
        assert migrated["version"] == STORAGE_VERSION

    async def test_migrate_func_does_not_raise_not_implemented(self):
        """The default Store implementation raises — ours must not."""
        store = KidsTasksStore.__new__(KidsTasksStore)
        try:
            await store._async_migrate_func(1, 0, _v1_payload())
        except NotImplementedError:  # pragma: no cover
            pytest.fail("KidsTasksStore must implement _async_migrate_func")


# ---------------------------------------------------------------------------
# Save guard
# ---------------------------------------------------------------------------

class TestSaveGuard:
    async def test_save_is_refused_before_load(self, coordinator):
        coordinator._storage_loaded = False
        await coordinator.async_save_data()
        coordinator.store.async_save.assert_not_called()

    async def test_save_is_allowed_after_load(self, coordinator):
        coordinator._storage_loaded = True
        await coordinator.async_save_data()
        coordinator.store.async_save.assert_called_once()

    async def test_load_marks_storage_as_loaded(self, coordinator):
        coordinator._storage_loaded = False
        coordinator.store.async_load.return_value = None
        await coordinator._load_data()
        assert coordinator._storage_loaded is True

    async def test_load_applies_migration_to_legacy_payload(self, coordinator):
        """A payload whose inner version is stale is still migrated."""
        coordinator.store.async_load.return_value = _v1_payload()
        await coordinator._load_data()
        assert coordinator.tasks["task-1"].assigned_child_ids == ["child-1"]
        assert coordinator.children["child-1"].coins == 0
