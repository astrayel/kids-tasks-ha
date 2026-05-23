"""Tests for coordinator business logic — resets, penalties, CRUD."""
from __future__ import annotations

import asyncio
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.kids_tasks.models import Child, Task, Reward
from custom_components.kids_tasks.const import FREQUENCY_DAILY, FREQUENCY_WEEKLY, FREQUENCY_MONTHLY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_child(child_id="c1", name="Alice", points=0) -> Child:
    return Child(id=child_id, name=name, points=points)


def make_task(task_id="t1", name="Clean Room", frequency=FREQUENCY_DAILY,
              points=10, penalty_points=0, child_ids=None) -> Task:
    task = Task(id=task_id, name=name, frequency=frequency, points=points,
                penalty_points=penalty_points)
    task.assigned_child_ids = child_ids or ["c1"]
    return task


def make_reward(reward_id="r1", name="Movie", cost=50) -> Reward:
    return Reward(id=reward_id, name=name, cost=cost)


# ---------------------------------------------------------------------------
# _initialized flag (1.2 regression)
# ---------------------------------------------------------------------------

class TestInitializedFlag:
    async def test_load_data_called_only_on_first_update(self, coordinator, mock_store):
        mock_store.async_load.return_value = {}
        await coordinator._async_update_data()
        await coordinator._async_update_data()
        assert mock_store.async_load.call_count == 1

    async def test_second_refresh_does_not_reload_storage(self, coordinator, mock_store):
        mock_store.async_load.return_value = {}
        coordinator._initialized = True  # simulate already initialized
        await coordinator._async_update_data()
        mock_store.async_load.assert_not_called()


# ---------------------------------------------------------------------------
# Daily reset
# ---------------------------------------------------------------------------

class TestDailyReset:
    async def test_triggers_when_no_previous_reset(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_DAILY)
        task.complete_for_child("c1", validation_required=False)
        coordinator.tasks["t1"] = task
        coordinator.last_daily_reset = None

        await coordinator._check_automatic_resets()

        assert coordinator.last_daily_reset == fixed_time.date()
        assert task.get_status_for_child("c1") == "todo"

    async def test_skips_if_already_reset_today(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_DAILY)
        coordinator.tasks["t1"] = task
        coordinator.last_daily_reset = fixed_time.date()

        await coordinator._check_automatic_resets()

        # save should not be called (no reset happened)
        coordinator.store.async_save.assert_not_called()

    async def test_does_not_trigger_twice_same_day(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_DAILY)
        coordinator.tasks["t1"] = task
        coordinator.last_daily_reset = None

        await coordinator._check_automatic_resets()
        initial_save_count = coordinator.store.async_save.call_count

        await coordinator._check_automatic_resets()
        assert coordinator.store.async_save.call_count == initial_save_count

    async def test_triggers_on_new_day(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_DAILY)
        coordinator.tasks["t1"] = task
        coordinator.last_daily_reset = fixed_time.date() - timedelta(days=1)

        await coordinator._check_automatic_resets()

        assert coordinator.last_daily_reset == fixed_time.date()

    async def test_penalty_applied_on_reset_for_uncompleted_task(self, coordinator, fixed_time):
        child = make_child(points=100)
        task = make_task(frequency=FREQUENCY_DAILY, penalty_points=10)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task
        coordinator.last_daily_reset = None

        await coordinator._check_automatic_resets()

        assert child.points == 90

    async def test_penalty_not_applied_if_already_validated(self, coordinator, fixed_time):
        child = make_child(points=100)
        task = make_task(frequency=FREQUENCY_DAILY, penalty_points=10)
        task.complete_for_child("c1", validation_required=False)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task
        coordinator.last_daily_reset = None

        await coordinator._check_automatic_resets()

        assert child.points == 100  # no penalty

    async def test_penalty_not_applied_twice(self, coordinator, fixed_time):
        """Penalty from deadline should not be doubled by reset."""
        child = make_child(points=100)
        task = make_task(frequency=FREQUENCY_DAILY, penalty_points=10)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task
        # Mark penalty already applied (e.g. by deadline)
        from custom_components.kids_tasks.models import TaskChildStatus
        task.child_statuses["c1"] = TaskChildStatus(child_id="c1", penalty_applied=True)
        coordinator.last_daily_reset = None

        await coordinator._check_automatic_resets()

        assert child.points == 100  # no double penalty


# ---------------------------------------------------------------------------
# Weekly / Monthly resets
# ---------------------------------------------------------------------------

class TestWeeklyReset:
    async def test_triggers_on_new_week(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_WEEKLY)
        coordinator.tasks["t1"] = task
        # Last reset was in previous week
        previous_week = fixed_time.date() - timedelta(days=7)
        coordinator.last_weekly_reset = previous_week - timedelta(days=previous_week.weekday())

        await coordinator._check_automatic_resets()

        week_start = fixed_time.date() - timedelta(days=fixed_time.weekday())
        assert coordinator.last_weekly_reset == week_start

    async def test_skips_same_week(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_WEEKLY)
        coordinator.tasks["t1"] = task
        week_start = fixed_time.date() - timedelta(days=fixed_time.weekday())
        coordinator.last_weekly_reset = week_start

        await coordinator._check_automatic_resets()

        coordinator.store.async_save.assert_not_called()


class TestMonthlyReset:
    async def test_triggers_on_new_month(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_MONTHLY)
        coordinator.tasks["t1"] = task
        coordinator.last_monthly_reset = date(fixed_time.year, fixed_time.month - 1, 1)

        await coordinator._check_automatic_resets()

        assert coordinator.last_monthly_reset == date(fixed_time.year, fixed_time.month, 1)

    async def test_skips_same_month(self, coordinator, fixed_time):
        task = make_task(frequency=FREQUENCY_MONTHLY)
        coordinator.tasks["t1"] = task
        coordinator.last_monthly_reset = date(fixed_time.year, fixed_time.month, 1)

        await coordinator._check_automatic_resets()

        coordinator.store.async_save.assert_not_called()


# ---------------------------------------------------------------------------
# Reset lock (1.4 regression)
# ---------------------------------------------------------------------------

class TestResetLock:
    async def test_concurrent_resets_blocked(self, coordinator):
        """Second call while lock is held should return immediately."""
        coordinator.tasks["t1"] = make_task(frequency=FREQUENCY_DAILY)
        coordinator.last_daily_reset = None

        async def slow_save():
            await asyncio.sleep(0.05)

        coordinator.store.async_save = AsyncMock(side_effect=slow_save)

        async with coordinator._reset_lock:
            # Lock is held — check_automatic_resets should skip
            await coordinator._check_automatic_resets()

        # save never called because lock was held
        coordinator.store.async_save.assert_not_called()


# ---------------------------------------------------------------------------
# complete_task / validate_task
# ---------------------------------------------------------------------------

class TestCompleteTask:
    async def test_complete_task_with_validation(self, coordinator):
        child = make_child()
        task = make_task()
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task

        result = await coordinator.async_complete_task("t1", "c1", validation_required=True)

        assert result is True
        assert task.get_status_for_child("c1") == "pending_validation"
        assert child.points == 0  # no points yet

    async def test_complete_task_without_validation_awards_points(self, coordinator):
        child = make_child()
        task = make_task(points=15)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task

        await coordinator.async_complete_task("t1", "c1", validation_required=False)

        assert child.points == 15

    async def test_complete_task_fires_event(self, coordinator):
        child = make_child()
        task = make_task(points=10)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task

        await coordinator.async_complete_task("t1", "c1", validation_required=False)

        coordinator.hass.bus.async_fire.assert_called()

    async def test_complete_task_nonexistent_returns_false(self, coordinator):
        result = await coordinator.async_complete_task("nonexistent", "c1")
        assert result is False

    async def test_complete_task_wrong_child_returns_false(self, coordinator):
        child = make_child()
        task = make_task(child_ids=["c2"])
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task

        result = await coordinator.async_complete_task("t1", "c1")
        assert result is False


class TestValidateTask:
    async def test_validate_awards_points(self, coordinator):
        child = make_child()
        task = make_task(points=20)
        task.complete_for_child("c1", validation_required=True)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task

        result = await coordinator.async_validate_task("t1")

        assert result is True
        assert child.points == 20

    async def test_validate_level_up_fires_event(self, coordinator):
        child = make_child(points=95)
        task = make_task(points=10)  # 95+10=105 → level 2
        task.complete_for_child("c1", validation_required=True)
        coordinator.children["c1"] = child
        coordinator.tasks["t1"] = task

        await coordinator.async_validate_task("t1")

        calls = [str(c) for c in coordinator.hass.bus.async_fire.call_args_list]
        assert any("level_up" in c for c in calls)

    async def test_validate_nonexistent_task_returns_false(self, coordinator):
        result = await coordinator.async_validate_task("nonexistent")
        assert result is False


# ---------------------------------------------------------------------------
# Claim reward
# ---------------------------------------------------------------------------

class TestClaimReward:
    async def test_claim_deducts_points(self, coordinator):
        child = make_child(points=100)
        reward = make_reward(cost=50)
        coordinator.children["c1"] = child
        coordinator.rewards["r1"] = reward

        result = await coordinator.async_claim_reward("r1", "c1")

        assert result is True
        assert child.points == 50

    async def test_claim_fails_insufficient_points(self, coordinator):
        child = make_child(points=30)
        reward = make_reward(cost=50)
        coordinator.children["c1"] = child
        coordinator.rewards["r1"] = reward

        result = await coordinator.async_claim_reward("r1", "c1")

        assert result is False
        assert child.points == 30

    async def test_claim_fires_event(self, coordinator):
        child = make_child(points=100)
        reward = make_reward(cost=0)
        coordinator.children["c1"] = child
        coordinator.rewards["r1"] = reward

        await coordinator.async_claim_reward("r1", "c1")

        coordinator.hass.bus.async_fire.assert_called()


# ---------------------------------------------------------------------------
# Backup / restore
# ---------------------------------------------------------------------------

class TestBackupRestore:
    async def test_backup_produces_valid_json(self, coordinator):
        coordinator.children["c1"] = make_child()
        coordinator.tasks["t1"] = make_task()
        backup = await coordinator.async_backup_data()
        import json
        data = json.loads(backup)
        assert "children" in data
        assert "tasks" in data
        assert "version" in data

    async def test_restore_valid_backup(self, coordinator):
        import json
        backup = json.dumps({
            "version": 1,
            "children": {"c1": make_child().to_dict()},
            "tasks": {},
            "rewards": {},
        })
        result = await coordinator.async_restore_data(backup)
        assert result is True
        assert "c1" in coordinator.children

    async def test_restore_invalid_json_returns_false(self, coordinator):
        result = await coordinator.async_restore_data("{not valid json")
        assert result is False

    async def test_restore_corrupted_data_returns_false(self, coordinator):
        """Backup with invalid child data should fail gracefully."""
        import json
        corrupted = json.dumps({
            "version": 1,
            "children": {"c1": {"id": "c1"}},  # missing required 'name'
            "tasks": {},
            "rewards": {},
        })
        result = await coordinator.async_restore_data(corrupted)
        assert result is False

    async def test_restore_clears_existing_data(self, coordinator):
        coordinator.children["old_child"] = make_child("old_child")
        import json
        backup = json.dumps({
            "version": 1,
            "children": {"c1": make_child().to_dict()},
            "tasks": {},
            "rewards": {},
        })
        await coordinator.async_restore_data(backup)
        assert "old_child" not in coordinator.children


# ---------------------------------------------------------------------------
# Service unload (1.5 regression)
# ---------------------------------------------------------------------------

class TestServiceUnload:
    def test_async_services_used_for_removal(self, mock_hass):
        """async_unload_entry must use async_services(), not a hardcoded list."""
        import inspect
        from custom_components.kids_tasks import async_unload_entry
        source = inspect.getsource(async_unload_entry)
        assert "async_services()" in source
        assert "services_to_remove" not in source
