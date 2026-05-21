"""Child-related services for Kids Tasks."""
from __future__ import annotations

import uuid
import logging
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from ..const import DOMAIN
from ..models import Child

if TYPE_CHECKING:
    from ..coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_CHILD = "add_child"
SERVICE_UPDATE_CHILD = "update_child"
SERVICE_REMOVE_CHILD = "remove_child"
SERVICE_ADD_POINTS = "add_points"
SERVICE_REMOVE_POINTS = "remove_points"
SERVICE_SET_POINTS = "set_points"
SERVICE_SET_COINS = "set_coins"
SERVICE_SET_LEVEL = "set_level"
SERVICE_ADD_CURRENCY = "add_currency"
SERVICE_ADD_COINS = "add_coins"
SERVICE_REMOVE_COINS = "remove_coins"
SERVICE_ACTIVATE_COSMETIC = "activate_cosmetic"
SERVICE_LIST_CHILDREN = "list_children"
SERVICE_GET_CHILD_HISTORY = "get_child_history"

SERVICE_ADD_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("avatar"): vol.Any(cv.string, None),
        vol.Optional("initial_points", default=0): vol.Coerce(int),
        vol.Optional("person_entity_id"): vol.Any(cv.string, None),
        vol.Optional("avatar_type", default="emoji"): vol.In(["emoji", "url", "inline", "person_entity"]),
        vol.Optional("avatar_data"): vol.Any(cv.string, None),
        vol.Optional("card_gradient_start"): vol.Any(cv.string, None),
        vol.Optional("card_gradient_end"): vol.Any(cv.string, None),
    }
)

SERVICE_UPDATE_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("avatar"): vol.Any(cv.string, None),
        vol.Optional("person_entity_id"): vol.Any(cv.string, None),
        vol.Optional("avatar_type"): vol.In(["emoji", "url", "inline", "person_entity"]),
        vol.Optional("avatar_data"): vol.Any(cv.string, None),
        vol.Optional("card_gradient_start"): vol.Any(cv.string, None),
        vol.Optional("card_gradient_end"): vol.Any(cv.string, None),
        vol.Optional("card_customizations"): vol.Any(dict, None),
    }
)

SERVICE_REMOVE_CHILD_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Optional("force_remove_entities", default=False): cv.boolean,
    }
)

SERVICE_ADD_POINTS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("points"): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_REMOVE_POINTS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("points"): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_SET_POINTS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("points"): vol.Coerce(int),
        vol.Optional("description"): cv.string,
    }
)

SERVICE_SET_COINS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("coins"): vol.Coerce(int),
    }
)

SERVICE_SET_LEVEL_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("level"): vol.Coerce(int),
        vol.Optional("description"): cv.string,
    }
)

SERVICE_ADD_CURRENCY_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Optional("points", default=0): vol.Coerce(int),
        vol.Optional("coins", default=0): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_ADD_COINS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("coins"): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_REMOVE_COINS_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("coins"): vol.Coerce(int),
        vol.Optional("reason"): cv.string,
    }
)

SERVICE_ACTIVATE_COSMETIC_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Required("cosmetic_id"): cv.string,
        vol.Required("cosmetic_type"): vol.In(["avatar", "background", "outfit", "theme"]),
    }
)

SERVICE_GET_CHILD_HISTORY_SCHEMA = vol.Schema(
    {
        vol.Required("child_id"): cv.string,
        vol.Optional("limit", default=20): vol.Coerce(int),
        vol.Optional("since_date"): cv.string,
        vol.Optional("action_type"): cv.string,
    }
)


def register_child_services(
    hass: HomeAssistant,
    coordinator: KidsTasksDataUpdateCoordinator,
) -> None:
    """Register all child-related services."""

    async def add_child_service(call: ServiceCall) -> None:
        child_id = str(uuid.uuid4())
        child = Child(
            id=child_id,
            name=call.data["name"],
            avatar=call.data.get("avatar"),
            points=call.data.get("initial_points", 0),
            person_entity_id=call.data.get("person_entity_id"),
            avatar_type=call.data.get("avatar_type", "emoji"),
            avatar_data=call.data.get("avatar_data"),
            card_gradient_start=call.data.get("card_gradient_start"),
            card_gradient_end=call.data.get("card_gradient_end"),
        )
        await coordinator.async_add_child(child)

    async def update_child_service(call: ServiceCall) -> None:
        child_id = call.data["child_id"]
        updates = {k: v for k, v in call.data.items() if k != "child_id"}
        await coordinator.async_update_child(child_id, updates)

    async def remove_child_service(call: ServiceCall) -> None:
        await coordinator.async_remove_child(
            call.data["child_id"],
            call.data.get("force_remove_entities", False),
        )

    async def add_points_service(call: ServiceCall) -> None:
        await coordinator.async_add_points(call.data["child_id"], call.data["points"])

    async def remove_points_service(call: ServiceCall) -> None:
        await coordinator.async_remove_points(call.data["child_id"], call.data["points"])

    async def set_points_service(call: ServiceCall) -> None:
        await coordinator.async_set_points(
            call.data["child_id"], call.data["points"], call.data.get("description")
        )

    async def set_coins_service(call: ServiceCall) -> None:
        await coordinator.async_set_coins(call.data["child_id"], call.data["coins"])

    async def set_level_service(call: ServiceCall) -> None:
        await coordinator.async_set_level(
            call.data["child_id"], call.data["level"], call.data.get("description")
        )

    async def add_currency_service(call: ServiceCall) -> None:
        await coordinator.async_add_currency(
            call.data["child_id"],
            call.data.get("points", 0),
            call.data.get("coins", 0),
        )

    async def add_coins_service(call: ServiceCall) -> None:
        await coordinator.async_add_coins(call.data["child_id"], call.data["coins"])

    async def remove_coins_service(call: ServiceCall) -> None:
        await coordinator.async_remove_coins(call.data["child_id"], call.data["coins"])

    async def activate_cosmetic_service(call: ServiceCall) -> None:
        await coordinator.async_activate_cosmetic(
            call.data["child_id"],
            call.data["cosmetic_id"],
            call.data["cosmetic_type"],
        )

    async def list_children_service(call: ServiceCall) -> None:
        try:
            children_list = []
            for child_id, child in coordinator.children.items():
                children_list.append({
                    "child_id": child_id,
                    "name": child.name,
                    "points": child.points,
                    "level": child.level,
                    "avatar": child.avatar,
                })
            _LOGGER.info("Children list retrieved: %d children found", len(children_list))
            for child in children_list:
                _LOGGER.info(
                    "Child: %s | ID: %s | Points: %d | Level: %d",
                    child["name"], child["child_id"], child["points"], child["level"],
                )
        except Exception as e:
            _LOGGER.error("Failed to list children: %s", e)
            raise

    async def get_child_history_service(call: ServiceCall) -> None:
        try:
            history = await coordinator.async_get_child_history(
                call.data["child_id"],
                call.data.get("limit", 20),
                call.data.get("since_date"),
                call.data.get("action_type"),
            )
            _LOGGER.info(
                "Retrieved history for child %s: %d entries",
                call.data["child_id"], len(history),
            )
            for entry in history:
                _LOGGER.info(
                    "History entry: %s - %s points (%s)",
                    entry.get("description", "Unknown action"),
                    entry.get("points_delta", 0),
                    entry.get("timestamp", "Unknown time"),
                )
        except Exception as e:
            _LOGGER.error("Failed to get child history: %s", e)
            raise

    hass.services.async_register(DOMAIN, SERVICE_ADD_CHILD, add_child_service, schema=SERVICE_ADD_CHILD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_CHILD, update_child_service, schema=SERVICE_UPDATE_CHILD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_CHILD, remove_child_service, schema=SERVICE_REMOVE_CHILD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ADD_POINTS, add_points_service, schema=SERVICE_ADD_POINTS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_POINTS, remove_points_service, schema=SERVICE_REMOVE_POINTS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_POINTS, set_points_service, schema=SERVICE_SET_POINTS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_COINS, set_coins_service, schema=SERVICE_SET_COINS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_LEVEL, set_level_service, schema=SERVICE_SET_LEVEL_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ADD_CURRENCY, add_currency_service, schema=SERVICE_ADD_CURRENCY_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ADD_COINS, add_coins_service, schema=SERVICE_ADD_COINS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_COINS, remove_coins_service, schema=SERVICE_REMOVE_COINS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ACTIVATE_COSMETIC, activate_cosmetic_service, schema=SERVICE_ACTIVATE_COSMETIC_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_LIST_CHILDREN, list_children_service)
    hass.services.async_register(DOMAIN, SERVICE_GET_CHILD_HISTORY, get_child_history_service, schema=SERVICE_GET_CHILD_HISTORY_SCHEMA)
