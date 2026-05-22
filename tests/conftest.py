"""Common fixtures for Kids Tasks tests."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Fixed point in time used by all tests — Saturday 2024-06-15 10:00 UTC
FIXED_NOW = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
FIXED_DATE = FIXED_NOW.date()


@pytest.fixture(autouse=True)
def fixed_time():
    """Patch dt_util.now() to a fixed value for deterministic tests."""
    with (
        patch("custom_components.kids_tasks.models.dt_util.now", return_value=FIXED_NOW),
        patch("custom_components.kids_tasks.coordinator.dt_util.now", return_value=FIXED_NOW),
        patch("custom_components.kids_tasks.sensor.dt_util.now", return_value=FIXED_NOW),
    ):
        yield FIXED_NOW


@pytest.fixture
def mock_hass():
    """Minimal HomeAssistant mock."""
    hass = MagicMock()
    hass.bus.async_fire = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.services.async_services = MagicMock(return_value={})
    hass.config.config_dir = "/tmp"
    hass.config.time_zone = "UTC"
    return hass


@pytest.fixture
def mock_store():
    """In-memory Store mock."""
    store = AsyncMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    store.async_remove = AsyncMock()
    return store


@pytest.fixture
def coordinator(mock_hass, mock_store):
    """KidsTasksDataUpdateCoordinator with HA machinery bypassed."""
    from custom_components.kids_tasks.coordinator import KidsTasksDataUpdateCoordinator

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
        return_value=None,
    ):
        coord = KidsTasksDataUpdateCoordinator.__new__(KidsTasksDataUpdateCoordinator)
        coord.hass = mock_hass
        coord.store = mock_store
        coord.config_entry_id = "test_entry_id"
        coord.children = {}
        coord.tasks = {}
        coord.rewards = {}
        coord.last_daily_reset = None
        coord.last_weekly_reset = None
        coord.last_monthly_reset = None
        coord._initialized = False
        coord._reset_lock = asyncio.Lock()
        coord._platform_add_entities = {}
        coord._last_statistics_hour = None
        coord.logger = logging.getLogger(__name__)
        coord.data = {}
        coord.last_update_success = True
        coord.config_entry = MagicMock()
        coord.config_entry.data = {"notifications_enabled": False}
        return coord
