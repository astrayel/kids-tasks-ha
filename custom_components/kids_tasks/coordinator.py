# ============================================================================
# coordinator.py
# ============================================================================

"""Data update coordinator for Kids Tasks integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .models import Child, Task, Reward

_LOGGER = logging.getLogger(__name__)


class KidsTasksDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, store: Store) -> None:
        """Initialize."""
        self.store = store
        self.children: dict[str, Child] = {}
        self.tasks: dict[str, Task] = {}
        self.rewards: dict[str, Reward] = {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Load data from storage
            await self._load_data()
            
            # Return current state
            return {
                "children": {child_id: child.to_dict() for child_id, child in self.children.items()},
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "rewards": {reward_id: reward.to_dict() for reward_id, reward in self.rewards.items()},
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _load_data(self) -> None:
        """Load data from storage."""
        data = await self.store.async_load() or {}
        
        # Load children
        children_data = data.get("children", {})
        self.children = {
            child_id: Child.from_dict(child_data)
            for child_id, child_data in children_data.items()
        }
        
        # Load tasks
        tasks_data = data.get("tasks", {})
        self.tasks = {
            task_id: Task.from_dict(task_data)
            for task_id, task_data in tasks_data.items()
        }
        
        # Load rewards
        rewards_data = data.get("rewards", {})
        self.rewards = {
            reward_id: Reward.from_dict(reward_data)
            for reward_id, reward_data in rewards_data.items()
        }

    async def async_save_data(self) -> None:
        """Save data to storage."""
        data = {
            "children": {child_id: child.to_dict() for child_id, child in self.children.items()},
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "rewards": {reward_id: reward.to_dict() for reward_id, reward in self.rewards.items()},
        }
        await self.store.async_save(data)

    # Child management methods
    async def async_add_child(self, child: Child) -> None:
        """Add a new child."""
        self.children[child.id] = child
        await self.async_save_data()
        await self.async_request_refresh()
        
        # Trigger integration reload to add new child entities
        await self._async_reload_integration_for_new_child(child.id)

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
                             if task.assigned_child_id == child_id]
            for task_id in tasks_to_remove:
                del self.tasks[task_id]
            
            await self.async_save_data()
            await self.async_request_refresh()
            
            # Force remove entities if requested
            if force_remove_entities:
                await self._async_force_remove_child_entities(child_id)

    # Task management methods
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
        except Exception as e:
            _LOGGER.error("Failed to add task %s: %s", task.name, e)
            raise UpdateFailed(f"Error communicating with API: {e}") from e

    async def async_update_task(self, task_id: str, updates: dict) -> None:
        """Update a task with new values."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            await self.async_save_data()
            await self.async_request_refresh()

    async def async_remove_task(self, task_id: str) -> None:
        """Remove a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            await self.async_save_data()
            await self.async_request_refresh()

    async def async_complete_task(self, task_id: str, validation_required: bool = None) -> bool:
        """Complete a task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        old_status = task.status
        new_status = task.complete(validation_required)
        
        if new_status == "validated" and task.assigned_child_id:
            # Award points to child
            child = self.children.get(task.assigned_child_id)
            if child:
                level_up = child.add_points(task.points)
                
                # Fire events
                self.hass.bus.async_fire(
                    f"{DOMAIN}_task_completed",
                    {
                        "task_id": task_id,
                        "child_id": child.id,
                        "points_awarded": task.points,
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
        """Validate a pending task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if not task.validate():
            return False
        
        if task.assigned_child_id:
            # Award points to child
            child = self.children.get(task.assigned_child_id)
            if child:
                level_up = child.add_points(task.points)
                
                # Fire events
                self.hass.bus.async_fire(
                    f"{DOMAIN}_task_validated",
                    {
                        "task_id": task_id,
                        "child_id": child.id,
                        "points_awarded": task.points,
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

    # Reward management methods
    async def async_add_reward(self, reward: Reward) -> None:
        """Add a new reward."""
        self.rewards[reward.id] = reward
        await self.async_save_data()
        await self.async_request_refresh()

    async def async_remove_reward(self, reward_id: str) -> None:
        """Remove a reward."""
        if reward_id in self.rewards:
            del self.rewards[reward_id]
            await self.async_save_data()
            await self.async_request_refresh()

    async def async_claim_reward(self, reward_id: str, child_id: str) -> bool:
        """Claim a reward for a child."""
        if reward_id not in self.rewards or child_id not in self.children:
            return False
        
        reward = self.rewards[reward_id]
        child = self.children[child_id]
        
        if not reward.can_claim(child.points):
            return False
        
        if not reward.claim():
            return False
        
        # Deduct points from child
        child.points -= reward.cost
        child.level = max(1, (child.points // 100) + 1)
        
        # Fire event
        self.hass.bus.async_fire(
            f"{DOMAIN}_reward_claimed",
            {
                "reward_id": reward_id,
                "child_id": child_id,
                "cost": reward.cost,
            }
        )
        
        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_request_refresh(self) -> None:
        """Request a data refresh."""
        await self.async_refresh()

    async def async_clear_all_data(self) -> None:
        """Clear all data from storage."""
        _LOGGER.info("Clearing all data - children: %d, tasks: %d, rewards: %d", 
                    len(self.children), len(self.tasks), len(self.rewards))
        
        self.children.clear()
        self.tasks.clear() 
        self.rewards.clear()
        
        await self.async_save_data()
        
        # Force entity registry to reload
        await self.async_request_refresh()
        
        # Also fire event for potential UI updates
        self.hass.bus.async_fire(f"{DOMAIN}_data_cleared")
        
        _LOGGER.info("All data cleared and refresh requested")

    async def async_reject_task(self, task_id: str) -> bool:
        """Reject a task and reset it to todo."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = "todo"
        
        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_add_points(self, child_id: str, points: int) -> bool:
        """Add bonus points to a child."""
        if child_id not in self.children:
            return False
        
        child = self.children[child_id]
        old_level = child.level
        child.add_points(points)
        
        # Check for level up
        if child.level > old_level:
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

    async def async_remove_points(self, child_id: str, points: int) -> bool:
        """Remove points from a child."""
        if child_id not in self.children:
            return False
        
        child = self.children[child_id]
        child.points = max(0, child.points - points)
        child.level = max(1, (child.points // 100) + 1)
        
        await self.async_save_data()
        await self.async_request_refresh()
        return True

    async def async_update_child(self, child_id: str, updates: dict) -> bool:
        """Update a child's information."""
        if child_id not in self.children:
            return False
        
        child = self.children[child_id]
        for key, value in updates.items():
            if hasattr(child, key):
                setattr(child, key, value)
        
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

    async def async_reset_all_daily_tasks(self) -> None:
        """Reset all daily tasks to todo status."""
        for task in self.tasks.values():
            if task.frequency == "daily":
                task.status = "todo"
        
        await self.async_save_data()
        await self.async_request_refresh()

    async def async_backup_data(self, include_history: bool = True) -> str:
        """Create a backup of all data."""
        import json
        
        backup_data = {
            "version": 1,
            "timestamp": datetime.now().isoformat(),
            "children": {child_id: child.to_dict() for child_id, child in self.children.items()},
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "rewards": {reward_id: reward.to_dict() for reward_id, reward in self.rewards.items()},
        }
        
        return json.dumps(backup_data, indent=2)

    async def async_restore_data(self, backup_json: str) -> bool:
        """Restore data from a backup."""
        import json
        
        try:
            backup_data = json.loads(backup_json)
            
            # Clear existing data
            self.children.clear()
            self.tasks.clear()
            self.rewards.clear()
            
            # Restore children
            for child_id, child_data in backup_data.get("children", {}).items():
                self.children[child_id] = Child.from_dict(child_data)
            
            # Restore tasks
            for task_id, task_data in backup_data.get("tasks", {}).items():
                self.tasks[task_id] = Task.from_dict(task_data)
            
            # Restore rewards
            for reward_id, reward_data in backup_data.get("rewards", {}).items():
                self.rewards[reward_id] = Reward.from_dict(reward_data)
            
            await self.async_save_data()
            await self.async_request_refresh()
            return True
            
        except Exception as e:
            _LOGGER.error("Failed to restore backup: %s", e)
            return False
    
    async def _async_reload_integration_for_new_child(self, child_id: str) -> None:
        """Reload the integration to add entities for a new child."""
        try:
            # Get the config entry for this integration
            config_entries = [entry for entry in self.hass.config_entries.async_entries(DOMAIN)]
            if not config_entries:
                _LOGGER.error("No config entry found for %s", DOMAIN)
                return
            
            config_entry = config_entries[0]
            
            # Trigger integration reload
            await self.hass.config_entries.async_reload(config_entry.entry_id)
            _LOGGER.info("Integration reloaded to add entities for new child: %s", child_id)
                            
        except Exception as e:
            _LOGGER.error("Failed to reload integration for child %s: %s", child_id, e)

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
                    entity_entry.unique_id.startswith("KT_") and
                    child_id in entity_entry.unique_id):
                    entities_to_remove.append(entity_id)
            
            # Remove the entities
            for entity_id in entities_to_remove:
                er.async_remove(entity_id)
                
            _LOGGER.info("Force removed %d entities for child %s", len(entities_to_remove), child_id)
            
        except Exception as e:
            _LOGGER.error("Failed to force remove entities for child %s: %s", child_id, e)