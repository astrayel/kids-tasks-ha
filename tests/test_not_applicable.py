"""A task not scheduled today is neither owed nor earned."""
from __future__ import annotations

import pytest

from custom_components.kids_tasks.const import (
    TASK_STATUS_NOT_APPLICABLE,
    TASK_STATUS_TODO,
    TASK_STATUS_VALIDATED,
)
from custom_components.kids_tasks.models import Child, Task, TaskChildStatus


# conftest pins "now" to Saturday 2024-06-15, so "sat" is today.
TODAY = "sat"
NOT_TODAY = "mon"


def _weekday_task(days: list[str], penalty: int = 5) -> Task:
    task = Task(
        id="t1",
        name="Sortir les poubelles",
        frequency="daily",
        points=10,
        penalty_points=penalty,
    )
    task.assigned_child_ids = ["leo"]
    task.weekly_days = days
    task.child_statuses["leo"] = TaskChildStatus(child_id="leo")
    return task


@pytest.fixture
def coord(coordinator):
    coordinator.children["leo"] = Child(id="leo", name="Léo", points=100)
    return coordinator


class TestUnscheduledDay:
    async def test_status_becomes_not_applicable(self, coord):
        task = _weekday_task([NOT_TODAY])
        coord.tasks["t1"] = task
        await coord._reset_tasks_with_penalty([task], "daily")
        assert task.get_status_for_child("leo") == TASK_STATUS_NOT_APPLICABLE

    async def test_status_is_not_faked_as_validated(self, coord):
        """The old behaviour inflated "tasks done today" and the statistics."""
        task = _weekday_task([NOT_TODAY])
        coord.tasks["t1"] = task
        await coord._reset_tasks_with_penalty([task], "daily")
        assert task.get_status_for_child("leo") != TASK_STATUS_VALIDATED

    async def test_scheduled_day_stays_todo(self, coord):
        task = _weekday_task([TODAY])
        coord.tasks["t1"] = task
        await coord._reset_tasks_with_penalty([task], "daily")
        assert task.get_status_for_child("leo") == TASK_STATUS_TODO


class TestNoPenalty:
    async def test_not_applicable_is_never_penalised(self, coord):
        task = _weekday_task([NOT_TODAY])
        coord.tasks["t1"] = task

        # First reset marks it not_applicable for today...
        await coord._reset_tasks_with_penalty([task], "daily")
        before = coord.children["leo"].points

        # ...and the next one must not charge for a day it was never due.
        await coord._reset_tasks_with_penalty([task], "daily")
        assert coord.children["leo"].points == before

    async def test_an_actually_missed_task_is_still_penalised(self, coord):
        task = _weekday_task([TODAY])
        task.complete_for_child("leo")
        task.reset()
        coord.tasks["t1"] = task

        before = coord.children["leo"].points
        await coord._reset_tasks_with_penalty([task], "daily")
        assert coord.children["leo"].points == before - 5


class TestGlobalStatus:
    def test_task_is_not_applicable_when_no_child_is_scheduled(self):
        task = _weekday_task([NOT_TODAY])
        task.complete_for_child("leo")
        task.child_statuses["leo"].status = TASK_STATUS_NOT_APPLICABLE
        task._update_global_status()
        assert task.status == TASK_STATUS_NOT_APPLICABLE

    def test_mixed_validated_and_not_applicable_reads_as_validated(self):
        task = _weekday_task([TODAY])
        task.assigned_child_ids = ["leo", "emma"]
        task.complete_for_child("leo", validation_required=False)
        task.complete_for_child("emma", validation_required=False)
        task.child_statuses["emma"].status = TASK_STATUS_NOT_APPLICABLE

        task._update_global_status()
        assert task.status == TASK_STATUS_VALIDATED

    def test_a_child_still_owing_keeps_the_task_todo(self):
        task = _weekday_task([TODAY])
        task.assigned_child_ids = ["leo", "emma"]
        task.complete_for_child("leo", validation_required=False)
        task.child_statuses["emma"] = TaskChildStatus(child_id="emma")

        task._update_global_status()
        assert task.status == TASK_STATUS_TODO
