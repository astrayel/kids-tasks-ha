"""Data update coordinator for Kids Tasks integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from ..const import DOMAIN, DEFAULT_SCAN_INTERVAL
from ..models import Child, Task, Reward
from ._storage import StorageMixin
from ._resets import ResetsMixin
from ._deadlines import DeadlinesMixin
from ._business import BusinessMixin

_LOGGER = logging.getLogger(__name__)


class KidsTasksDataUpdateCoordinator(
    StorageMixin, ResetsMixin, DeadlinesMixin, BusinessMixin,
    DataUpdateCoordinator
):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, store: Store, config_entry_id: str | None = None) -> None:
        """Initialize."""
        self.store = store
        self.config_entry_id = config_entry_id
        self.children: dict[str, Child] = {}
        self.tasks: dict[str, Task] = {}
        self.rewards: dict[str, Reward] = {}

        self.last_daily_reset = None
        self.last_weekly_reset = None
        self.last_monthly_reset = None

        self._initialized = False
        self._reset_lock = asyncio.Lock()
        self._platform_add_entities: dict[str, AddEntitiesCallback] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    def async_register_platform(self, platform: str, cb: AddEntitiesCallback) -> None:
        """Register an add_entities callback for a platform."""
        self._platform_add_entities[platform] = cb

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            if not self._initialized:
                await self._load_data()
                self._initialized = True

            await self._check_task_deadlines()
            await self._check_automatic_resets()

            return {
                "children": {child_id: child.to_dict() for child_id, child in self.children.items()},
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "rewards": {reward_id: reward.to_dict() for reward_id, reward in self.rewards.items()},
            }
        except Exception as err:
            raise UpdateFailed(f"Error updating kids tasks data: {err}") from err

    async def async_request_refresh(self) -> None:
        """Request a data refresh."""
        try:
            refresh_result = self.async_refresh()
            if refresh_result is not None:
                await refresh_result
        except Exception as e:
            _LOGGER.warning("Failed to refresh coordinator: %s", e)
