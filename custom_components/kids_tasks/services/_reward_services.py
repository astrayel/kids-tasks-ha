"""Reward-related services for Kids Tasks."""
from __future__ import annotations

import json
import uuid
import logging
from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from ..const import DOMAIN
from ..models import Reward

if TYPE_CHECKING:
    from ..coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_REWARD = "add_reward"
SERVICE_CLAIM_REWARD = "claim_reward"
SERVICE_UPDATE_REWARD = "update_reward"
SERVICE_REMOVE_REWARD = "remove_reward"

SERVICE_ADD_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("cost", default=0): vol.Coerce(int),
        vol.Optional("coin_cost", default=0): vol.Coerce(int),
        vol.Optional("category", default="fun"): cv.string,
        vol.Optional("icon"): vol.Any(cv.string, None),
        vol.Optional("limited_quantity"): vol.Any(vol.Coerce(int), None),
        vol.Optional("reward_type", default="real"): vol.In(["real", "cosmetic"]),
        vol.Optional("cosmetic_data"): vol.Any(dict, cv.string, None),
    }
)

SERVICE_CLAIM_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("reward_id"): cv.string,
        vol.Required("child_id"): cv.string,
    }
)

SERVICE_UPDATE_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("reward_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("cost"): vol.Coerce(int),
        vol.Optional("coin_cost"): vol.Coerce(int),
        vol.Optional("category"): cv.string,
        vol.Optional("icon"): vol.Any(cv.string, None),
        vol.Optional("limited_quantity"): vol.Any(vol.Coerce(int), None),
        vol.Optional("remaining_quantity"): vol.Any(vol.Coerce(int), None),
        vol.Optional("active"): cv.boolean,
    }
)

SERVICE_REMOVE_REWARD_SCHEMA = vol.Schema(
    {
        vol.Required("reward_id"): cv.string,
    }
)

SERVICE_LOAD_COSMETICS_SCHEMA = vol.Schema({})
SERVICE_CREATE_COSMETIC_REWARDS_SCHEMA = vol.Schema({})


def register_reward_services(
    hass: HomeAssistant,
    coordinator: KidsTasksDataUpdateCoordinator,
) -> None:
    """Register all reward-related services."""

    async def add_reward_service(call: ServiceCall) -> None:
        try:
            cosmetic_data = call.data.get("cosmetic_data")
            if cosmetic_data and isinstance(cosmetic_data, str):
                try:
                    cosmetic_data = json.loads(cosmetic_data)
                except json.JSONDecodeError:
                    _LOGGER.warning("Invalid JSON in cosmetic_data: %s", cosmetic_data)
                    cosmetic_data = None

            reward_id = str(uuid.uuid4())
            reward = Reward(
                id=reward_id,
                name=call.data["name"],
                description=call.data.get("description", ""),
                cost=call.data.get("cost", 0),
                coin_cost=call.data.get("coin_cost", 0),
                category=call.data.get("category", "fun"),
                icon=call.data.get("icon"),
                limited_quantity=call.data.get("limited_quantity"),
                remaining_quantity=call.data.get("limited_quantity"),
                reward_type=call.data.get("reward_type", "real"),
                cosmetic_data=cosmetic_data,
            )
            await coordinator.async_add_reward(reward)
            _LOGGER.info("Reward successfully added with ID: %s", reward_id)
        except Exception as e:
            _LOGGER.error("Failed to create reward: %s | data: %s", e, call.data)
            raise

    async def claim_reward_service(call: ServiceCall) -> None:
        await coordinator.async_claim_reward(call.data["reward_id"], call.data["child_id"])

    async def update_reward_service(call: ServiceCall) -> None:
        reward_id = call.data["reward_id"]
        updates = {k: v for k, v in call.data.items() if k != "reward_id"}
        await coordinator.async_update_reward(reward_id, updates)

    async def remove_reward_service(call: ServiceCall) -> None:
        await coordinator.async_remove_reward(call.data["reward_id"])

    async def load_cosmetics_catalog_service(call: ServiceCall) -> None:
        try:
            await coordinator.async_load_cosmetics_catalog()
            _LOGGER.info("Cosmetics catalog loaded successfully")
        except Exception as e:
            _LOGGER.error("Failed to load cosmetics catalog: %s", e)
            raise

    async def create_cosmetic_rewards_service(call: ServiceCall) -> None:
        try:
            created_count = await coordinator.async_create_cosmetic_rewards_from_catalog()
            _LOGGER.info("Created %d cosmetic rewards from catalog", created_count)
        except Exception as e:
            _LOGGER.error("Failed to create cosmetic rewards: %s", e)
            raise

    hass.services.async_register(DOMAIN, SERVICE_ADD_REWARD, add_reward_service, schema=SERVICE_ADD_REWARD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CLAIM_REWARD, claim_reward_service, schema=SERVICE_CLAIM_REWARD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_REWARD, update_reward_service, schema=SERVICE_UPDATE_REWARD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_REWARD, remove_reward_service, schema=SERVICE_REMOVE_REWARD_SCHEMA)
    hass.services.async_register(DOMAIN, "load_cosmetics_catalog", load_cosmetics_catalog_service, schema=SERVICE_LOAD_COSMETICS_SCHEMA)
    hass.services.async_register(DOMAIN, "create_cosmetic_rewards", create_cosmetic_rewards_service, schema=SERVICE_CREATE_COSMETIC_REWARDS_SCHEMA)
