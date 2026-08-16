"""Tests for the task switch platform."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.kids_tasks.models import Child, Task, TaskChildStatus
from custom_components.kids_tasks.switch import TaskSwitch


def _coordinator_with(task_status: str = "todo"):
    """Coordinator mock exposing one task shared by Léo and Emma."""
    coord = MagicMock()
    coord.data = {
        "tasks": {
            "t1": {
                "name": "Ranger la chambre",
                "status": task_status,
                "points": 10,
                "category": "bedroom",
                "validation_required": True,
                "child_statuses": {
                    "leo": {"status": task_status},
                    "emma": {"status": "todo"},
                },
            }
        },
        "children": {
            "leo": {"name": "Léo"},
            "emma": {"name": "Emma"},
        },
    }
    coord.async_complete_task = AsyncMock()
    coord.async_save_data = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    return coord


def _switch(coord, child_id="leo"):
    with patch(
        "homeassistant.helpers.update_coordinator.CoordinatorEntity.__init__",
        return_value=None,
    ):
        sw = TaskSwitch(coord, "t1", child_id)
        sw.coordinator = coord
        return sw


class TestIdentity:
    def test_unique_id_pairs_task_and_child(self):
        assert _switch(_coordinator_with())._attr_unique_id == "kidtasks_switch_t1_leo"

    def test_name_shows_task_and_child(self):
        name = _switch(_coordinator_with()).name
        assert "Ranger la chambre" in name and "Léo" in name

    def test_device_is_the_child(self):
        info = _switch(_coordinator_with()).device_info
        assert ("kids_tasks", "leo") in info["identifiers"]


class TestState:
    @pytest.mark.parametrize("status", ["validated", "completed", "pending_validation"])
    def test_on_once_submitted(self, status):
        assert _switch(_coordinator_with(status)).is_on is True

    def test_off_when_todo(self):
        assert _switch(_coordinator_with("todo")).is_on is False

    def test_off_when_not_applicable(self):
        """A day the task is not scheduled is not a day it was done."""
        assert _switch(_coordinator_with("not_applicable")).is_on is False

    def test_reads_this_childs_row_not_the_global_status(self):
        """Emma has not done it, even though the task reads as submitted."""
        coord = _coordinator_with("pending_validation")
        assert _switch(coord, "emma").is_on is False

    def test_attributes_expose_ids(self):
        attrs = _switch(_coordinator_with()).extra_state_attributes
        assert attrs["task_id"] == "t1"
        assert attrs["child_id"] == "leo"


class TestActions:
    async def test_turn_on_completes_for_this_child(self):
        coord = _coordinator_with()
        await _switch(coord).async_turn_on()
        coord.async_complete_task.assert_awaited_once_with(
            "t1", "leo", validation_required=True
        )

    async def test_turn_off_only_resets_this_child(self):
        coord = _coordinator_with()
        task = Task(id="t1", name="Ranger la chambre", points=10)
        task.assigned_child_ids = ["leo", "emma"]
        task.complete_for_child("leo")
        task.complete_for_child("emma")
        coord.tasks = {"t1": task}

        await _switch(coord, "leo").async_turn_off()

        assert task.get_status_for_child("leo") == "todo"
        assert task.get_status_for_child("emma") == "pending_validation"

    async def test_turn_off_saves(self):
        coord = _coordinator_with()
        task = Task(id="t1", name="T", points=10)
        task.assigned_child_ids = ["leo"]
        task.complete_for_child("leo")
        coord.tasks = {"t1": task}

        await _switch(coord).async_turn_off()
        coord.async_save_data.assert_awaited_once()

    async def test_turn_off_is_a_noop_when_child_has_no_row(self):
        coord = _coordinator_with()
        task = Task(id="t1", name="T", points=10)
        task.assigned_child_ids = ["leo"]
        coord.tasks = {"t1": task}

        await _switch(coord).async_turn_off()
        coord.async_save_data.assert_not_awaited()

    async def test_turn_off_on_unknown_task_does_not_raise(self):
        coord = _coordinator_with()
        coord.tasks = {}
        await _switch(coord).async_turn_off()
        coord.async_save_data.assert_not_awaited()
