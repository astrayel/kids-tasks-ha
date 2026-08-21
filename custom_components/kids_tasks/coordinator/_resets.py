"""Resets mixin for Kids Tasks coordinator."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.util import dt as dt_util

from ..const import TASK_STATUS_NOT_APPLICABLE, TASK_STATUS_VALIDATED
from ..models import TaskChildStatus

_LOGGER = logging.getLogger("custom_components.kids_tasks.coordinator")

# A child owes nothing for a task already earned, or not scheduled that day.
NO_PENALTY_STATUSES = (TASK_STATUS_VALIDATED, TASK_STATUS_NOT_APPLICABLE)


class ResetsMixin:
    async def _check_automatic_resets(self) -> None:
        """Check if tasks need to be automatically reset based on frequency."""
        if self._reset_lock.locked():
            _LOGGER.debug("Reset already in progress, skipping")
            return

        async with self._reset_lock:
            today = dt_util.now().date()

            if self.last_daily_reset is None or self.last_daily_reset < today:
                daily_tasks = [task for task in self.tasks.values() if task.frequency == "daily"]
                if daily_tasks:
                    _LOGGER.info(
                        "Auto-resetting %d daily tasks (%d with penalties) - last reset was %s",
                        len(daily_tasks),
                        sum(1 for t in daily_tasks if t.penalty_points > 0),
                        self.last_daily_reset,
                    )
                    await self._reset_tasks_with_penalty(daily_tasks, "daily")
                    self.last_daily_reset = today
                    await self.async_save_data()
                    _LOGGER.info("Daily reset completed - updated timestamp to %s", today)

            week_start = today - timedelta(days=today.weekday())
            if self.last_weekly_reset is None or self.last_weekly_reset < week_start:
                weekly_tasks = [task for task in self.tasks.values() if task.frequency == "weekly"]
                if weekly_tasks:
                    _LOGGER.info(
                        "Auto-resetting %d weekly tasks (%d with penalties) - last reset was %s",
                        len(weekly_tasks),
                        sum(1 for t in weekly_tasks if t.penalty_points > 0),
                        self.last_weekly_reset,
                    )
                    await self._reset_tasks_with_penalty(weekly_tasks, "weekly")
                    self.last_weekly_reset = week_start
                    await self.async_save_data()
                    _LOGGER.info("Weekly reset completed - updated timestamp to %s", week_start)

            month_start = today.replace(day=1)
            if self.last_monthly_reset is None or self.last_monthly_reset < month_start:
                monthly_tasks = [task for task in self.tasks.values() if task.frequency == "monthly"]
                if monthly_tasks:
                    _LOGGER.info(
                        "Auto-resetting %d monthly tasks (%d with penalties) - last reset was %s",
                        len(monthly_tasks),
                        sum(1 for t in monthly_tasks if t.penalty_points > 0),
                        self.last_monthly_reset,
                    )
                    await self._reset_tasks_with_penalty(monthly_tasks, "monthly")
                    self.last_monthly_reset = month_start
                    await self.async_save_data()
                    _LOGGER.info("Monthly reset completed - updated timestamp to %s", month_start)

    async def _reset_tasks_with_penalty(self, tasks: list, frequency: str) -> bool:
        """Reset a list of tasks and apply penalties for uncompleted ones. Returns True if any changes were made."""
        penalties_applied = False
        tasks_reset = False

        for task in tasks:
            # Only apply penalty for available tasks that have penalty_points defined
            if task.is_available() and task.penalty_points > 0:
                assigned_children = task.get_assigned_child_ids()
                for child_id in assigned_children:
                    if child_id in self.children:
                        child = self.children[child_id]
                        child_status = task.get_status_for_child(child_id)

                        # Apply penalty if task was not validated by this child
                        if child_status not in NO_PENALTY_STATUSES:
                            # Check if penalty was already applied for this period (e.g., deadline penalty)
                            penalty_already_applied = False
                            if child_id in task.child_statuses:
                                penalty_already_applied = task.child_statuses[child_id].penalty_applied

                            if not penalty_already_applied:
                                # Use penalty_points (no default penalty)
                                penalty_points = task.penalty_points
                                old_points = child.points
                                old_level = child.level

                                # Apply penalty with tracking
                                if penalty_points > 0:
                                    child.add_points(
                                        -penalty_points,
                                        description=f"Reset automatique {frequency} - Tâche '{task.name}' non terminée",
                                        action_type="task_penalty",
                                        related_entity_id=task.id,
                                        related_entity_name=task.name
                                    )

                                if child_id in task.child_statuses:
                                    task.child_statuses[child_id].penalty_applied = True
                                    task.child_statuses[child_id].penalty_applied_at = dt_util.now()

                                penalties_applied = True

                                _LOGGER.info(
                                    "Applied %s penalty of %d points to %s for uncompleted task '%s' "
                                    "(points: %d -> %d, level: %d -> %d)",
                                    frequency, penalty_points, child.name, task.name,
                                    old_points, child.points, old_level, child.level
                                )

                                # Fire penalty event
                                self.hass.bus.async_fire(
                                    "kids_tasks_penalty_applied",
                                    {
                                        "task_id": task.id,
                                        "task_name": task.name,
                                        "child_id": child_id,
                                        "child_name": child.name,
                                        "penalty_points": penalty_points,
                                        "old_points": old_points,
                                        "new_points": child.points,
                                        "old_level": old_level,
                                        "new_level": child.level,
                                        "frequency": frequency,
                                        "reset_type": "automatic"
                                    },
                                )
                            else:
                                _LOGGER.info(
                                    "Skipping penalty for %s on task '%s' - penalty already applied this period",
                                    child.name, task.name
                                )

            # Reset task status for next period
            task.reset()
            tasks_reset = True

            # A daily task restricted to certain weekdays is neither owed nor
            # earned on the other days. It used to be marked "validated" to
            # dodge the penalty, which inflated the "tasks done today" counters
            # and the statistics; not_applicable says what is actually true.
            if frequency == "daily" and task.weekly_days:
                current_day = dt_util.now().strftime('%a').lower()
                if current_day not in task.weekly_days:
                    for child_id in task.get_assigned_child_ids():
                        # Create the entry when missing: without it the child
                        # reads as "todo" and gets charged on the next reset.
                        if child_id not in task.child_statuses:
                            task.child_statuses[child_id] = TaskChildStatus(child_id=child_id)
                        task.child_statuses[child_id].status = TASK_STATUS_NOT_APPLICABLE
                    task._update_global_status()

        # Note: Saving is handled by the caller to ensure atomic operations
        return tasks_reset or penalties_applied

    async def async_reset_all_daily_tasks(self) -> None:
        """Reset all daily tasks to todo status and deduct points for uncompleted recurring tasks."""

        for task in self.tasks.values():
            if task.frequency == "daily":

                # Vérifier chaque enfant assigné pour appliquer des pénalités
                assigned_children = task.get_assigned_child_ids()
                for child_id in assigned_children:
                    if child_id in self.children:
                        child = self.children[child_id]
                        child_status = task.get_status_for_child(child_id)

                        # Si l'enfant n'a pas validé la tâche, appliquer une pénalité
                        if child_status not in NO_PENALTY_STATUSES:
                            # Pour reset manuel: utiliser penalty_points si défini, sinon moitié des points (minimum 1)
                            penalty_points = task.penalty_points if task.penalty_points > 0 else max(1, task.points // 2)
                            old_points = child.points
                            old_level = child.level

                            # Apply penalty with tracking
                            if penalty_points > 0:
                                child.add_points(
                                    -penalty_points,
                                    description=f"Reset manuel quotidien - Tâche '{task.name}' non terminée",
                                    action_type="task_penalty",
                                    related_entity_id=task.id,
                                    related_entity_name=task.name
                                )

                            if child_id in task.child_statuses:
                                task.child_statuses[child_id].penalty_applied = True
                                task.child_statuses[child_id].penalty_applied_at = dt_util.now()

                            self.hass.bus.async_fire(
                                "kids_tasks_penalty_applied",
                                {
                                    "task_id": task.id,
                                    "task_name": task.name,
                                    "child_id": child_id,
                                    "child_name": child.name,
                                    "penalty_points": penalty_points,
                                    "old_points": old_points,
                                    "new_points": child.points,
                                    "old_level": old_level,
                                    "new_level": child.level,
                                    "frequency": "daily",
                                    "reset_type": "manual"
                                },
                            )

                # Utiliser la méthode reset() du modèle pour remettre la tâche à zéro
                task.reset()

        await self.async_save_data()
        await self.async_request_refresh()

    async def async_reset_all_weekly_tasks(self) -> None:
        """Reset all weekly tasks to todo status and deduct points for uncompleted tasks."""

        for task in self.tasks.values():
            if task.frequency == "weekly":
                _LOGGER.debug("Resetting weekly task: %s (ID: %s)", task.name, task.id)

                # Vérifier chaque enfant assigné pour appliquer des pénalités
                assigned_children = task.get_assigned_child_ids()
                for child_id in assigned_children:
                    if child_id in self.children:
                        child = self.children[child_id]
                        child_status = task.get_status_for_child(child_id)

                        # Si l'enfant n'a pas validé la tâche, appliquer une pénalité
                        if child_status not in NO_PENALTY_STATUSES:
                            # Pour reset manuel: utiliser penalty_points si défini, sinon moitié des points (minimum 1)
                            penalty_points = task.penalty_points if task.penalty_points > 0 else max(1, task.points // 2)
                            old_points = child.points
                            old_level = child.level

                            # Apply penalty with tracking
                            if penalty_points > 0:
                                child.add_points(
                                    -penalty_points,
                                    description=f"Reset manuel hebdomadaire - Tâche '{task.name}' non terminée",
                                    action_type="task_penalty",
                                    related_entity_id=task.id,
                                    related_entity_name=task.name
                                )

                            if child_id in task.child_statuses:
                                task.child_statuses[child_id].penalty_applied = True
                                task.child_statuses[child_id].penalty_applied_at = dt_util.now()

                            self.hass.bus.async_fire(
                                "kids_tasks_penalty_applied",
                                {
                                    "task_id": task.id,
                                    "task_name": task.name,
                                    "child_id": child_id,
                                    "child_name": child.name,
                                    "penalty_points": penalty_points,
                                    "old_points": old_points,
                                    "new_points": child.points,
                                    "old_level": old_level,
                                    "new_level": child.level,
                                    "frequency": "weekly",
                                    "reset_type": "manual"
                                },
                            )

                # Utiliser la méthode reset() du modèle pour remettre la tâche à zéro
                task.reset()

        await self.async_save_data()
        await self.async_request_refresh()

    async def async_reset_all_monthly_tasks(self) -> None:
        """Reset all monthly tasks to todo status and deduct points for uncompleted tasks."""

        for task in self.tasks.values():
            if task.frequency == "monthly":
                _LOGGER.debug("Resetting monthly task: %s (ID: %s)", task.name, task.id)

                # Vérifier chaque enfant assigné pour appliquer des pénalités
                assigned_children = task.get_assigned_child_ids()
                for child_id in assigned_children:
                    if child_id in self.children:
                        child = self.children[child_id]
                        child_status = task.get_status_for_child(child_id)

                        # Si l'enfant n'a pas validé la tâche, appliquer une pénalité
                        if child_status not in NO_PENALTY_STATUSES:
                            # Pour reset manuel: utiliser penalty_points si défini, sinon moitié des points (minimum 1)
                            penalty_points = task.penalty_points if task.penalty_points > 0 else max(1, task.points // 2)
                            old_points = child.points
                            old_level = child.level

                            # Apply penalty with tracking
                            if penalty_points > 0:
                                child.add_points(
                                    -penalty_points,
                                    description=f"Reset manuel mensuel - Tâche '{task.name}' non terminée",
                                    action_type="task_penalty",
                                    related_entity_id=task.id,
                                    related_entity_name=task.name
                                )

                            if child_id in task.child_statuses:
                                task.child_statuses[child_id].penalty_applied = True
                                task.child_statuses[child_id].penalty_applied_at = dt_util.now()

                            self.hass.bus.async_fire(
                                "kids_tasks_penalty_applied",
                                {
                                    "task_id": task.id,
                                    "task_name": task.name,
                                    "child_id": child_id,
                                    "child_name": child.name,
                                    "penalty_points": penalty_points,
                                    "old_points": old_points,
                                    "new_points": child.points,
                                    "old_level": old_level,
                                    "new_level": child.level,
                                    "frequency": "monthly",
                                    "reset_type": "manual"
                                },
                            )

                # Utiliser la méthode reset() du modèle pour remettre la tâche à zéro
                task.reset()

        await self.async_save_data()
        await self.async_request_refresh()
