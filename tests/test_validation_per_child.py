"""Validating or rejecting a shared task must only affect the targeted child."""
from __future__ import annotations

import pytest

from custom_components.kids_tasks.models import Child, Task
from custom_components.kids_tasks.const import FREQUENCY_DAILY


def _shared_task() -> Task:
    """A daily task worth 10 points, assigned to three children."""
    task = Task(id="t1", name="Ranger la chambre", frequency=FREQUENCY_DAILY, points=10, coins=2)
    task.assigned_child_ids = ["leo", "emma", "nina"]
    return task


@pytest.fixture
def family(coordinator):
    """Coordinator with three children and one task they all share."""
    for cid, name in (("leo", "Léo"), ("emma", "Emma"), ("nina", "Nina")):
        coordinator.children[cid] = Child(id=cid, name=name)
    coordinator.tasks["t1"] = _shared_task()
    return coordinator


async def _submit(coordinator, child_id: str) -> None:
    """The child marks the task done; it lands in pending validation."""
    await coordinator.async_complete_task("t1", child_id, validation_required=True)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidateOneChild:
    async def test_only_targeted_child_is_validated(self, family):
        await _submit(family, "leo")
        await _submit(family, "emma")

        await family.async_validate_task("t1", "leo")

        task = family.tasks["t1"]
        assert task.get_status_for_child("leo") == "validated"
        assert task.get_status_for_child("emma") == "pending_validation"

    async def test_only_targeted_child_is_awarded(self, family):
        await _submit(family, "leo")
        await _submit(family, "emma")

        await family.async_validate_task("t1", "leo")

        assert family.children["leo"].points == 10
        assert family.children["leo"].coins == 2
        assert family.children["emma"].points == 0
        assert family.children["emma"].coins == 0

    async def test_untouched_sibling_keeps_todo(self, family):
        await _submit(family, "leo")
        await family.async_validate_task("t1", "leo")
        assert family.tasks["t1"].get_status_for_child("nina") == "todo"

    async def test_validating_child_without_submission_fails(self, family):
        await _submit(family, "leo")
        assert await family.async_validate_task("t1", "nina") is False
        assert family.children["nina"].points == 0

    async def test_without_child_id_all_pending_are_validated(self, family):
        await _submit(family, "leo")
        await _submit(family, "emma")

        await family.async_validate_task("t1")

        assert family.children["leo"].points == 10
        assert family.children["emma"].points == 10
        assert family.children["nina"].points == 0

    async def test_returns_false_for_unknown_task(self, family):
        assert await family.async_validate_task("nope", "leo") is False


# ---------------------------------------------------------------------------
# Rejection
# ---------------------------------------------------------------------------

class TestRejectOneChild:
    async def test_only_targeted_child_is_reset(self, family):
        await _submit(family, "leo")
        await _submit(family, "emma")

        await family.async_reject_task("t1", "leo", reason="Pas fini")

        task = family.tasks["t1"]
        assert task.get_status_for_child("leo") == "todo"
        assert task.get_status_for_child("emma") == "pending_validation"

    async def test_rejection_awards_nothing(self, family):
        await _submit(family, "leo")
        await family.async_reject_task("t1", "leo")
        assert family.children["leo"].points == 0

    async def test_rejecting_child_without_submission_fails(self, family):
        await _submit(family, "leo")
        assert await family.async_reject_task("t1", "nina") is False

    async def test_without_child_id_the_whole_task_is_reset(self, family):
        await _submit(family, "leo")
        await _submit(family, "emma")

        await family.async_reject_task("t1")

        task = family.tasks["t1"]
        assert task.get_status_for_child("leo") == "todo"
        assert task.get_status_for_child("emma") == "todo"

    async def test_previously_validated_sibling_is_kept(self, family):
        await _submit(family, "leo")
        await _submit(family, "emma")
        await family.async_validate_task("t1", "emma")

        await family.async_reject_task("t1", "leo")

        assert family.tasks["t1"].get_status_for_child("emma") == "validated"
        assert family.children["emma"].points == 10


# ---------------------------------------------------------------------------
# Model-level helper
# ---------------------------------------------------------------------------

class TestResetForChild:
    def test_returns_false_when_child_has_no_status(self):
        assert _shared_task().reset_for_child("leo") is False

    def test_clears_penalty_flag(self):
        task = _shared_task()
        task.complete_for_child("leo")
        task.child_statuses["leo"].penalty_applied = True

        assert task.reset_for_child("leo") is True
        assert task.child_statuses["leo"].penalty_applied is False
        assert task.child_statuses["leo"].completed_at is None

    def test_clears_completed_by_when_it_was_that_child(self):
        task = _shared_task()
        task.complete_for_child("leo")
        assert task.completed_by_child_id == "leo"

        task.reset_for_child("leo")
        assert task.completed_by_child_id is None
