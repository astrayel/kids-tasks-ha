# ============================================================================
# coordinator.py
# ============================================================================

"""Data update coordinator for Kids Tasks integration."""
from __future__ import annotations

import logging
from datetime import timedelta
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

    async def async_update_child(self, child: Child) -> None:
        """Update a child."""
        if child.id in self.children:
            self.children[child.id] = child
            await self.async_save_data()
            await self.async_request_refresh()

    async def async_remove_child(self, child_id: str) -> None:
        """Remove a child."""
        if child_id in self.children:
            del self.children[child_id]
            await self.async_save_data()
            await self.async_request_refresh()

    # Task management methods
    async def async_add_task(self, task: Task) -> None:
        """Add a new task."""
        self.tasks[task.id] = task
        await self.async_save_data()
        await self.async_request_refresh()

    async def async_update_task(self, task: Task) -> None:
        """Update a task."""
        if task.id in self.tasks:
            self.tasks[task.id] = task
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