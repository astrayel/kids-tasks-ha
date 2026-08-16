"""Deadlines mixin for Kids Tasks coordinator."""
from __future__ import annotations

import logging

from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger("custom_components.kids_tasks.coordinator")


class DeadlinesMixin:
    async def _check_task_deadlines(self) -> None:
        """Check for tasks that have passed their deadline and apply penalties."""
        penalties_applied = False

        for task_id, task in self.tasks.items():
            # Skip bonus tasks (frequency = "none") - they don't have deadlines
            if task.frequency == "none":
                continue

            if task.check_deadline():  # Returns True if deadline just passed
                _LOGGER.info("Task '%s' (ID: %s) deadline passed", task.name, task_id)

                # Apply penalties only to assigned children who haven't completed the task
                for child_id in task.get_assigned_child_ids():
                    if child_id in self.children and task.penalty_points > 0:
                        child_status = task.get_status_for_child(child_id)

                        # Only apply penalty if the child hasn't completed/validated the task
                        if child_status not in ("validated", "pending_validation", "not_applicable"):
                            child = self.children[child_id]
                            old_points = child.points
                            old_level = child.level

                            child.add_points(
                                -task.penalty_points,
                                description="'%s' non terminée" % task.name,
                                action_type="task_penalty",
                                related_entity_id=task.id,
                                related_entity_name=task.name
                            )

                            if child_id in task.child_statuses:
                                task.child_statuses[child_id].penalty_applied = True
                                task.child_statuses[child_id].penalty_applied_at = dt_util.now()

                            penalties_applied = True

                            _LOGGER.info(
                                "Applied deadline penalty of %d points to %s for task '%s' "
                                "(points: %d -> %d, level: %d -> %d)",
                                task.penalty_points, child.name, task.name,
                                old_points, child.points, old_level, child.level,
                            )

                            # Fire penalty event
                            self.hass.bus.async_fire(
                                "kids_tasks_penalty_applied",
                                {
                                    "task_id": task.id,
                                    "task_name": task.name,
                                    "child_id": child_id,
                                    "child_name": child.name,
                                    "penalty_points": task.penalty_points,
                                    "old_points": old_points,
                                    "new_points": child.points,
                                    "old_level": old_level,
                                    "new_level": child.level,
                                    "penalty_type": "deadline",
                                    "frequency": task.frequency
                                },
                            )

        # Save data if penalties were applied
        if penalties_applied:
            await self.async_save_data()

    async def _send_validation_notification(self, task, child) -> None:
        """Send a Home Assistant notification for task validation."""
        try:
            child_name = child.name if child else "Enfant inconnu"
            message = f"Tâche à valider !\n\n"
            message += f"{child_name} a terminé la tâche :\n"
            message += f"{task.name}\n\n"

            if task.points > 0 or task.coins > 0:
                message += "Récompense en attente :\n"
                if task.points > 0:
                    message += f"• {task.points} points\n"
                if task.coins > 0:
                    message += f"• {task.coins} coins\n"

            message += "\nValidez depuis l'onglet Validation de votre tableau de bord Kids Tasks"

            # Send persistent notification
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "Kids Tasks - Validation requise",
                    "message": message,
                    "notification_id": f"kids_tasks_validation_{task.id}",
                }
            )

            _LOGGER.info("Notification sent for task validation: %s by %s", task.name, child.name if child else 'Unknown')

        except Exception as e:
            _LOGGER.error("Failed to send validation notification: %s", e)
