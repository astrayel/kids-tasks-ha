"""Storage mixin for Kids Tasks coordinator."""
from __future__ import annotations

import json
import logging
from datetime import datetime

from homeassistant.util import dt as dt_util

from ..const import DOMAIN, STORAGE_VERSION
from ..models import Child, Task, Reward
from ..storage import migrate_payload

_LOGGER = logging.getLogger("custom_components.kids_tasks.coordinator")


class StorageMixin:
    async def _migrate_data(self, data: dict) -> dict:
        """Migrate a payload to the current schema version.

        The Store itself migrates on load (see ``storage.KidsTasksStore``);
        this remains the entry point for payloads that arrive outside that
        path — restored backups above all — and is idempotent.
        """
        return migrate_payload(data, data.get("version", 1))

    async def _load_data(self) -> None:
        """Load data from storage."""
        raw = await self.store.async_load() or {}
        data = await self._migrate_data(raw)

        # Load children
        children_data = data.get("children", {})
        self.children = {
            child_id: Child.from_dict(child_data)
            for child_id, child_data in children_data.items()
        }

        # Load tasks
        tasks_data = data.get("tasks", {})
        self.tasks = {
            task_id: Task.from_dict(task_data)
            for task_id, task_data in tasks_data.items()
        }

        # Load rewards
        rewards_data = data.get("rewards", {})
        self.rewards = {
            reward_id: Reward.from_dict(reward_data)
            for reward_id, reward_data in rewards_data.items()
        }

        # Load system data (reset dates)
        system_data = data.get("system", {})

        # Parse reset dates
        if system_data.get("last_daily_reset"):
            try:
                self.last_daily_reset = datetime.fromisoformat(system_data["last_daily_reset"]).date()
            except ValueError:
                self.last_daily_reset = None

        if system_data.get("last_weekly_reset"):
            try:
                self.last_weekly_reset = datetime.fromisoformat(system_data["last_weekly_reset"]).date()
            except ValueError:
                self.last_weekly_reset = None

        if system_data.get("last_monthly_reset"):
            try:
                self.last_monthly_reset = datetime.fromisoformat(system_data["last_monthly_reset"]).date()
            except ValueError:
                self.last_monthly_reset = None

        # Only from here on is it safe to write: everything the store held is
        # now in memory, so a save can no longer erase it.
        self._storage_loaded = True

    async def async_save_data(self) -> None:
        """Save data to storage.

        Refuses to write before a successful load. Without this guard a save
        triggered by any service call while loading had failed would persist
        empty dictionaries over the user's real data.
        """
        if not getattr(self, "_storage_loaded", False):
            _LOGGER.error(
                "Refusing to save Kids Tasks data before storage was loaded — "
                "this would overwrite existing data"
            )
            return

        data = {
            "version": STORAGE_VERSION,
            "children": {child_id: child.to_dict() for child_id, child in self.children.items()},
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "rewards": {reward_id: reward.to_dict() for reward_id, reward in self.rewards.items()},
            "system": {
                "last_daily_reset": self.last_daily_reset.isoformat() if self.last_daily_reset else None,
                "last_weekly_reset": self.last_weekly_reset.isoformat() if self.last_weekly_reset else None,
                "last_monthly_reset": self.last_monthly_reset.isoformat() if self.last_monthly_reset else None,
            }
        }

        await self.store.async_save(data)

    async def async_clear_all_data(self) -> None:
        """Clear all data from storage."""
        _LOGGER.info("Clearing all data - children: %d, tasks: %d, rewards: %d",
                    len(self.children), len(self.tasks), len(self.rewards))

        self.children.clear()
        self.tasks.clear()
        self.rewards.clear()

        await self.async_save_data()

        # Force entity registry to reload
        await self.async_request_refresh()

        # Also fire event for potential UI updates
        self.hass.bus.async_fire(f"{DOMAIN}_data_cleared")

        _LOGGER.info("All data cleared and refresh requested")

    async def async_backup_data(self, include_history: bool = True) -> str:
        """Create a backup of all data."""
        backup_data = {
            "version": STORAGE_VERSION,
            "timestamp": dt_util.now().isoformat(),
            "children": {child_id: child.to_dict() for child_id, child in self.children.items()},
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "rewards": {reward_id: reward.to_dict() for reward_id, reward in self.rewards.items()},
        }

        return json.dumps(backup_data, indent=2)

    async def async_restore_data(self, backup_json: str) -> bool:
        """Restore data from a backup."""
        try:
            backup_data = await self._migrate_data(json.loads(backup_json))

            # Clear existing data
            self.children.clear()
            self.tasks.clear()
            self.rewards.clear()

            # Restore children
            for child_id, child_data in backup_data.get("children", {}).items():
                self.children[child_id] = Child.from_dict(child_data)

            # Restore tasks
            for task_id, task_data in backup_data.get("tasks", {}).items():
                self.tasks[task_id] = Task.from_dict(task_data)

            # Restore rewards
            for reward_id, reward_data in backup_data.get("rewards", {}).items():
                self.rewards[reward_id] = Reward.from_dict(reward_data)

            await self.async_save_data()
            await self.async_request_refresh()
            return True

        except Exception as e:
            _LOGGER.error("Failed to restore backup: %s", e)
            return False
