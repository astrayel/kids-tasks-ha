"""Tests for the four-regime access control."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from homeassistant.exceptions import ServiceValidationError

from custom_components.kids_tasks.models import Child
from custom_components.kids_tasks.permissions import (
    CONF_KIOSK_USERS,
    REGIME_CHILD,
    REGIME_GUEST,
    REGIME_INTERNAL,
    REGIME_KIOSK,
    REGIME_PARENT,
    Permissions,
    build_registrar,
)

PARENT_USER = "user-parent"
LEO_USER = "user-leo"
KIOSK_USER = "user-tablet"
STRANGER_USER = "user-stranger"


def _call(data: dict | None = None, user_id: str | None = None) -> MagicMock:
    call = MagicMock()
    call.data = data or {}
    call.context.user_id = user_id
    return call


@pytest.fixture
def perms(mock_hass):
    """Permissions over a family of two children, one of whom has an account."""
    coordinator = MagicMock()
    coordinator.children = {
        "leo": Child(id="leo", name="Léo", person_entity_id="person.leo"),
        "emma": Child(id="emma", name="Emma", person_entity_id="person.emma"),
        "nina": Child(id="nina", name="Nina"),  # no account at all
    }
    coordinator.config_entry.options = {CONF_KIOSK_USERS: [KIOSK_USER]}
    coordinator.config_entry.data = {}

    # person.leo points at Léo's account; person.emma has no user linked yet.
    states = {
        "person.leo": MagicMock(attributes={"user_id": LEO_USER}),
        "person.emma": MagicMock(attributes={}),
    }
    mock_hass.states.get = lambda entity_id: states.get(entity_id)

    def _user(user_id):
        if user_id == PARENT_USER:
            return MagicMock(is_admin=True)
        if user_id in (LEO_USER, KIOSK_USER, STRANGER_USER):
            return MagicMock(is_admin=False)
        return None

    mock_hass.auth.async_get_user = AsyncMock(side_effect=_user)
    return Permissions(mock_hass, coordinator)


# ---------------------------------------------------------------------------
# Regime resolution
# ---------------------------------------------------------------------------

class TestResolve:
    async def test_no_user_is_internal(self, perms):
        assert await perms.async_resolve(_call()) == (REGIME_INTERNAL, None)

    async def test_admin_is_parent(self, perms):
        assert await perms.async_resolve(_call(user_id=PARENT_USER)) == (REGIME_PARENT, None)

    async def test_linked_account_is_that_child(self, perms):
        assert await perms.async_resolve(_call(user_id=LEO_USER)) == (REGIME_CHILD, "leo")

    async def test_configured_account_is_kiosk(self, perms):
        assert await perms.async_resolve(_call(user_id=KIOSK_USER)) == (REGIME_KIOSK, None)

    async def test_unknown_account_is_guest(self, perms):
        assert await perms.async_resolve(_call(user_id=STRANGER_USER)) == (REGIME_GUEST, None)

    async def test_deleted_user_is_guest(self, perms):
        assert await perms.async_resolve(_call(user_id="ghost")) == (REGIME_GUEST, None)

    async def test_kiosk_wins_over_child_link(self, perms, mock_hass):
        """A shared device account is never mistaken for one child."""
        perms.coordinator.config_entry.options = {CONF_KIOSK_USERS: [LEO_USER]}
        regime, child_id = await perms.async_resolve(_call(user_id=LEO_USER))
        assert (regime, child_id) == (REGIME_KIOSK, None)


# ---------------------------------------------------------------------------
# Parent
# ---------------------------------------------------------------------------

class TestParent:
    @pytest.mark.parametrize(
        "service", ["validate_task", "set_points", "remove_child", "clear_all_data"]
    )
    async def test_may_do_anything(self, perms, service):
        await perms.async_check(_call(user_id=PARENT_USER), service)


# ---------------------------------------------------------------------------
# Child
# ---------------------------------------------------------------------------

class TestChild:
    async def test_may_complete_own_task(self, perms):
        await perms.async_check(
            _call({"task_id": "t1", "child_id": "leo"}, LEO_USER), "complete_task"
        )

    async def test_may_claim_own_reward(self, perms):
        await perms.async_check(
            _call({"reward_id": "r1", "child_id": "leo"}, LEO_USER), "claim_reward"
        )

    async def test_may_not_complete_a_siblings_task(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"task_id": "t1", "child_id": "emma"}, LEO_USER), "complete_task"
            )

    async def test_may_not_validate(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"task_id": "t1"}, LEO_USER), "validate_task"
            )

    async def test_may_not_reject(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(_call({"task_id": "t1"}, LEO_USER), "reject_task")

    async def test_may_not_grant_themselves_points(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"child_id": "leo", "points": 500}, LEO_USER), "set_points"
            )

    async def test_may_not_edit_tasks(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(_call({"task_id": "t1"}, LEO_USER), "update_task")

    async def test_may_read_own_history(self, perms):
        await perms.async_check(
            _call({"child_id": "leo"}, LEO_USER), "get_child_history"
        )

    async def test_may_not_read_a_siblings_history(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"child_id": "emma"}, LEO_USER), "get_child_history"
            )


# ---------------------------------------------------------------------------
# Kiosk — the shared tablet
# ---------------------------------------------------------------------------

class TestKiosk:
    @pytest.mark.parametrize("child_id", ["leo", "emma", "nina"])
    async def test_may_complete_for_any_child(self, perms, child_id):
        await perms.async_check(
            _call({"task_id": "t1", "child_id": child_id}, KIOSK_USER), "complete_task"
        )

    async def test_may_claim_for_any_child(self, perms):
        await perms.async_check(
            _call({"reward_id": "r1", "child_id": "nina"}, KIOSK_USER), "claim_reward"
        )

    async def test_may_equip_a_cosmetic(self, perms):
        await perms.async_check(
            _call(
                {"child_id": "nina", "cosmetic_id": "crown", "cosmetic_type": "outfit"},
                KIOSK_USER,
            ),
            "activate_cosmetic",
        )

    async def test_may_not_validate(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"task_id": "t1", "child_id": "leo"}, KIOSK_USER), "validate_task"
            )

    async def test_may_not_move_points(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"child_id": "leo", "points": 100}, KIOSK_USER), "add_points"
            )

    async def test_may_not_clear_data(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(_call({}, KIOSK_USER), "clear_all_data")


# ---------------------------------------------------------------------------
# Guest
# ---------------------------------------------------------------------------

class TestGuest:
    async def test_may_list(self, perms):
        await perms.async_check(_call({}, STRANGER_USER), "list_tasks")

    async def test_may_not_complete(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(
                _call({"task_id": "t1", "child_id": "leo"}, STRANGER_USER),
                "complete_task",
            )

    async def test_may_not_validate(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(_call({"task_id": "t1"}, STRANGER_USER), "validate_task")


# ---------------------------------------------------------------------------
# Default-deny: an unlisted service is admin-only, not wide open
# ---------------------------------------------------------------------------

class TestDefaultDeny:
    async def test_unknown_service_is_denied_for_child(self, perms):
        with pytest.raises(ServiceValidationError):
            await perms.async_check(_call({}, LEO_USER), "some_future_service")

    async def test_unknown_service_is_allowed_for_parent(self, perms):
        await perms.async_check(_call({}, PARENT_USER), "some_future_service")


# ---------------------------------------------------------------------------
# Registrar wiring
# ---------------------------------------------------------------------------

class TestRegistrar:
    async def test_registered_handler_runs_when_allowed(self, mock_hass, perms):
        register = build_registrar(mock_hass, perms.coordinator)
        handler = AsyncMock()
        register("list_tasks", handler)

        guarded = mock_hass.services.async_register.call_args[0][2]
        await guarded(_call({}, STRANGER_USER))
        handler.assert_awaited_once()

    async def test_registered_handler_is_blocked_when_denied(self, mock_hass, perms):
        register = build_registrar(mock_hass, perms.coordinator)
        handler = AsyncMock()
        register("validate_task", handler)

        guarded = mock_hass.services.async_register.call_args[0][2]
        with pytest.raises(ServiceValidationError):
            await guarded(_call({"task_id": "t1"}, LEO_USER))
        handler.assert_not_awaited()

    async def test_schema_is_passed_through(self, mock_hass, perms):
        register = build_registrar(mock_hass, perms.coordinator)
        sentinel = object()
        register("complete_task", AsyncMock(), schema=sentinel)
        assert mock_hass.services.async_register.call_args.kwargs["schema"] is sentinel
