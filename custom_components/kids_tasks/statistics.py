"""Long-term statistics for Kids Tasks integration."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_VALIDATED,
)

_LOGGER = logging.getLogger(__name__)

_DONE_STATUSES = {TASK_STATUS_COMPLETED, TASK_STATUS_VALIDATED}


def _hour_start(dt: datetime) -> datetime:
    """Return the top-of-hour for a datetime (UTC)."""
    return dt.replace(minute=0, second=0, microsecond=0)


async def async_record_statistics(hass: HomeAssistant, coordinator) -> None:
    """Push one snapshot of Kids Tasks state into the HA recorder statistics."""
    try:
        from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
        from homeassistant.components.recorder.statistics import async_add_external_statistics
    except ImportError:
        _LOGGER.debug("Recorder not available - skipping statistics")
        return

    try:
        from homeassistant.components.recorder.statistics import StatisticMeanType
        _mean_type = StatisticMeanType.ARITHMETIC
    except ImportError:
        _mean_type = None

    start = _hour_start(dt_util.utcnow())
    children = coordinator.children
    tasks = coordinator.tasks

    # ------------------------------------------------------------------ #
    # Per-child statistics                                                 #
    # ------------------------------------------------------------------ #
    for child_id, child in children.items():
        name = child.name

        # Current point balance
        _push(
            hass, async_add_external_statistics, StatisticMetaData, StatisticData,
            statistic_id=f"{DOMAIN}:child_{child_id}_points",
            name=f"{name} - Points",
            unit="pts", start=start, value=float(child.points), mean_type=_mean_type,
        )

        # Current level
        _push(
            hass, async_add_external_statistics, StatisticMetaData, StatisticData,
            statistic_id=f"{DOMAIN}:child_{child_id}_level",
            name=f"{name} - Niveau",
            unit=None, start=start, value=float(child.level), mean_type=_mean_type,
        )

        # Tasks completed (validated or completed) right now
        done = sum(
            1
            for task in tasks.values()
            if child_id in task.assigned_child_ids
            and child_id in task.child_statuses
            and task.child_statuses[child_id].status in _DONE_STATUSES
        )
        _push(
            hass, async_add_external_statistics, StatisticMetaData, StatisticData,
            statistic_id=f"{DOMAIN}:child_{child_id}_tasks_done",
            name=f"{name} - Taches Completees",
            unit=None, start=start, value=float(done), mean_type=_mean_type,
        )

    # ------------------------------------------------------------------ #
    # Global statistics                                                    #
    # ------------------------------------------------------------------ #
    pending = sum(
        1
        for task in tasks.values()
        for cs in task.child_statuses.values()
        if cs.status == "pending_validation"
    )
    _push(
        hass, async_add_external_statistics, StatisticMetaData, StatisticData,
        statistic_id=f"{DOMAIN}:pending_validations",
        name="Taches en Attente de Validation",
        unit=None, start=start, value=float(pending), mean_type=_mean_type,
    )

    _LOGGER.debug(
        "Recorded statistics for %d children at %s",
        len(children),
        start.isoformat(),
    )


def _push(
    hass: HomeAssistant,
    async_add_external_statistics,
    StatisticMetaData,
    StatisticData,
    *,
    statistic_id: str,
    name: str,
    unit: str | None,
    start: datetime,
    value: float,
    mean_type=None,
) -> None:
    """Insert a single mean-based statistic into the recorder."""
    kwargs = {
        "has_mean": True,
        "has_sum": False,
        "name": name,
        "source": DOMAIN,
        "statistic_id": statistic_id,
        "unit_of_measurement": unit,
    }
    if mean_type is not None:
        kwargs["mean_type"] = mean_type
    metadata = StatisticMetaData(**kwargs)
    data = StatisticData(start=start, mean=value)
    async_add_external_statistics(hass, metadata, [data])
