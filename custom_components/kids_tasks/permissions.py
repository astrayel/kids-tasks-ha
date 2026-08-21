"""Access control for Kids Tasks services.

Four regimes, resolved from the Home Assistant user behind the service call:

``parent``  an administrator — may do anything.
``child``   a Home Assistant account linked to a child through that child's
            ``person_entity_id`` — may act, but only on their own profile.
``kiosk``   a shared device account listed in the ``kiosk_users`` option — may
            act on behalf of any child, because a tablet in the hallway cannot
            tell which child is standing in front of it. It can never validate,
            reject, or move points.
``guest``   anyone else — read-only.

The kiosk regime deliberately leaves one hole: a child could mark a sibling's
task as done from the shared tablet. Parental validation is the backstop, and
nothing that grants points or levels is reachable from that account.

Calls without a user (automations, scripts, blueprints) are treated as
internal and allowed: they are authored by someone with admin access already.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

if TYPE_CHECKING:
    from .coordinator import KidsTasksDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_KIOSK_USERS = "kiosk_users"

REGIME_PARENT = "parent"
REGIME_CHILD = "child"
REGIME_KIOSK = "kiosk"
REGIME_GUEST = "guest"
REGIME_INTERNAL = "internal"

# Services a non-admin may call. Everything not listed here is admin-only,
# so a service added later is locked down by default rather than wide open.
POLICY_CHILD_SCOPED = {
    "complete_task",
    "claim_reward",
    "activate_cosmetic",
    "get_child_history",
}

POLICY_PUBLIC = {
    "list_tasks",
    "list_children",
}


class Permissions:
    """Resolves who is calling and whether they may."""

    def __init__(
        self, hass: HomeAssistant, coordinator: KidsTasksDataUpdateCoordinator
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator

    # -- resolution ---------------------------------------------------------

    def _kiosk_user_ids(self) -> set[str]:
        """User IDs configured as shared devices."""
        entry = getattr(self.coordinator, "config_entry", None)
        if entry is None:
            return set()
        configured = entry.options.get(CONF_KIOSK_USERS) or entry.data.get(
            CONF_KIOSK_USERS, []
        )
        return set(configured or [])

    def child_id_for_user(self, user_id: str) -> str | None:
        """Return the child this Home Assistant user is, if any.

        The link goes child -> person entity -> user, so a child only needs a
        person entity pointing at their account for this to work.
        """
        for child_id, child in self.coordinator.children.items():
            if not child.person_entity_id:
                continue
            person = self.hass.states.get(child.person_entity_id)
            if person and person.attributes.get("user_id") == user_id:
                return child_id
        return None

    async def async_resolve(self, call: ServiceCall) -> tuple[str, str | None]:
        """Return ``(regime, child_id)`` for the caller of this service call."""
        user_id = call.context.user_id
        if user_id is None:
            return REGIME_INTERNAL, None

        user = await self.hass.auth.async_get_user(user_id)
        if user is None:
            return REGIME_GUEST, None
        if user.is_admin:
            return REGIME_PARENT, None
        if user_id in self._kiosk_user_ids():
            return REGIME_KIOSK, None

        child_id = self.child_id_for_user(user_id)
        if child_id is not None:
            return REGIME_CHILD, child_id
        return REGIME_GUEST, None

    # -- enforcement --------------------------------------------------------

    async def async_check(self, call: ServiceCall, service: str) -> None:
        """Raise ``ServiceValidationError`` when the caller may not run this.

        ServiceValidationError rather than Unauthorized because it carries a
        message the caller actually sees, instead of a bare "Unauthorized".
        """
        regime, own_child_id = await self.async_resolve(call)

        if regime in (REGIME_PARENT, REGIME_INTERNAL):
            return

        if service in POLICY_PUBLIC:
            return

        if service not in POLICY_CHILD_SCOPED:
            raise ServiceValidationError(
                f"kids_tasks.{service} is reserved for parents "
                f"(caller regime: {regime})"
            )

        # Child-scoped: a kiosk acts for anyone, a child only for themselves.
        if regime == REGIME_KIOSK:
            return

        if regime != REGIME_CHILD:
            raise ServiceValidationError(
                f"kids_tasks.{service} requires a linked child account "
                f"(caller regime: {regime})"
            )

        target_child_id = call.data.get("child_id")
        if target_child_id is not None and target_child_id != own_child_id:
            raise ServiceValidationError(
                f"kids_tasks.{service} may only be called for your own profile"
            )


def build_registrar(
    hass: HomeAssistant, coordinator: KidsTasksDataUpdateCoordinator
):
    """Return a ``register()`` that wraps every handler with the guard.

    Registering through this instead of ``hass.services.async_register``
    guarantees no service is ever exposed unguarded by accident.
    """
    permissions = Permissions(hass, coordinator)

    def register(service: str, handler, schema=None, supports_response=None):
        async def guarded(call: ServiceCall):
            await permissions.async_check(call, service)
            return await handler(call)

        kwargs = {}
        if schema is not None:
            kwargs["schema"] = schema
        if supports_response is not None:
            kwargs["supports_response"] = supports_response

        from .const import DOMAIN

        hass.services.async_register(DOMAIN, service, guarded, **kwargs)

    return register
