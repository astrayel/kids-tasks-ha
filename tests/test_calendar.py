"""Tests for the calendar platform."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from unittest.mock import MagicMock, patch

from custom_components.kids_tasks.calendar import KidsTasksCalendar

# conftest pins "now" to Saturday 2024-06-15 10:00 UTC.
WINDOW_START = datetime(2024, 6, 10, tzinfo=timezone.utc)
WINDOW_END = datetime(2024, 6, 30, tzinfo=timezone.utc)


def _calendar(tasks: dict, children: dict | None = None) -> KidsTasksCalendar:
    coord = MagicMock()
    coord.data = {
        "tasks": tasks,
        "children": children or {"leo": {"name": "Léo"}},
    }
    with patch(
        "homeassistant.helpers.update_coordinator.CoordinatorEntity.__init__",
        return_value=None,
    ):
        cal = KidsTasksCalendar(coord, "entry")
        cal.coordinator = coord
        return cal


def _task(**overrides) -> dict:
    base = {
        "name": "Ranger la chambre",
        "active": True,
        "points": 10,
        "category": "bedroom",
        "frequency": "daily",
        "status": "todo",
        "assigned_child_ids": ["leo"],
    }
    base.update(overrides)
    return base


def _events(tasks: dict):
    return _calendar(tasks)._build_events(WINDOW_START, WINDOW_END)


class TestDailyTasks:
    def test_pending_daily_task_produces_an_event(self):
        assert len(_events({"t1": _task()})) == 1

    def test_summary_names_the_child(self):
        summary = _events({"t1": _task()})[0].summary
        assert "Ranger la chambre" in summary and "Léo" in summary

    def test_validated_task_produces_nothing(self):
        assert _events({"t1": _task(status="validated")}) == []

    def test_not_applicable_produces_nothing(self):
        """A day the task is not scheduled must not clutter the calendar."""
        assert _events({"t1": _task(status="not_applicable")}) == []

    def test_inactive_task_produces_nothing(self):
        assert _events({"t1": _task(active=False)}) == []

    def test_unassigned_task_is_labelled(self):
        events = _events({"t1": _task(assigned_child_ids=[])})
        assert "Non assigné" in events[0].summary


class TestWeeklyTasks:
    def test_abbreviated_day_names_are_understood(self):
        """The model stores strftime('%a') values — 'mon', not 'monday'."""
        events = _events({"t1": _task(frequency="weekly", weekly_days=["mon"])})
        assert len(events) == 1

    def test_full_day_names_still_work(self):
        events = _events({"t1": _task(frequency="weekly", weekly_days=["monday"])})
        assert len(events) == 1

    def test_event_lands_on_the_named_day(self):
        events = _events({"t1": _task(frequency="weekly", weekly_days=["wed"])})
        assert events[0].start.weekday() == 2

    def test_several_days_produce_several_events(self):
        events = _events({"t1": _task(frequency="weekly", weekly_days=["mon", "wed", "fri"])})
        assert len(events) == 3

    def test_unknown_day_is_skipped(self):
        events = _events({"t1": _task(frequency="weekly", weekly_days=["someday"])})
        assert events == []


class TestDeadlines:
    def test_deadline_produces_a_timed_event(self):
        events = _events({"t1": _task(deadline_time="18:00")})
        timed = [e for e in events if e.summary.startswith("[deadline]")]
        assert len(timed) == 1
        assert timed[0].start.hour == 18

    def test_malformed_deadline_is_ignored(self):
        events = _events({"t1": _task(deadline_time="pas une heure")})
        assert not any(e.summary.startswith("[deadline]") for e in events)

    def test_deadline_event_lasts_an_hour(self):
        events = _events({"t1": _task(deadline_time="18:00")})
        timed = next(e for e in events if e.summary.startswith("[deadline]"))
        assert timed.end - timed.start == timedelta(hours=1)


class TestIdentity:
    def test_unique_id_is_stable(self):
        assert _calendar({})._attr_unique_id == "kidtasks_calendar"

    def test_no_events_means_no_next_event(self):
        assert _calendar({}).event is None
