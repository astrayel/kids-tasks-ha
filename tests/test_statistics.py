"""Tests for long-term statistics recording."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from unittest.mock import MagicMock, patch

from custom_components.kids_tasks import statistics as stats_module
from custom_components.kids_tasks.models import Child, Task


@pytest.fixture
def recorded(mock_hass):
    """Run async_record_statistics and capture every statistic pushed."""
    captured: list[dict] = []

    def _fake_push(hass, adder, meta_cls, data_cls, **kwargs):
        captured.append(kwargs)

    async def _run(children: dict, tasks: dict):
        coordinator = MagicMock()
        coordinator.children = children
        coordinator.tasks = tasks
        with patch.object(stats_module, "_push", _fake_push):
            await stats_module.async_record_statistics(mock_hass, coordinator)
        return captured

    return _run


def _ids(entries: list[dict]) -> set[str]:
    return {e["statistic_id"] for e in entries}


class TestChildStatistics:
    async def test_uuid_dashes_are_sanitised(self, recorded):
        """HA rejects a statistic_id whose suffix contains dashes (BUG-003)."""
        child_id = "3f2a1b4c-8e7d-4f9a-b2c1-0d5e6f7a8b9c"
        entries = await recorded({child_id: Child(id=child_id, name="Léo")}, {})
        assert entries, "no statistics recorded"
        for entry in entries:
            suffix = entry["statistic_id"].split(":", 1)[1]
            assert "-" not in suffix

    async def test_points_are_recorded(self, recorded):
        entries = await recorded({"leo": Child(id="leo", name="Léo", points=320)}, {})
        points = next(e for e in entries if e["statistic_id"].endswith("_points"))
        assert points["value"] == 320.0

    async def test_level_is_recorded(self, recorded):
        entries = await recorded({"leo": Child(id="leo", name="Léo", level=4)}, {})
        level = next(e for e in entries if e["statistic_id"].endswith("_level"))
        assert level["value"] == 4.0

    async def test_each_child_gets_its_own_ids(self, recorded):
        entries = await recorded(
            {
                "leo": Child(id="leo", name="Léo"),
                "emma": Child(id="emma", name="Emma"),
            },
            {},
        )
        assert any("child_leo_points" in i for i in _ids(entries))
        assert any("child_emma_points" in i for i in _ids(entries))

    async def test_child_name_is_carried_into_the_label(self, recorded):
        entries = await recorded({"leo": Child(id="leo", name="Léo")}, {})
        assert any("Léo" in e["name"] for e in entries)


class TestGlobalStatistics:
    async def test_pending_validations_are_recorded(self, recorded):
        task = Task(id="t1", name="Ranger", points=10)
        task.assigned_child_ids = ["leo"]
        task.complete_for_child("leo", validation_required=True)

        entries = await recorded({"leo": Child(id="leo", name="Léo")}, {"t1": task})
        assert any(i.endswith(":pending_validations") for i in _ids(entries))


class TestResilience:
    async def test_no_children_records_nothing_per_child(self, recorded):
        entries = await recorded({}, {})
        assert not any("child_" in i for i in _ids(entries))

    async def test_missing_recorder_is_not_fatal(self, mock_hass):
        """Statistics are a bonus; an install without recorder must still run."""
        coordinator = MagicMock()
        coordinator.children = {}
        coordinator.tasks = {}
        with patch.dict("sys.modules", {"homeassistant.components.recorder.models": None}):
            await stats_module.async_record_statistics(mock_hass, coordinator)


class TestHourStart:
    def test_truncates_to_the_hour(self):
        dt = datetime(2024, 6, 15, 10, 37, 42, 123456, tzinfo=timezone.utc)
        assert stats_module._hour_start(dt) == datetime(
            2024, 6, 15, 10, 0, 0, 0, tzinfo=timezone.utc
        )
