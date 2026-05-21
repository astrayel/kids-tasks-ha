"""Tests for config flow — schema, user step, options flow routing."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.kids_tasks.config_flow import (
    ConfigFlow,
    KidsTasksOptionsFlow,
    STEP_USER_DATA_SCHEMA,
)
from custom_components.kids_tasks.const import DOMAIN


# ---------------------------------------------------------------------------
# STEP_USER_DATA_SCHEMA
# ---------------------------------------------------------------------------

class TestStepUserSchema:
    def test_applies_defaults_for_optional_fields(self):
        result = STEP_USER_DATA_SCHEMA({"name": "My Family"})
        assert result["name"] == "My Family"
        assert result["validation_required"] is True
        assert result["notifications_enabled"] is True

    def test_accepts_all_fields_explicitly(self):
        data = {"name": "Test", "validation_required": False, "notifications_enabled": False}
        result = STEP_USER_DATA_SCHEMA(data)
        assert result["validation_required"] is False
        assert result["notifications_enabled"] is False

    def test_empty_input_uses_default_name(self):
        result = STEP_USER_DATA_SCHEMA({})
        assert result["name"] == "Kids Tasks"


# ---------------------------------------------------------------------------
# ConfigFlow
# ---------------------------------------------------------------------------

class TestConfigFlow:
    def _make(self):
        """Build a ConfigFlow instance with HA framework methods mocked out."""
        flow = ConfigFlow.__new__(ConfigFlow)
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        return flow

    async def test_shows_form_when_no_input(self):
        flow = self._make()
        result = await flow.async_step_user(None)
        flow.async_show_form.assert_called_once()
        assert result["type"] == "form"

    async def test_creates_entry_with_valid_input(self):
        flow = self._make()
        user_input = {"name": "Kids", "validation_required": True, "notifications_enabled": True}
        await flow.async_step_user(user_input)
        flow.async_set_unique_id.assert_awaited_once_with(f"{DOMAIN}_Kids")
        flow.async_create_entry.assert_called_once_with(title="Kids", data=user_input)

    async def test_checks_for_duplicate_id(self):
        flow = self._make()
        flow._abort_if_unique_id_configured.side_effect = Exception("abort")
        with pytest.raises(Exception, match="abort"):
            await flow.async_step_user(
                {"name": "Kids", "validation_required": True, "notifications_enabled": True}
            )

    def test_schema_version_is_1(self):
        assert ConfigFlow.VERSION == 1

    def test_returns_options_flow(self):
        config_entry = MagicMock()
        options_flow = ConfigFlow.async_get_options_flow(config_entry)
        assert isinstance(options_flow, KidsTasksOptionsFlow)


# ---------------------------------------------------------------------------
# KidsTasksOptionsFlow
# ---------------------------------------------------------------------------

class TestOptionsFlow:
    def _make(self, children=None):
        """Build an OptionsFlow with coordinator mock and HA methods mocked."""
        config_entry = MagicMock()
        config_entry.runtime_data.coordinator.children = children or {}
        flow = KidsTasksOptionsFlow(config_entry)
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        return flow

    async def test_init_delegates_to_main_menu(self):
        flow = self._make()
        flow.async_step_main_menu = AsyncMock(return_value={"type": "form"})
        await flow.async_step_init()
        flow.async_step_main_menu.assert_awaited_once()

    async def test_main_menu_shows_form_without_input(self):
        flow = self._make()
        await flow.async_step_main_menu(None)
        flow.async_show_form.assert_called_once()

    async def test_main_menu_routes_to_add_task(self):
        flow = self._make()
        flow.async_step_add_task = AsyncMock(return_value={"type": "form"})
        await flow.async_step_main_menu({"action": "add_task"})
        flow.async_step_add_task.assert_awaited_once()

    async def test_main_menu_routes_to_add_child(self):
        flow = self._make()
        flow.async_step_add_child = AsyncMock(return_value={"type": "form"})
        await flow.async_step_main_menu({"action": "add_child"})
        flow.async_step_add_child.assert_awaited_once()

    async def test_main_menu_routes_to_add_reward(self):
        flow = self._make()
        flow.async_step_add_reward = AsyncMock(return_value={"type": "form"})
        await flow.async_step_main_menu({"action": "add_reward"})
        flow.async_step_add_reward.assert_awaited_once()

    async def test_add_task_shows_form_without_input(self):
        flow = self._make()
        await flow.async_step_add_task(None)
        flow.async_show_form.assert_called_once()

    async def test_add_child_shows_form_without_input(self):
        flow = self._make()
        await flow.async_step_add_child(None)
        flow.async_show_form.assert_called_once()

    async def test_add_reward_shows_form_without_input(self):
        flow = self._make()
        await flow.async_step_add_reward(None)
        flow.async_show_form.assert_called_once()

    async def test_add_child_creates_entry_with_valid_input(self):
        flow = self._make()
        flow.config_entry.runtime_data.coordinator.async_add_child = AsyncMock()
        user_input = {"name": "Emma", "initial_points": 0}
        await flow.async_step_add_child(user_input)
        flow.config_entry.runtime_data.coordinator.async_add_child.assert_awaited_once()

    async def test_add_reward_creates_entry_with_valid_input(self):
        flow = self._make()
        flow.config_entry.runtime_data.coordinator.async_add_reward = AsyncMock()
        user_input = {"name": "Movie Night", "cost": 50, "category": "fun"}
        await flow.async_step_add_reward(user_input)
        flow.config_entry.runtime_data.coordinator.async_add_reward.assert_awaited_once()
