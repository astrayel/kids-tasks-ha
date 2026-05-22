"""Calendar platform for Kids Tasks — exposes task deadlines as HA calendar events."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CATEGORY_ICONS
from .coordinator import KidsTasksDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""
    coordinator: KidsTasksDataUpdateCoordinator = entry.runtime_data.coordinator
    async_add_entities([KidsTasksCalendar(coordinator, entry.entry_id)])


class KidsTasksCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar entity exposing task deadlines and recurring tasks."""

    def __init__(self, coordinator: KidsTasksDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "kidtasks_calendar"
        self._attr_name = "Kids Tasks"
        self.entity_id = "calendar.kids_tasks"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "system")},
            name="Kids Tasks Manager",
            manufacturer="Kids Tasks",
            model="Calendar",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        now = dt_util.now()
        upcoming = [e for e in self._build_events(now, now + timedelta(days=7)) if e.start >= now]
        return min(upcoming, key=lambda e: e.start) if upcoming else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within the given time window."""
        return self._build_events(start_date, end_date)

    def _build_events(self, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        events: list[CalendarEvent] = []
        tasks = self.coordinator.data.get("tasks", {})
        children = self.coordinator.data.get("children", {})
        today = dt_util.now().date()

        for task_id, task in tasks.items():
            if not task.get("active", True):
                continue

            child_names = [
                children[cid]["name"]
                for cid in task.get("assigned_child_ids", [])
                if cid in children and children[cid].get("name")
            ]
            child_label = ", ".join(child_names) if child_names else "Non assigné"
            cat_icon = CATEGORY_ICONS.get(task.get("category", "other"), "📋")
            summary = f"{cat_icon} {task.get('name', 'Tâche')} — {child_label}"
            description = (
                f"Points : {task.get('points', 0)}\n"
                f"Catégorie : {task.get('category', 'other')}\n"
                f"Statut : {task.get('status', 'todo')}\n"
                + (f"Description : {task['description']}" if task.get("description") else "")
            )

            # Tasks with an explicit deadline_time → timed event on today
            deadline_str = task.get("deadline_time")
            if deadline_str:
                try:
                    hour, minute = map(int, deadline_str.split(":"))
                    event_start = dt_util.as_local(
                        datetime.combine(today, datetime.min.time()).replace(hour=hour, minute=minute)
                    )
                    event_end = event_start + timedelta(hours=1)
                    if start_date <= event_start <= end_date:
                        events.append(CalendarEvent(
                            start=event_start,
                            end=event_end,
                            summary=f"⏰ {summary}",
                            description=description,
                            uid=f"kidtasks_deadline_{task_id}",
                        ))
                except (ValueError, AttributeError):
                    pass

            # Daily tasks → all-day event for today if not yet validated
            frequency = task.get("frequency", "")
            status = task.get("status", "todo")
            if frequency == "daily" and status not in ("validated", "failed"):
                event_date = today
                if start_date.date() <= event_date <= end_date.date():
                    events.append(CalendarEvent(
                        start=datetime.combine(event_date, datetime.min.time()),
                        end=datetime.combine(event_date + timedelta(days=1), datetime.min.time()),
                        summary=summary,
                        description=description,
                        uid=f"kidtasks_daily_{task_id}_{event_date.isoformat()}",
                    ))

            # Weekly tasks → all-day event on assigned days this week
            if frequency == "weekly":
                weekly_days = task.get("weekly_days") or []
                day_map = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6,
                }
                for day_name in weekly_days:
                    day_num = day_map.get(day_name.lower())
                    if day_num is None:
                        continue
                    days_ahead = (day_num - today.weekday()) % 7
                    event_date = today + timedelta(days=days_ahead)
                    if start_date.date() <= event_date <= end_date.date():
                        events.append(CalendarEvent(
                            start=datetime.combine(event_date, datetime.min.time()),
                            end=datetime.combine(event_date + timedelta(days=1), datetime.min.time()),
                            summary=summary,
                            description=description,
                            uid=f"kidtasks_weekly_{task_id}_{event_date.isoformat()}",
                        ))

        return events
