"""Business logic mixin for Kids Tasks coordinator."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from ..const import DOMAIN
from ..models import Child, Task, Reward

_LOGGER = logging.getLogger("custom_components.kids_tasks.coordinator")


class BusinessMixin:
    async def async_add_child(self, child: Child) -> None:
        """Add a new child."""
        self.children[child.id] = child
        await self.async_save_data()
        await self.async_request_refresh()

        add_entities = self._platform_add_entities.get("sensor")
        if add_entities is not None:
            try:
                from ..sensor import ChildPointsSensor, ChildLevelSensor, ChildTasksCompletedTodaySensor, ChildPointsHistorySensor
                add_entities([
                    ChildPointsSensor(self, child.id),
                    ChildLevelSensor(self, child.id),
                    ChildTasksCompletedTodaySensor(self, child.id),
                    ChildPointsHistorySensor(self, child.id),
                ])
                _LOGGER.debug("Child sensors created dynamically for child %s", child.id[:8])
            except Exception as e:
                _LOGGER.warning("Could not create child sensors dynamically: %s", e)

    async def async_update_child(self, child_id: str, updates: dict) -> None:
        """Update a child with new values."""
        if child_id in self.children:
            child = self.children[child_id]
            for key, value in updates.items():
                if hasattr(child, key):
                    setattr(child, key, value)
            await self.async_save_data()
            await self.async_request_refresh()

    async def async_remove_child(self, child_id: str, force_remove_entities: bool = False) -> None:
        """Remove a child and optionally force remove their entities."""
        if child_id in self.children:
            # Remove child data
            del self.children[child_id]

            # Remove tasks assigned to this child
            tasks_to_remove = [task_id for task_id, task in self.tasks.items()
                             if child_id in task.assigned_child_ids]
            for task_id in tasks_to_remove:
                del self.tasks[task_id]

            await self.async_save_data()
            await self.async_request_refresh()

            # Force remove entities if requested
            if force_remove_entities:
                await self._async_force_remove_child_entities(child_id)

    async def async_add_task(self, task: Task) -> None:
        """Add a new task."""
        try:
            _LOGGER.info("Adding task to coordinator: %s", task.name)
            self.tasks[task.id] = task
            _LOGGER.info("Task added to memory, saving data...")
            await self.async_save_data()
            _LOGGER.info("Data saved, requesting refresh...")
            await self.async_request_refresh()
            _LOGGER.info("Task addition completed successfully")

            add_entities = self._platform_add_entities.get("sensor")
            if add_entities is not None:
                try:
                    from ..sensor import TaskSensor
                    add_entities([TaskSensor(self, task.id)])
                    _LOGGER.debug("Task sensor created dynamically: %s", task.id[:8])
                except Exception as e:
                    _LOGGER.warning("Could not create task sensor dynamically: %s", e)
        except Exception as e:
            _LOGGER.error("Failed to add task %s: %s", task.name, e)
            raise UpdateFailed(f"Error communicating with API: {e}") from e

    async def async_remove_task(self, task_id: str) -> None:
        """Remove a task."""
        if task_id in self.tasks:
            # Remove task data
            del self.tasks[task_id]

            # Remove task entities from registry
            try:
                from homeassistant.helpers import entity_registry
                er = entity_registry.async_get(self.hass)

                # Find all entities related to this task
                entities_to_remove = []
                safe_task_id = task_id.replace("-", "_")

                for entity_id, entity_entry in er.entities.items():
                    # Look for task sensor entities
                    if (entity_id.startswith(f'sensor.kidtasks_task_{safe_task_id}') and
                        entity_entry.config_entry_id == self.config_entry_id):
                        entities_to_remove.append(entity_id)

                # Remove the entities
                for entity_id in entities_to_remove:
                    er.async_remove(entity_id)
                    _LOGGER.info("Removed task entity: %s", entity_id)

                _LOGGER.info("Removed %d entities for task %s", len(entities_to_remove), task_id)

            except Exception as e:
                _LOGGER.error("Failed to remove task entities for task %s: %s", task_id, e)

            await self.async_save_data()
            await self.async_request_refresh()

    async def async_complete_task(self, task_id: str, child_id: str, validation_required: bool = None) -> bool:
        """Complete a task for a specific child."""
        if task_id not in self.tasks:
            return False

        # Vérifier que l'enfant existe et est assigné à cette tâche
        task = self.tasks[task_id]
        if child_id not in self.children:
            _LOGGER.error("Child %s does not exist", child_id)
            return False

        if child_id not in task.assigned_child_ids:
            _LOGGER.error("Child %s is not assigned to task %s", child_id, task_id)
            return False


        old_status = task.get_status_for_child(child_id)
        new_status = task.complete_for_child(child_id, validation_required)

        # Fire notification event if task needs validation
        if new_status == "pending_validation":
            child = self.children.get(child_id)
            self.hass.bus.async_fire(
                f"{DOMAIN}_task_pending_validation",
                {
                    "task_id": task_id,
                    "task_name": task.name,
                    "child_id": child.id if child else child_id,
                    "child_name": child.name if child else "Unknown",
                    "points": task.points,
                    "coins": task.coins,
                }
            )

            # Send Home Assistant notification if enabled
            if self.config_entry and self.config_entry.data.get("notifications_enabled", True):
                await self._send_validation_notification(task, child)

        if new_status == "validated":
            # Award points and coins only to the child who completed the task
            child = self.children.get(child_id)
            if child:
                # Add points with tracking
                level_up = False
                if task.points > 0:
                    level_up = child.add_points(
                        task.points,
                        description=f"Tâche '{task.name}' terminée",
                        action_type="task_completed",
                        related_entity_id=task.id,
                        related_entity_name=task.name
                    )
                # Add coins (no tracking for coins yet)
                if task.coins > 0:
                    child.add_coins(task.coins)

                # Fire events
                self.hass.bus.async_fire(
                    f"{DOMAIN}_task_completed",
                    {
                        "task_id": task_id,
                        "child_id": child.id,
                        "points_awarded": task.points,
                        "coins_awarded": task.coins,
                    }
                )

                if level_up:
                    self.hass.bus.async_fire(
                        f"{DOMAIN}_level_up",
                        {
                            "child_id": child.id,
                            "new_level": child.level,
                        }
                    )

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_validate_task(self, task_id: str) -> bool:
        """Validate a pending task for all children who completed it."""
        _LOGGER.info("DEBUG VALIDATION: Starting validation for task %s", task_id)

        if task_id not in self.tasks:
            _LOGGER.error("DEBUG VALIDATION: Task %s not found", task_id)
            return False

        task = self.tasks[task_id]
        validated_any = False

        _LOGGER.info("DEBUG VALIDATION: Task %s has child_statuses: %s", task_id, list(task.child_statuses.keys()))
        _LOGGER.info("DEBUG VALIDATION: Global task status: %s", task.status)

        # Use new system with individual child statuses only
        for child_id, child_status in task.child_statuses.items():
            _LOGGER.info("DEBUG VALIDATION: Child %s has status: %s", child_id, child_status.status)
            if child_status.status == "pending_validation":
                _LOGGER.info("DEBUG VALIDATION: Validating for child %s", child_id)
                if task.validate_for_child(child_id):
                    validated_any = True
                    _LOGGER.info("DEBUG VALIDATION: Successfully validated for child %s", child_id)

                    # Award points and coins to the child who completed the task
                    child = self.children.get(child_id)
                    if child:
                        # Add points with tracking
                        level_up = False
                        if task.points > 0:
                            level_up = child.add_points(
                                task.points,
                                description=f"Tâche '{task.name}' validée",
                                action_type="task_validated",
                                related_entity_id=task.id,
                                related_entity_name=task.name
                            )
                        # Add coins (no tracking for coins yet)
                        if task.coins > 0:
                            child.add_coins(task.coins)

                        # Fire events
                        self.hass.bus.async_fire(
                            f"{DOMAIN}_task_validated",
                            {
                                "task_id": task_id,
                                "child_id": child.id,
                                "points_awarded": task.points,
                                "coins_awarded": task.coins,
                            }
                        )

                        if level_up:
                            self.hass.bus.async_fire(
                                f"{DOMAIN}_level_up",
                                {
                                    "child_id": child.id,
                                    "new_level": child.level,
                                }
                            )

        if validated_any:
            # Clear any persistent notification for this task
            try:
                await self.hass.services.async_call(
                    "persistent_notification",
                    "dismiss",
                    {
                        "notification_id": f"kids_tasks_validation_{task_id}",
                    }
                )
            except Exception as e:
                _LOGGER.debug("Could not dismiss notification (may not exist): %s", e)

            await self.async_save_data()
            await self.async_request_refresh()

        return validated_any

    async def async_add_reward(self, reward: Reward) -> None:
        """Add a new reward."""
        try:
            _LOGGER.info("Adding reward to coordinator: %s", reward.name)
            self.rewards[reward.id] = reward
            _LOGGER.info("Reward added to memory, saving data...")
            await self.async_save_data()
            _LOGGER.info("Data saved, requesting refresh...")
            await self.async_request_refresh()
            _LOGGER.info("Reward addition completed successfully")

            add_entities = self._platform_add_entities.get("sensor")
            if add_entities is not None:
                try:
                    from ..sensor import RewardSensor
                    add_entities([RewardSensor(self, reward.id)])
                    _LOGGER.debug("Reward sensor created dynamically: %s", reward.id[:8])
                except Exception as e:
                    _LOGGER.warning("Could not create reward sensor dynamically: %s", e)
        except Exception as e:
            _LOGGER.error("Failed to add reward %s: %s", reward.name, e)
            raise UpdateFailed(f"Error communicating with API: {e}") from e

    async def async_remove_reward(self, reward_id: str) -> None:
        """Remove a reward."""
        if reward_id in self.rewards:
            # Remove reward data
            del self.rewards[reward_id]

            # Remove reward entities from registry
            try:
                from homeassistant.helpers import entity_registry
                er = entity_registry.async_get(self.hass)

                # Find all entities related to this reward
                entities_to_remove = []
                safe_reward_id = reward_id.replace("-", "_")

                for entity_id, entity_entry in er.entities.items():
                    # Look for reward sensor entities
                    if (entity_id.startswith(f'sensor.kidtasks_reward_{safe_reward_id}') and
                        entity_entry.config_entry_id == self.config_entry_id):
                        entities_to_remove.append(entity_id)

                # Remove the entities
                for entity_id in entities_to_remove:
                    er.async_remove(entity_id)
                    _LOGGER.info("Removed reward entity: %s", entity_id)

                _LOGGER.info("Removed %d entities for reward %s", len(entities_to_remove), reward_id)

            except Exception as e:
                _LOGGER.error("Failed to remove reward entities for reward %s: %s", reward_id, e)

            await self.async_save_data()
            await self.async_request_refresh()

    async def async_claim_reward(self, reward_id: str, child_id: str) -> bool:
        """Claim a reward for a child."""
        if reward_id not in self.rewards or child_id not in self.children:
            return False

        reward = self.rewards[reward_id]
        child = self.children[child_id]

        if not reward.can_claim(child.points, child.coins):
            return False

        if not reward.claim():
            return False

        # Handle different reward types
        if reward.reward_type == "cosmetic":
            # For cosmetic rewards, add to collection instead of consuming currency
            cosmetic_type = reward.cosmetic_data.get("type") if reward.cosmetic_data else "avatar"
            cosmetic_id = reward.cosmetic_data.get("cosmetic_id", reward_id) if reward.cosmetic_data else reward_id
            child.add_cosmetic_item(cosmetic_id, cosmetic_type)
        else:
            # For real rewards, deduct currency and consume with tracking
            if reward.cost > 0:
                child.add_points(
                    -reward.cost,
                    description=f"Récompense '{reward.name}' achetée",
                    action_type="reward_claimed",
                    related_entity_id=reward.id,
                    related_entity_name=reward.name
                )
            if reward.coin_cost > 0:
                child.coins -= reward.coin_cost

        # Fire event
        self.hass.bus.async_fire(
            f"{DOMAIN}_reward_claimed",
            {
                "reward_id": reward_id,
                "child_id": child_id,
                "cost": reward.cost,
                "coin_cost": reward.coin_cost,
                "reward_type": reward.reward_type,
            }
        )

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_activate_cosmetic(self, child_id: str, cosmetic_type: str, reward_id: str) -> bool:
        """Activate a cosmetic item for a child."""
        if child_id not in self.children or reward_id not in self.rewards:
            return False

        child = self.children[child_id]
        reward = self.rewards[reward_id]

        # Check if it's a cosmetic reward
        if reward.reward_type != "cosmetic":
            return False

        # Activate the cosmetic
        success = child.activate_cosmetic(cosmetic_type, reward_id)

        if success:
            await self.async_save_data()
            await self.async_request_refresh()

        return success

    async def async_reject_task(self, task_id: str) -> bool:
        """Reject a task and reset it to todo for all assigned children."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Use the task's reset method to properly reset all child statuses
        task.reset()

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_add_points(self, child_id: str, points: int) -> bool:
        """Add bonus points to a child (legacy method)."""
        return await self.async_add_currency(child_id, points=points)

    async def async_add_currency(self, child_id: str, points: int = 0, coins: int = 0) -> bool:
        """Add points and/or coins to a child."""
        if child_id not in self.children:
            return False

        child = self.children[child_id]
        old_level = child.level
        level_up = False

        # Add points with tracking
        if points != 0:
            level_up = child.add_points(
                points,
                description=f"Ajustement manuel de {points} points",
                action_type="manual_adjustment"
            )

        # Add coins (no tracking for coins yet)
        if coins != 0:
            child.add_coins(coins)

        # Check for level up
        if level_up:
            self.hass.bus.async_fire(
                f"{DOMAIN}_level_up",
                {
                    "child_id": child_id,
                    "new_level": child.level,
                }
            )

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_add_coins(self, child_id: str, coins: int) -> bool:
        """Add bonus coins to a child."""
        return await self.async_add_currency(child_id, coins=coins)

    async def async_remove_points(self, child_id: str, points: int) -> bool:
        """Remove points from a child."""
        if child_id not in self.children:
            return False

        child = self.children[child_id]
        # Use add_points with negative value to track the removal
        child.add_points(
            -points,
            description=f"Retrait manuel de {points} points",
            action_type="manual_adjustment"
        )

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_remove_coins(self, child_id: str, coins: int) -> bool:
        """Remove coins from a child."""
        if child_id not in self.children:
            return False

        child = self.children[child_id]
        success = child.remove_coins(coins)

        if success:
            await self.async_save_data()
            await self.async_request_refresh()

        return success

    async def async_set_points(self, child_id: str, points: int, description: str = None) -> bool:
        """Set child's points to exact value."""
        if child_id not in self.children:
            return False

        child = self.children[child_id]
        old_level = child.level

        # Set points with tracking
        level_up = child.set_points(
            points,
            description=description or f"Points définis à {points}",
            action_type="set_value"
        )

        # Fire level up event if needed
        if level_up:
            self.hass.bus.async_fire(
                f"{DOMAIN}_level_up",
                {
                    "child_id": child_id,
                    "child_name": child.name,
                    "old_level": old_level,
                    "new_level": child.level,
                    "new_points": child.points,
                },
            )

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_set_coins(self, child_id: str, coins: int) -> bool:
        """Set child's coins to exact value."""
        if child_id not in self.children:
            return False

        child = self.children[child_id]
        child.set_coins(coins)

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_set_level(self, child_id: str, level: int, description: str = None) -> bool:
        """Set child's level to exact value and recalculate points."""
        if child_id not in self.children:
            return False

        child = self.children[child_id]
        old_level = child.level

        # Set level with tracking
        child.set_level(
            level,
            description=description or f"Niveau défini à {level}",
            action_type="set_level"
        )

        # Fire level change event (could be up or down)
        if child.level != old_level:
            event_name = f"{DOMAIN}_level_up" if child.level > old_level else f"{DOMAIN}_level_change"
            self.hass.bus.async_fire(
                event_name,
                {
                    "child_id": child_id,
                    "child_name": child.name,
                    "old_level": old_level,
                    "new_level": child.level,
                    "new_points": child.points,
                },
            )

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_update_task(self, task_id: str, updates: dict) -> bool:
        """Update a task's information."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
            else:
                _LOGGER.warning("Task does not have attribute: %s", key)

        # If assigned_child_ids was updated, ensure all assigned children have child_statuses
        if "assigned_child_ids" in updates:
            from ..models import TaskChildStatus
            for child_id in task.assigned_child_ids:
                if child_id not in task.child_statuses:
                    task.child_statuses[child_id] = TaskChildStatus(child_id=child_id)

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_suspend_task(self, task_id: str, until_date: datetime | None = None) -> bool:
        """Suspend a task temporarily."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.suspend(until_date)

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_resume_task(self, task_id: str) -> bool:
        """Resume a suspended task."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.resume()

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_update_reward(self, reward_id: str, updates: dict) -> bool:
        """Update a reward's information."""
        if reward_id not in self.rewards:
            return False

        reward = self.rewards[reward_id]
        for key, value in updates.items():
            if hasattr(reward, key):
                setattr(reward, key, value)

        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_load_cosmetics_catalog(self) -> dict:
        """Load cosmetics catalog from files."""
        import os
        import json

        try:
            # Define cosmetics directory path
            cosmetics_dir = os.path.join(self.hass.config.config_dir, "custom_components", "kids_tasks", "cosmetics")

            catalog = {
                "avatars": [],
                "backgrounds": [],
                "outfits": [],
                "themes": []
            }

            # Load each cosmetic type
            for cosmetic_type in catalog.keys():
                type_dir = os.path.join(cosmetics_dir, cosmetic_type)
                if os.path.exists(type_dir):
                    # Load catalog.json for this type
                    catalog_file = os.path.join(type_dir, "catalog.json")
                    if os.path.exists(catalog_file):
                        # Use async file reading to avoid blocking the event loop
                        import asyncio
                        def read_catalog_file(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                return json.load(f)

                        # Execute file reading in thread pool to avoid blocking
                        type_catalog = await self.hass.async_add_executor_job(read_catalog_file, catalog_file)
                        catalog[cosmetic_type] = type_catalog.get("items", [])
                        _LOGGER.info("Loaded %d %s from catalog", len(catalog[cosmetic_type]), cosmetic_type)

            # Fire event with loaded catalog
            self.hass.bus.async_fire(
                f"{DOMAIN}_cosmetics_loaded",
                {
                    "catalog": catalog,
                    "total_items": sum(len(items) for items in catalog.values())
                }
            )

            _LOGGER.info("Cosmetics catalog loaded successfully: %d total items", sum(len(items) for items in catalog.values()))
            return catalog

        except Exception as e:
            _LOGGER.error("Failed to load cosmetics catalog: %s", e)
            return {"avatars": [], "backgrounds": [], "outfits": [], "themes": []}

    async def async_activate_cosmetic(self, child_id: str, cosmetic_id: str, cosmetic_type: str) -> bool:
        """Activate a cosmetic item for a child."""
        if child_id not in self.children:
            _LOGGER.error("Child %s not found", child_id)
            return False

        child = self.children[child_id]

        # Check if child owns this cosmetic (from rewards or default)
        if not self._child_owns_cosmetic(child, cosmetic_id, cosmetic_type):
            _LOGGER.error("Child %s does not own cosmetic %s of type %s", child_id, cosmetic_id, cosmetic_type)
            return False

        # Activate the cosmetic
        if not hasattr(child, 'active_cosmetics'):
            child.active_cosmetics = {}

        child.active_cosmetics[cosmetic_type] = cosmetic_id

        # Fire event
        self.hass.bus.async_fire(
            f"{DOMAIN}_cosmetic_activated",
            {
                "child_id": child_id,
                "child_name": child.name,
                "cosmetic_id": cosmetic_id,
                "cosmetic_type": cosmetic_type,
            }
        )

        await self.async_save_data()
        await self.async_request_refresh()

        _LOGGER.info("Activated %s cosmetic %s for child %s", cosmetic_type, cosmetic_id, child.name)
        return True

    def _child_owns_cosmetic(self, child, cosmetic_id: str, cosmetic_type: str) -> bool:
        """Check if a child owns a specific cosmetic item."""
        # Check if it's a default cosmetic (starts with "default_")
        if cosmetic_id.startswith("default_"):
            return True

        # Check if child has this cosmetic in their organized collection
        if hasattr(child, 'cosmetic_collection') and child.cosmetic_collection:
            type_collection = child.cosmetic_collection.get(cosmetic_type, [])
            if cosmetic_id in type_collection:
                return True

        # Fallback: check legacy cosmetic_items list
        if hasattr(child, 'cosmetic_items') and child.cosmetic_items:
            if cosmetic_id in child.cosmetic_items:
                return True

        return False

    async def async_create_cosmetic_rewards_from_catalog(self) -> int:
        """Create cosmetic rewards from the catalog for items that don't have rewards yet."""
        catalog = await self.async_load_cosmetics_catalog()
        created_count = 0

        from ..models import Reward
        import uuid

        for cosmetic_type, items in catalog.items():
            for item in items:
                # Skip default items
                if item.get("unlocked_by_default", False):
                    continue

                cosmetic_id = item.get("id")
                if not cosmetic_id:
                    continue

                # Check if a reward already exists for this cosmetic
                existing_reward = None
                for reward in self.rewards.values():
                    if (reward.reward_type == "cosmetic" and
                        reward.cosmetic_data and
                        reward.cosmetic_data.get("cosmetic_id") == cosmetic_id):
                        existing_reward = reward
                        break

                if existing_reward:
                    continue  # Skip if reward already exists

                # Create new cosmetic reward
                reward_id = str(uuid.uuid4())
                reward = Reward(
                    id=reward_id,
                    name=item.get("name", f"Cosmétique {cosmetic_id}"),
                    description=item.get("description", f"Débloque le cosmétique {item.get('name', cosmetic_id)}"),
                    cost=item.get("cost", 100),
                    coin_cost=item.get("coin_cost", 0),
                    category="cosmetic",
                    icon="🎨",  # Default cosmetic icon
                    reward_type="cosmetic",
                    cosmetic_data={
                        "type": cosmetic_type,
                        "cosmetic_id": cosmetic_id,
                        "rarity": item.get("rarity", "common"),
                        "catalog_data": item
                    }
                )

                self.rewards[reward_id] = reward
                created_count += 1
                _LOGGER.info("Created cosmetic reward for %s: %s", cosmetic_type, item.get("name", cosmetic_id))

        if created_count > 0:
            await self.async_save_data()
            await self.async_request_refresh()

            # Fire event
            self.hass.bus.async_fire(
                f"{DOMAIN}_cosmetic_rewards_created",
                {
                    "count": created_count,
                    "catalog_items": sum(len(items) for items in catalog.values())
                }
            )

        _LOGGER.info("Created %d cosmetic rewards from catalog", created_count)
        return created_count

    async def async_get_child_history(
        self,
        child_id: str,
        limit: int = 20,
        since_date: str | None = None,
        action_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get child points history with optional filtering."""
        try:
            # Verify child exists
            if child_id not in self.children:
                available_children = list(self.children.keys())
                _LOGGER.error(
                    "Child with ID %s does not exist. Available children: %s",
                    child_id, available_children
                )
                raise ValueError(f"Child with ID {child_id} does not exist")

            child = self.children[child_id]
            points_history = child.points_history or []

            # Apply date filter if provided
            if since_date:
                try:
                    since_datetime = datetime.fromisoformat(since_date)
                    filtered_history = []
                    for entry in points_history:
                        if hasattr(entry, 'timestamp') and entry.timestamp:
                            if entry.timestamp >= since_datetime:
                                filtered_history.append(entry)
                    points_history = filtered_history
                except ValueError:
                    _LOGGER.warning("Invalid date format for since_date: %s", since_date)

            # Apply action type filter if provided
            if action_type:
                points_history = [
                    entry for entry in points_history
                    if hasattr(entry, 'action_type') and entry.action_type == action_type
                ]

            # Limit results
            limited_history = points_history[:limit]

            # Format for response
            formatted_history = []
            for entry in limited_history:
                # Use to_dict() method if available, or access attributes directly
                if hasattr(entry, 'to_dict'):
                    formatted_entry = entry.to_dict()
                else:
                    formatted_entry = {
                        "timestamp": entry.timestamp.isoformat() if hasattr(entry, 'timestamp') and entry.timestamp else "",
                        "action_type": getattr(entry, 'action_type', 'unknown'),
                        "points_delta": getattr(entry, 'points_delta', 0),
                        "description": getattr(entry, 'description', ''),
                        "related_entity_name": getattr(entry, 'related_entity_name', None),
                    }
                formatted_history.append(formatted_entry)

            _LOGGER.info(
                "Retrieved %d history entries for child %s (out of %d total)",
                len(formatted_history), child_id, len(child.points_history or [])
            )

            return formatted_history

        except Exception as e:
            _LOGGER.error("Failed to get child history for %s: %s", child_id, e)
            raise

    async def _async_force_remove_child_entities(self, child_id: str) -> None:
        """Force remove all entities associated with a child."""
        try:
            from homeassistant.helpers import entity_registry

            # Get entity registry
            er = entity_registry.async_get(self.hass)

            # Find all entities related to this child
            entities_to_remove = []

            for entity_id, entity_entry in er.entities.items():
                # Check if entity belongs to our domain and is related to this child
                if (entity_entry.domain == DOMAIN and
                    entity_entry.unique_id and
                    child_id in entity_entry.unique_id):
                    entities_to_remove.append(entity_id)

            # Remove the entities
            for entity_id in entities_to_remove:
                er.async_remove(entity_id)

            _LOGGER.info("Force removed %d entities for child %s", len(entities_to_remove), child_id)

        except Exception as e:
            _LOGGER.error("Failed to force remove entities for child %s: %s", child_id, e)
