"""Unit tests for models — Child, Task, Reward, PointsHistoryEntry."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from custom_components.kids_tasks.models import Child, Task, Reward, TaskChildStatus, PointsHistoryEntry
from custom_components.kids_tasks.const import (
    TASK_STATUS_TODO,
    FREQUENCY_DAILY,
    FREQUENCY_NONE,
)


# ---------------------------------------------------------------------------
# Child
# ---------------------------------------------------------------------------

class TestChildLevel:
    def test_initial_level_is_1(self):
        child = Child(id="c1", name="Alice")
        assert child.level == 1

    def test_level_stays_1_at_99_points(self):
        child = Child(id="c1", name="Alice")
        child.add_points(99)
        assert child.level == 1

    def test_level_up_at_exactly_100_points(self):
        child = Child(id="c1", name="Alice")
        leveled_up = child.add_points(100)
        assert child.level == 2
        assert leveled_up is True

    def test_level_up_at_200_points(self):
        child = Child(id="c1", name="Alice")
        child.add_points(200)
        assert child.level == 3

    def test_no_level_up_returns_false(self):
        child = Child(id="c1", name="Alice")
        leveled_up = child.add_points(50)
        assert leveled_up is False

    def test_level_boundary_99_to_100(self):
        child = Child(id="c1", name="Alice", points=99)
        child.level = 1
        leveled_up = child.add_points(1)
        assert child.points == 100
        assert child.level == 2
        assert leveled_up is True

    def test_set_points_recalculates_level(self):
        child = Child(id="c1", name="Alice", points=50, level=1)
        child.set_points(250)
        assert child.level == 3

    def test_set_points_cannot_go_negative(self):
        child = Child(id="c1", name="Alice", points=10)
        child.set_points(-50)
        assert child.points == 0

    def test_set_level_adjusts_points(self):
        child = Child(id="c1", name="Alice")
        child.set_level(3)
        assert child.level == 3
        assert child.points == 200  # (3-1) * 100

    def test_points_to_next_level(self):
        child = Child(id="c1", name="Alice", points=30, level=1)
        assert child.points_to_next_level == 70  # 1*100 - 30


class TestChildPointsHistory:
    def test_history_entry_added_on_add_points(self):
        child = Child(id="c1", name="Alice")
        child.add_points(10, description="test")
        assert len(child.points_history) == 1
        assert child.points_history[0].points_delta == 10

    def test_history_capped_at_20_entries(self):
        child = Child(id="c1", name="Alice")
        for i in range(25):
            child.add_points(1)
        assert len(child.points_history) == 20

    def test_history_most_recent_first(self):
        child = Child(id="c1", name="Alice")
        child.add_points(5, description="first")
        child.add_points(10, description="second")
        assert child.points_history[0].points_delta == 10
        assert child.points_history[1].points_delta == 5

    def test_negative_delta_recorded(self):
        child = Child(id="c1", name="Alice", points=50)
        child.add_points(-20)
        assert child.points_history[0].points_delta == -20


class TestChildCoins:
    def test_add_coins(self):
        child = Child(id="c1", name="Alice")
        child.add_coins(5)
        assert child.coins == 5

    def test_remove_coins_success(self):
        child = Child(id="c1", name="Alice", coins=10)
        result = child.remove_coins(3)
        assert result is True
        assert child.coins == 7

    def test_remove_coins_insufficient_returns_false(self):
        child = Child(id="c1", name="Alice", coins=2)
        result = child.remove_coins(5)
        assert result is False
        assert child.coins == 2


class TestChildSerialization:
    def test_to_dict_roundtrip(self):
        child = Child(id="c1", name="Alice", points=150, coins=3, level=2)
        child.add_points(10, description="bonus")
        restored = Child.from_dict(child.to_dict())
        assert restored.id == child.id
        assert restored.name == child.name
        assert restored.points == child.points
        assert restored.coins == child.coins
        assert restored.level == child.level
        assert len(restored.points_history) == len(child.points_history)


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TestTaskCompletion:
    def _task(self, child_id="c1", validation=True):
        task = Task(id="t1", name="Clean Room", points=10, validation_required=validation)
        task.assigned_child_ids = [child_id]
        return task

    def test_complete_with_validation_sets_pending(self):
        task = self._task()
        status = task.complete_for_child("c1", validation_required=True)
        assert status == "pending_validation"

    def test_complete_without_validation_sets_validated(self):
        task = self._task()
        status = task.complete_for_child("c1", validation_required=False)
        assert status == "validated"

    def test_validate_for_child_updates_status(self):
        task = self._task()
        task.complete_for_child("c1", validation_required=True)
        result = task.validate_for_child("c1")
        assert result is True
        assert task.get_status_for_child("c1") == "validated"

    def test_validate_returns_false_if_not_pending(self):
        task = self._task()
        result = task.validate_for_child("c1")
        assert result is False

    def test_get_status_for_unassigned_child(self):
        task = self._task()
        assert task.get_status_for_child("unknown") == TASK_STATUS_TODO

    def test_reset_clears_all_child_statuses(self):
        task = self._task()
        task.complete_for_child("c1", validation_required=False)
        task.reset()
        assert task.get_status_for_child("c1") == TASK_STATUS_TODO
        assert task.deadline_passed is False

    def test_global_status_pending_when_any_child_pending(self):
        task = Task(id="t1", name="Task", points=5)
        task.assigned_child_ids = ["c1", "c2"]
        task.complete_for_child("c1", validation_required=True)
        task.complete_for_child("c2", validation_required=False)
        assert task.status == "pending_validation"

    def test_global_status_validated_when_all_children_validated(self):
        task = Task(id="t1", name="Task", points=5)
        task.assigned_child_ids = ["c1", "c2"]
        task.complete_for_child("c1", validation_required=False)
        task.complete_for_child("c2", validation_required=False)
        assert task.status == "validated"

    def test_bonus_task_can_be_recompleted(self):
        task = Task(id="t1", name="Bonus", points=5, frequency=FREQUENCY_NONE)
        task.assigned_child_ids = ["c1"]
        task.complete_for_child("c1", validation_required=False)
        assert task.get_status_for_child("c1") == "validated"
        # Bonus tasks reset on completion to allow re-completion
        task.complete_for_child("c1", validation_required=True)
        assert task.get_status_for_child("c1") == "pending_validation"


class TestTaskDeadline:
    def test_deadline_triggers_when_passed(self, fixed_time):
        """Deadline at 09:00, fixed time is 10:00 → should trigger."""
        task = Task(id="t1", name="Task", deadline_time="09:00")
        task.assigned_child_ids = ["c1"]
        result = task.check_deadline()
        assert result is True
        assert task.deadline_passed is True

    def test_deadline_not_triggered_if_future(self, fixed_time):
        """Deadline at 11:00, fixed time is 10:00 → should not trigger."""
        task = Task(id="t1", name="Task", deadline_time="11:00")
        task.assigned_child_ids = ["c1"]
        result = task.check_deadline()
        assert result is False

    def test_deadline_only_triggers_once(self, fixed_time):
        """Second check on already-passed deadline → False."""
        task = Task(id="t1", name="Task", deadline_time="09:00")
        task.check_deadline()
        result = task.check_deadline()
        assert result is False

    def test_deadline_skipped_for_non_todo_status(self):
        task = Task(id="t1", name="Task", deadline_time="09:00", status="validated")
        result = task.check_deadline()
        assert result is False

    def test_invalid_deadline_format_does_not_raise(self):
        task = Task(id="t1", name="Task", deadline_time="bad")
        result = task.check_deadline()
        assert result is False


class TestTaskSuspension:
    def test_suspend_makes_task_unavailable(self):
        task = Task(id="t1", name="Task")
        task.suspend()
        assert task.is_available() is False

    def test_resume_makes_task_available(self):
        task = Task(id="t1", name="Task")
        task.suspend()
        task.resume()
        assert task.is_available() is True

    def test_suspension_auto_expires(self, fixed_time):
        from datetime import timedelta
        past = fixed_time.replace(tzinfo=None) - timedelta(hours=1)
        task = Task(id="t1", name="Task", suspended=True, suspended_until=past)
        assert task.is_available() is True  # auto-resumed
        assert task.suspended is False


class TestTaskSerialization:
    def test_to_dict_roundtrip(self):
        task = Task(id="t1", name="Clean Room", points=10, frequency=FREQUENCY_DAILY)
        task.assigned_child_ids = ["c1"]
        task.complete_for_child("c1", validation_required=False)
        restored = Task.from_dict(task.to_dict())
        assert restored.id == task.id
        assert restored.name == task.name
        assert restored.get_status_for_child("c1") == "validated"


# ---------------------------------------------------------------------------
# Reward
# ---------------------------------------------------------------------------

class TestReward:
    def test_can_claim_with_enough_points(self):
        reward = Reward(id="r1", name="Movie", cost=50)
        assert reward.can_claim(child_points=50) is True

    def test_cannot_claim_with_insufficient_points(self):
        reward = Reward(id="r1", name="Movie", cost=50)
        assert reward.can_claim(child_points=49) is False

    def test_cannot_claim_inactive_reward(self):
        reward = Reward(id="r1", name="Movie", cost=0, active=False)
        assert reward.can_claim(child_points=100) is False

    def test_limited_quantity_depletes_on_claim(self):
        reward = Reward(id="r1", name="Movie", cost=0, limited_quantity=2, remaining_quantity=2)
        reward.claim()
        assert reward.remaining_quantity == 1

    def test_claim_fails_when_quantity_exhausted(self):
        reward = Reward(id="r1", name="Movie", cost=0, limited_quantity=1, remaining_quantity=0)
        assert reward.can_claim(child_points=100) is False

    def test_unlimited_reward_always_claimable(self):
        reward = Reward(id="r1", name="Movie", cost=0)
        for _ in range(10):
            assert reward.claim() is True

    def test_can_claim_checks_coin_cost(self):
        reward = Reward(id="r1", name="Movie", cost=0, coin_cost=5)
        assert reward.can_claim(child_points=100, child_coins=4) is False
        assert reward.can_claim(child_points=100, child_coins=5) is True

    def test_to_dict_roundtrip(self):
        reward = Reward(id="r1", name="Movie", cost=50, category="fun")
        restored = Reward.from_dict(reward.to_dict())
        assert restored.id == reward.id
        assert restored.cost == reward.cost
