# ============================================================================
# diagnostics.py
# ============================================================================

"""Diagnostics support for Kids Tasks."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import KidsTasksDataUpdateCoordinator

TO_REDACT = {"name", "avatar", "avatar_data", "person_entity_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: Any
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: KidsTasksDataUpdateCoordinator = entry.runtime_data.coordinator

    children_summary = []
    for child in coordinator.children.values():
        children_summary.append(async_redact_data({
            "name": child.name,
            "level": child.level,
            "points": child.points,
            "coins": child.coins,
            "history_entries": len(child.points_history),
        }, TO_REDACT))

    tasks_summary = []
    for task in coordinator.tasks.values():
        tasks_summary.append({
            "frequency": task.frequency,
            "status": task.status,
            "points": task.points,
            "penalty_points": task.penalty_points,
            "has_deadline": bool(task.deadline_time),
            "assigned_children": len(task.assigned_child_ids),
        })

    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "coordinator": {
            "last_daily_reset": str(coordinator.last_daily_reset),
            "last_weekly_reset": str(coordinator.last_weekly_reset),
            "last_monthly_reset": str(coordinator.last_monthly_reset),
        },
        "counts": {
            "children": len(coordinator.children),
            "tasks": len(coordinator.tasks),
            "rewards": len(coordinator.rewards),
        },
        "children": children_summary,
        "tasks": tasks_summary,
    }
