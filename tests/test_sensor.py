"""Tests for sensor entities — native values, attributes, availability."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

# Matches conftest FIXED_NOW = datetime(2024, 6, 15, 10, 0, 0, tzinfo=utc)
FIXED_TODAY_STR = "2024-06-15"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_coordinator(children=None, tasks=None, rewards=None):
    coord = MagicMock()
    coord.data = {
        "children": children or {},
        "tasks": tasks or {},
        "rewards": rewards or {},
    }
    # get_safe_child_name reads coordinator.children (objects with .name attribute)
    coord.children = {}
    for child_id, cd in (children or {}).items():
        m = MagicMock()
        m.name = cd.get("name", "Child")
        coord.children[child_id] = m
    return coord


@pytest.fixture(autouse=True)
def _bypass_entity_init():
    """Replace CoordinatorEntity.__init__ with a minimal version that only sets self.coordinator."""
    def _minimal(self, coordinator, context=None):
        self.coordinator = coordinator

    with patch(
        "homeassistant.helpers.update_coordinator.CoordinatorEntity.__init__",
        new=_minimal,
    ):
        yield


# ---------------------------------------------------------------------------
# get_safe_child_name
# ---------------------------------------------------------------------------

class TestGetSafeChildName:
    def test_basic_name_lowercased(self):
        from custom_components.kids_tasks.sensor import get_safe_child_name
        coord = _make_coordinator({"c1": {"name": "Alice"}})
        assert get_safe_child_name(coord, "c1") == "alice"

    def test_spaces_become_underscores(self):
        from custom_components.kids_tasks.sensor import get_safe_child_name
        coord = _make_coordinator({"c1": {"name": "Jean Pierre"}})
        assert get_safe_child_name(coord, "c1") == "jean_pierre"

    def test_accented_characters_normalized(self):
        from custom_components.kids_tasks.sensor import get_safe_child_name
        coord = _make_coordinator({"c1": {"name": "Élodie"}})
        assert get_safe_child_name(coord, "c1") == "elodie"

    def test_unknown_child_uses_id_fallback(self):
        from custom_components.kids_tasks.sensor import get_safe_child_name
        coord = _make_coordinator()
        result = get_safe_child_name(coord, "xyz123abc")
        assert result.startswith("child_")


# ---------------------------------------------------------------------------
# ChildPointsSensor
# ---------------------------------------------------------------------------

class TestChildPointsSensor:
    def _sensor(self, points=50, level=1):
        from custom_components.kids_tasks.sensor import ChildPointsSensor
        coord = _make_coordinator({"c1": {"name": "Alice", "points": points, "level": level}})
        return ChildPointsSensor(coord, "c1")

    def test_native_value_returns_points(self):
        assert self._sensor(points=42).native_value == 42

    def test_name_includes_child_name(self):
        assert "Alice" in self._sensor().name

    def test_unique_id_is_deterministic(self):
        assert "alice" in self._sensor()._attr_unique_id

    def test_extra_attrs_contains_level(self):
        assert self._sensor(points=50, level=2).extra_state_attributes["level"] == 2

    def test_extra_attrs_points_to_next_level(self):
        attrs = self._sensor(points=30, level=1).extra_state_attributes
        assert attrs["points_to_next_level"] == 70  # 1*100 - 30

    def test_extra_attrs_child_id(self):
        assert self._sensor().extra_state_attributes["child_id"] == "c1"


# ---------------------------------------------------------------------------
# ChildLevelSensor
# ---------------------------------------------------------------------------

class TestChildLevelSensor:
    def _sensor(self, level=1):
        from custom_components.kids_tasks.sensor import ChildLevelSensor
        coord = _make_coordinator({"c1": {"name": "Bob", "level": level}})
        return ChildLevelSensor(coord, "c1")

    def test_native_value_is_level(self):
        assert self._sensor(level=3).native_value == 3

    def test_defaults_to_1_when_no_level_key(self):
        from custom_components.kids_tasks.sensor import ChildLevelSensor
        coord = _make_coordinator({"c1": {"name": "Bob"}})
        assert ChildLevelSensor(coord, "c1").native_value == 1


# ---------------------------------------------------------------------------
# ChildTasksCompletedTodaySensor
# ---------------------------------------------------------------------------

class TestChildTasksCompletedTodaySensor:
    def _sensor(self, tasks=None):
        from custom_components.kids_tasks.sensor import ChildTasksCompletedTodaySensor
        coord = _make_coordinator(
            children={"c1": {"name": "Alice"}},
            tasks=tasks or {},
        )
        return ChildTasksCompletedTodaySensor(coord, "c1")

    def test_counts_validated_today(self):
        tasks = {"t1": {
            "assigned_child_ids": ["c1"],
            "child_statuses": {"c1": {"status": "validated", "validated_at": f"{FIXED_TODAY_STR}T10:00:00"}},
        }}
        assert self._sensor(tasks).native_value == 1

    def test_multiple_tasks_today(self):
        tasks = {
            "t1": {
                "assigned_child_ids": ["c1"],
                "child_statuses": {"c1": {"status": "validated", "validated_at": f"{FIXED_TODAY_STR}T08:00:00"}},
            },
            "t2": {
                "assigned_child_ids": ["c1"],
                "child_statuses": {"c1": {"status": "validated", "validated_at": f"{FIXED_TODAY_STR}T09:00:00"}},
            },
        }
        assert self._sensor(tasks).native_value == 2

    def test_ignores_validation_from_different_day(self):
        tasks = {"t1": {
            "assigned_child_ids": ["c1"],
            "child_statuses": {"c1": {"status": "validated", "validated_at": "2024-01-01T10:00:00"}},
        }}
        assert self._sensor(tasks).native_value == 0

    def test_ignores_task_assigned_to_other_child(self):
        tasks = {"t1": {
            "assigned_child_ids": ["c2"],
            "child_statuses": {"c2": {"status": "validated", "validated_at": f"{FIXED_TODAY_STR}T10:00:00"}},
        }}
        assert self._sensor(tasks).native_value == 0

    def test_ignores_pending_validation(self):
        tasks = {"t1": {
            "assigned_child_ids": ["c1"],
            "child_statuses": {"c1": {"status": "pending_validation", "validated_at": None}},
        }}
        assert self._sensor(tasks).native_value == 0


# ---------------------------------------------------------------------------
# PendingValidationsSensor
# ---------------------------------------------------------------------------

class TestPendingValidationsSensor:
    def _sensor(self, tasks=None):
        from custom_components.kids_tasks.sensor import PendingValidationsSensor
        return PendingValidationsSensor(_make_coordinator(tasks=tasks or {}))

    def test_counts_pending_validations(self):
        tasks = {
            "t1": {"status": "pending_validation"},
            "t2": {"status": "pending_validation"},
            "t3": {"status": "validated"},
        }
        assert self._sensor(tasks).native_value == 2

    def test_returns_zero_when_none_pending(self):
        assert self._sensor({"t1": {"status": "validated"}}).native_value == 0

    def test_device_info_is_system_device(self):
        from custom_components.kids_tasks.sensor import _SYSTEM_DEVICE_INFO
        assert self._sensor().device_info is _SYSTEM_DEVICE_INFO

    def test_extra_attrs_include_categories(self):
        attrs = self._sensor().extra_state_attributes
        assert "available_categories" in attrs
        assert "available_frequencies" in attrs


# ---------------------------------------------------------------------------
# TotalTasksCompletedTodaySensor
# ---------------------------------------------------------------------------

class TestTotalTasksCompletedTodaySensor:
    def _sensor(self, tasks=None):
        from custom_components.kids_tasks.sensor import TotalTasksCompletedTodaySensor
        return TotalTasksCompletedTodaySensor(_make_coordinator(tasks=tasks or {}))

    def test_counts_all_child_validations_today(self):
        tasks = {"t1": {"child_statuses": {
            "c1": {"status": "validated", "validated_at": f"{FIXED_TODAY_STR}T09:00:00"},
            "c2": {"status": "validated", "validated_at": f"{FIXED_TODAY_STR}T11:00:00"},
        }}}
        assert self._sensor(tasks).native_value == 2

    def test_ignores_old_validations(self):
        tasks = {"t1": {"child_statuses": {
            "c1": {"status": "validated", "validated_at": "2024-01-01T09:00:00"},
        }}}
        assert self._sensor(tasks).native_value == 0

    def test_zero_when_no_tasks(self):
        assert self._sensor().native_value == 0


# ---------------------------------------------------------------------------
# ActiveTasksSensor
# ---------------------------------------------------------------------------

class TestActiveTasksSensor:
    def _sensor(self, tasks=None):
        from custom_components.kids_tasks.sensor import ActiveTasksSensor
        return ActiveTasksSensor(_make_coordinator(tasks=tasks or {}))

    def test_counts_only_active_tasks(self):
        tasks = {
            "t1": {"active": True},
            "t2": {"active": True},
            "t3": {"active": False},
        }
        assert self._sensor(tasks).native_value == 2

    def test_task_without_active_key_defaults_to_active(self):
        assert self._sensor({"t1": {}}).native_value == 1

    def test_zero_when_no_tasks(self):
        assert self._sensor().native_value == 0


# ---------------------------------------------------------------------------
# TaskSensor
# ---------------------------------------------------------------------------

class TestTaskSensor:
    def _sensor(self, task_data=None):
        from custom_components.kids_tasks.sensor import TaskSensor
        coord = _make_coordinator(tasks={"t1": task_data or {"name": "Clean Room", "status": "todo"}})
        return TaskSensor(coord, "t1")

    def test_native_value_is_task_status(self):
        assert self._sensor({"name": "Task", "status": "validated"}).native_value == "validated"

    def test_name_is_task_name(self):
        assert self._sensor({"name": "Brush Teeth", "status": "todo"}).name == "Brush Teeth"

    def test_available_when_task_in_data(self):
        assert self._sensor().available is True

    def test_unavailable_when_task_absent(self):
        from custom_components.kids_tasks.sensor import TaskSensor
        sensor = TaskSensor(_make_coordinator(tasks={}), "nonexistent")
        assert sensor.available is False

    def test_extra_attrs_contains_task_id(self):
        assert self._sensor().extra_state_attributes["task_id"] == "t1"

    def test_device_info_is_system_device(self):
        from custom_components.kids_tasks.sensor import _SYSTEM_DEVICE_INFO
        assert self._sensor().device_info is _SYSTEM_DEVICE_INFO


# ---------------------------------------------------------------------------
# RewardSensor
# ---------------------------------------------------------------------------

class TestRewardSensor:
    def _sensor(self, reward_data=None):
        from custom_components.kids_tasks.sensor import RewardSensor
        coord = _make_coordinator(rewards={"r1": reward_data or {"name": "Movie Night", "cost": 50}})
        return RewardSensor(coord, "r1")

    def test_native_value_is_cost(self):
        assert self._sensor({"name": "Trip", "cost": 100}).native_value == 100

    def test_name_is_reward_name(self):
        assert self._sensor({"name": "Ice Cream", "cost": 20}).name == "Ice Cream"

    def test_available_when_reward_in_data(self):
        assert self._sensor().available is True

    def test_unavailable_when_reward_absent(self):
        from custom_components.kids_tasks.sensor import RewardSensor
        sensor = RewardSensor(_make_coordinator(rewards={}), "nonexistent")
        assert sensor.available is False

    def test_unlimited_reward_is_available(self):
        attrs = self._sensor({"name": "R", "cost": 0, "remaining_quantity": None}).extra_state_attributes
        assert attrs["is_available"] is True

    def test_exhausted_reward_is_not_available(self):
        attrs = self._sensor({"name": "R", "cost": 0, "remaining_quantity": 0}).extra_state_attributes
        assert attrs["is_available"] is False

    def test_device_info_is_system_device(self):
        from custom_components.kids_tasks.sensor import _SYSTEM_DEVICE_INFO
        assert self._sensor().device_info is _SYSTEM_DEVICE_INFO
