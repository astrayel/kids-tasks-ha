# ============================================================================
# config_flow.py
# ============================================================================

"""Config flow for Kids Tasks integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, CATEGORIES, FREQUENCIES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default="Kids Tasks"): str,
        vol.Optional("validation_required", default=True): bool,
        vol.Optional("notifications_enabled", default=True): bool,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kids Tasks."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{user_input['name']}")
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod 
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return KidsTasksOptionsFlow(config_entry)


class KidsTasksOptionsFlow(config_entries.OptionsFlow):
    """Handle Kids Tasks options."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_main_menu()

    async def async_step_main_menu(self, user_input=None):
        """Show main menu."""
        if user_input is not None:
            if user_input["action"] == "add_task":
                return await self.async_step_add_task()
            elif user_input["action"] == "add_child":
                return await self.async_step_add_child()
            elif user_input["action"] == "add_reward":
                return await self.async_step_add_reward()

        return self.async_show_form(
            step_id="main_menu",
            data_schema=vol.Schema({
                vol.Required("action"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "add_task", "label": "Add Task"},
                            {"value": "add_child", "label": "Add Child"},
                            {"value": "add_reward", "label": "Add Reward"},
                        ],
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }),
        )

    async def async_step_add_task(self, user_input=None):
        """Add a new task through options flow."""
        errors = {}

        if user_input is not None:
            # Get coordinator to add the task
            coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]["coordinator"]
            
            try:
                import uuid
                from .models import Task
                
                task_id = str(uuid.uuid4())
                task = Task(
                    id=task_id,
                    name=user_input["name"],
                    description=user_input.get("description", ""),
                    category=user_input.get("category", "other"),
                    points=user_input.get("points", 10),
                    frequency=user_input.get("frequency", "daily"),
                    assigned_child_id=user_input.get("assigned_child_id"),
                    validation_required=user_input.get("validation_required", True),
                )
                await coordinator.async_add_task(task)
                
                return self.async_create_entry(title="", data={})
                
            except Exception as e:
                _LOGGER.error("Error adding task: %s", e)
                errors["base"] = "unknown"

        # Get list of children for selection
        coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]["coordinator"]
        children_options = [{"value": "", "label": "Unassigned"}]
        for child_id, child in coordinator.children.items():
            children_options.append({
                "value": child_id,
                "label": child.name
            })

        return self.async_show_form(
            step_id="add_task",
            data_schema=vol.Schema({
                vol.Required("name"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional("description"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                        multiline=True,
                    )
                ),
                vol.Optional("category", default="other"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": cat, "label": cat.title()} 
                            for cat in CATEGORIES
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("points", default=10): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=100,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional("frequency", default="daily"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": freq, "label": freq.title()}
                            for freq in FREQUENCIES
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("assigned_child_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=children_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("validation_required", default=True): selector.BooleanSelector(),
            }),
            errors=errors,
        )

    async def async_step_add_child(self, user_input=None):
        """Add a new child through options flow."""
        errors = {}

        if user_input is not None:
            try:
                import uuid
                from .models import Child
                
                coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]["coordinator"]
                
                child_id = str(uuid.uuid4())
                child = Child(
                    id=child_id,
                    name=user_input["name"],
                    avatar=user_input.get("avatar"),
                    points=user_input.get("initial_points", 0),
                )
                await coordinator.async_add_child(child)
                
                return self.async_create_entry(title="", data={})
                
            except Exception as e:
                _LOGGER.error("Error adding child: %s", e)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="add_child",
            data_schema=vol.Schema({
                vol.Required("name"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional("avatar"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional("initial_points", default=0): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=1000,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }),
            errors=errors,
        )

    async def async_step_add_reward(self, user_input=None):
        """Add a new reward through options flow."""
        errors = {}

        if user_input is not None:
            try:
                import uuid
                from .models import Reward
                
                coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]["coordinator"]
                
                reward_id = str(uuid.uuid4())
                reward = Reward(
                    id=reward_id,
                    name=user_input["name"],
                    description=user_input.get("description", ""),
                    cost=user_input.get("cost", 50),
                    category=user_input.get("category", "fun"),
                    limited_quantity=user_input.get("limited_quantity"),
                    remaining_quantity=user_input.get("limited_quantity"),
                )
                await coordinator.async_add_reward(reward)
                
                return self.async_create_entry(title="", data={})
                
            except Exception as e:
                _LOGGER.error("Error adding reward: %s", e)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="add_reward",
            data_schema=vol.Schema({
                vol.Required("name"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional("description"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                        multiline=True,
                    )
                ),
                vol.Optional("cost", default=50): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=1000,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional("category", default="fun"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "fun", "label": "Fun"},
                            {"value": "screen_time", "label": "Screen Time2"},
                            {"value": "outing", "label": "Outing"},
                            {"value": "treat", "label": "Treat"},
                            {"value": "privilege", "label": "Privilege"},
                            {"value": "toy", "label": "Toy"},
                            {"value": "other", "label": "Other"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("limited_quantity"): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=100,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }),
            errors=errors,
        )