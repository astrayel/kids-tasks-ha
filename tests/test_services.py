"""Tests for Kids Tasks service handlers."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_call(data: dict) -> MagicMock:
    """Build a minimal ServiceCall-like mock with a data dict."""
    call_mock = MagicMock()
    call_mock.data = data
    return call_mock


def capture_handlers(mock_hass) -> dict[str, object]:
    """Return {service_name: handler} from all async_register calls."""
    handlers = {}
    for c in mock_hass.services.async_register.call_args_list:
        args = c[0]  # positional: (domain, service_name, handler[, schema])
        handlers[args[1]] = args[2]
    return handlers


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc_hass():
    """Fresh hass mock whose services.async_register captures handlers."""
    hass = MagicMock()
    hass.services.async_register = MagicMock()
    hass.services.async_services = MagicMock(return_value={})
    hass.bus.async_fire = MagicMock()
    return hass


@pytest.fixture
def svc_coordinator():
    """Coordinator with all async methods mocked."""
    coord = MagicMock()
    coord.children = {}
    coord.tasks = {}
    coord.rewards = {}
    coord.async_add_child = AsyncMock()
    coord.async_update_child = AsyncMock()
    coord.async_remove_child = AsyncMock()
    coord.async_add_points = AsyncMock(return_value=True)
    coord.async_remove_points = AsyncMock(return_value=True)
    coord.async_set_points = AsyncMock(return_value=True)
    coord.async_add_coins = AsyncMock(return_value=True)
    coord.async_remove_coins = AsyncMock(return_value=True)
    coord.async_set_coins = AsyncMock(return_value=True)
    coord.async_set_level = AsyncMock(return_value=True)
    coord.async_add_currency = AsyncMock(return_value=True)
    coord.async_add_task = AsyncMock()
    coord.async_update_task = AsyncMock(return_value=True)
    coord.async_remove_task = AsyncMock()
    coord.async_complete_task = AsyncMock(return_value=True)
    coord.async_validate_task = AsyncMock(return_value=True)
    coord.async_reject_task = AsyncMock()
    coord.async_suspend_task = AsyncMock(return_value=True)
    coord.async_resume_task = AsyncMock(return_value=True)
    coord.async_save_data = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    coord.async_add_reward = AsyncMock()
    coord.async_update_reward = AsyncMock(return_value=True)
    coord.async_remove_reward = AsyncMock()
    coord.async_claim_reward = AsyncMock(return_value=True)
    return coord


# ---------------------------------------------------------------------------
# Task services
# ---------------------------------------------------------------------------

class TestAddTaskService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._task_services import register_task_services
        register_task_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_creates_task_with_required_fields(self):
        await self.handlers["add_task"](make_call({"name": "Ranger chambre"}))
        self.coord.async_add_task.assert_awaited_once()
        task = self.coord.async_add_task.call_args[0][0]
        assert task.name == "Ranger chambre"
        assert task.frequency == "daily"
        assert task.points == 10
        assert task.validation_required is True

    async def test_creates_task_with_all_optional_fields(self):
        await self.handlers["add_task"](make_call({
            "name": "Devoirs",
            "description": "Maths",
            "category": "homework",
            "points": 20,
            "coins": 5,
            "frequency": "weekly",
            "validation_required": False,
            "penalty_points": 3,
            "deadline_time": "18:00",
        }))
        task = self.coord.async_add_task.call_args[0][0]
        assert task.description == "Maths"
        assert task.category == "homework"
        assert task.points == 20
        assert task.frequency == "weekly"
        assert task.validation_required is False
        assert task.penalty_points == 3
        assert task.deadline_time == "18:00"

    async def test_assigns_child_creates_child_status(self):
        from custom_components.kids_tasks.models import Child
        self.coord.children["c1"] = Child(id="c1", name="Leo")
        await self.handlers["add_task"](make_call({
            "name": "Vaisselle",
            "assigned_child_ids": ["c1"],
        }))
        task = self.coord.async_add_task.call_args[0][0]
        assert "c1" in task.assigned_child_ids
        assert "c1" in task.child_statuses

    async def test_raises_if_assigned_child_not_found(self):
        with pytest.raises(ValueError, match="c_unknown"):
            await self.handlers["add_task"](make_call({
                "name": "Tâche",
                "assigned_child_ids": ["c_unknown"],
            }))
        self.coord.async_add_task.assert_not_awaited()

    async def test_empty_assigned_child_ids_accepted(self):
        await self.handlers["add_task"](make_call({
            "name": "Tâche globale",
            "assigned_child_ids": [],
        }))
        task = self.coord.async_add_task.call_args[0][0]
        assert task.assigned_child_ids == []


class TestUpdateTaskService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._task_services import register_task_services
        from custom_components.kids_tasks.models import Task
        register_task_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator
        self.coord.tasks["t1"] = Task(id="t1", name="Ancienne tâche")

    async def test_calls_update_with_correct_fields(self):
        await self.handlers["update_task"](make_call({
            "task_id": "t1",
            "name": "Nouvelle tâche",
            "points": 25,
        }))
        self.coord.async_update_task.assert_awaited_once_with(
            "t1", {"name": "Nouvelle tâche", "points": 25}
        )

    async def test_raises_if_task_not_found(self):
        with pytest.raises(ValueError, match="t_unknown"):
            await self.handlers["update_task"](make_call({
                "task_id": "t_unknown",
                "name": "Inexistant",
            }))
        self.coord.async_update_task.assert_not_awaited()


class TestRemoveTaskService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._task_services import register_task_services
        register_task_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_calls_remove_with_task_id(self):
        await self.handlers["remove_task"](make_call({"task_id": "t1"}))
        self.coord.async_remove_task.assert_awaited_once_with("t1")


class TestResetTaskService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._task_services import register_task_services
        from custom_components.kids_tasks.models import Task
        register_task_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator
        task = Task(id="t1", name="Tâche")
        task.reset = MagicMock()
        self.coord.tasks["t1"] = task

    async def test_calls_reset_and_saves(self):
        await self.handlers["reset_task"](make_call({"task_id": "t1"}))
        self.coord.tasks["t1"].reset.assert_called_once()
        self.coord.async_save_data.assert_awaited_once()
        self.coord.async_request_refresh.assert_awaited_once()

    async def test_noop_if_task_not_found(self):
        await self.handlers["reset_task"](make_call({"task_id": "t_unknown"}))
        self.coord.async_save_data.assert_not_awaited()


class TestSuspendResumeTaskService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._task_services import register_task_services
        register_task_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_suspend_without_date(self):
        await self.handlers["suspend_task"](make_call({"task_id": "t1"}))
        self.coord.async_suspend_task.assert_awaited_once_with("t1", None)

    async def test_suspend_with_valid_date(self):
        await self.handlers["suspend_task"](make_call({
            "task_id": "t1",
            "until_date": "2025-12-31T00:00:00",
        }))
        args = self.coord.async_suspend_task.call_args[0]
        assert args[0] == "t1"
        assert args[1] is not None

    async def test_suspend_with_invalid_date_does_not_raise(self):
        # Handler logs error and returns — no exception bubbles
        await self.handlers["suspend_task"](make_call({
            "task_id": "t1",
            "until_date": "not-a-date",
        }))
        self.coord.async_suspend_task.assert_not_awaited()

    async def test_resume(self):
        await self.handlers["resume_task"](make_call({"task_id": "t1"}))
        self.coord.async_resume_task.assert_awaited_once_with("t1")


# ---------------------------------------------------------------------------
# Child services
# ---------------------------------------------------------------------------

class TestAddChildService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._child_services import register_child_services
        register_child_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_creates_child_with_name(self):
        await self.handlers["add_child"](make_call({"name": "Emma"}))
        self.coord.async_add_child.assert_awaited_once()
        child = self.coord.async_add_child.call_args[0][0]
        assert child.name == "Emma"
        assert child.points == 0

    async def test_creates_child_with_all_fields(self):
        await self.handlers["add_child"](make_call({
            "name": "Leo",
            "avatar": "🦁",
            "avatar_type": "emoji",
            "initial_points": 50,
            "card_gradient_start": "#ff0000",
            "card_gradient_end": "#0000ff",
        }))
        child = self.coord.async_add_child.call_args[0][0]
        assert child.name == "Leo"
        assert child.avatar == "🦁"
        assert child.points == 50
        assert child.card_gradient_start == "#ff0000"
        assert child.card_gradient_end == "#0000ff"

    async def test_child_id_is_uuid(self):
        await self.handlers["add_child"](make_call({"name": "Marie"}))
        child = self.coord.async_add_child.call_args[0][0]
        import uuid
        uuid.UUID(child.id)  # raises if not a valid UUID


class TestUpdateChildService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._child_services import register_child_services
        register_child_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_calls_update_without_child_id_key(self):
        await self.handlers["update_child"](make_call({
            "child_id": "c1",
            "name": "Emma modifiée",
            "avatar": "🌟",
        }))
        self.coord.async_update_child.assert_awaited_once_with(
            "c1", {"name": "Emma modifiée", "avatar": "🌟"}
        )


class TestRemoveChildService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._child_services import register_child_services
        register_child_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_calls_remove(self):
        await self.handlers["remove_child"](make_call({"child_id": "c1"}))
        self.coord.async_remove_child.assert_awaited_once_with("c1", False)

    async def test_calls_remove_with_force_flag(self):
        await self.handlers["remove_child"](make_call({
            "child_id": "c1",
            "force_remove_entities": True,
        }))
        self.coord.async_remove_child.assert_awaited_once_with("c1", True)


class TestPointsAndCoinsServices:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._child_services import register_child_services
        register_child_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_add_points(self):
        await self.handlers["add_points"](make_call({"child_id": "c1", "points": 30}))
        self.coord.async_add_points.assert_awaited_once_with("c1", 30)

    async def test_remove_points(self):
        await self.handlers["remove_points"](make_call({"child_id": "c1", "points": 10}))
        self.coord.async_remove_points.assert_awaited_once_with("c1", 10)

    async def test_set_points(self):
        await self.handlers["set_points"](make_call({
            "child_id": "c1", "points": 100, "description": "Bonus"
        }))
        self.coord.async_set_points.assert_awaited_once_with("c1", 100, "Bonus")

    async def test_add_coins(self):
        await self.handlers["add_coins"](make_call({"child_id": "c1", "coins": 5}))
        self.coord.async_add_coins.assert_awaited_once_with("c1", 5)

    async def test_remove_coins(self):
        await self.handlers["remove_coins"](make_call({"child_id": "c1", "coins": 3}))
        self.coord.async_remove_coins.assert_awaited_once_with("c1", 3)

    async def test_set_coins(self):
        await self.handlers["set_coins"](make_call({"child_id": "c1", "coins": 20}))
        self.coord.async_set_coins.assert_awaited_once_with("c1", 20)

    async def test_set_level(self):
        await self.handlers["set_level"](make_call({"child_id": "c1", "level": 5}))
        self.coord.async_set_level.assert_awaited_once_with("c1", 5, None)

    async def test_add_currency_points_and_coins(self):
        await self.handlers["add_currency"](make_call({
            "child_id": "c1", "points": 10, "coins": 2
        }))
        self.coord.async_add_currency.assert_awaited_once_with("c1", 10, 2)

    async def test_add_currency_defaults_to_zero(self):
        await self.handlers["add_currency"](make_call({"child_id": "c1"}))
        self.coord.async_add_currency.assert_awaited_once_with("c1", 0, 0)


# ---------------------------------------------------------------------------
# Reward services
# ---------------------------------------------------------------------------

class TestAddRewardService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._reward_services import register_reward_services
        register_reward_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_creates_reward_with_name(self):
        await self.handlers["add_reward"](make_call({"name": "Cinéma"}))
        self.coord.async_add_reward.assert_awaited_once()
        reward = self.coord.async_add_reward.call_args[0][0]
        assert reward.name == "Cinéma"
        assert reward.cost == 0
        assert reward.reward_type == "real"

    async def test_creates_reward_with_all_fields(self):
        await self.handlers["add_reward"](make_call({
            "name": "Glace",
            "description": "Une boule de glace",
            "cost": 50,
            "coin_cost": 2,
            "category": "treat",
            "limited_quantity": 3,
            "reward_type": "real",
        }))
        reward = self.coord.async_add_reward.call_args[0][0]
        assert reward.cost == 50
        assert reward.coin_cost == 2
        assert reward.limited_quantity == 3
        assert reward.remaining_quantity == 3  # initialized from limited_quantity

    async def test_reward_type_cosmetic(self):
        await self.handlers["add_reward"](make_call({
            "name": "Badge",
            "reward_type": "cosmetic",
        }))
        reward = self.coord.async_add_reward.call_args[0][0]
        assert reward.reward_type == "cosmetic"

    async def test_reward_id_is_uuid(self):
        await self.handlers["add_reward"](make_call({"name": "Test"}))
        reward = self.coord.async_add_reward.call_args[0][0]
        import uuid
        uuid.UUID(reward.id)

    async def test_cosmetic_data_parsed_from_json_string(self):
        await self.handlers["add_reward"](make_call({
            "name": "Avatar",
            "cosmetic_data": '{"color": "blue"}',
            "reward_type": "cosmetic",
        }))
        reward = self.coord.async_add_reward.call_args[0][0]
        assert reward.cosmetic_data == {"color": "blue"}

    async def test_invalid_cosmetic_data_json_becomes_none(self):
        await self.handlers["add_reward"](make_call({
            "name": "Avatar",
            "cosmetic_data": "not-json",
        }))
        reward = self.coord.async_add_reward.call_args[0][0]
        assert reward.cosmetic_data is None


class TestUpdateRewardService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._reward_services import register_reward_services
        register_reward_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_calls_update_without_reward_id_key(self):
        await self.handlers["update_reward"](make_call({
            "reward_id": "r1",
            "name": "Nouveau nom",
            "cost": 100,
        }))
        self.coord.async_update_reward.assert_awaited_once_with(
            "r1", {"name": "Nouveau nom", "cost": 100}
        )


class TestRemoveRewardService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._reward_services import register_reward_services
        register_reward_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_calls_remove(self):
        await self.handlers["remove_reward"](make_call({"reward_id": "r1"}))
        self.coord.async_remove_reward.assert_awaited_once_with("r1")


class TestClaimRewardService:
    @pytest.fixture(autouse=True)
    def setup(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._reward_services import register_reward_services
        register_reward_services(svc_hass, svc_coordinator)
        self.handlers = capture_handlers(svc_hass)
        self.coord = svc_coordinator

    async def test_calls_claim_with_reward_and_child(self):
        await self.handlers["claim_reward"](make_call({
            "reward_id": "r1",
            "child_id": "c1",
        }))
        self.coord.async_claim_reward.assert_awaited_once_with("r1", "c1")


# ---------------------------------------------------------------------------
# Registration completeness
# ---------------------------------------------------------------------------

class TestServiceRegistration:
    """Verify all expected services are registered."""

    def test_task_services_registered(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._task_services import register_task_services
        register_task_services(svc_hass, svc_coordinator)
        registered = {c[0][1] for c in svc_hass.services.async_register.call_args_list}
        for svc in ("add_task", "update_task", "remove_task", "reset_task",
                    "complete_task", "validate_task", "reject_task",
                    "suspend_task", "resume_task"):
            assert svc in registered, f"Service '{svc}' not registered"

    def test_child_services_registered(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._child_services import register_child_services
        register_child_services(svc_hass, svc_coordinator)
        registered = {c[0][1] for c in svc_hass.services.async_register.call_args_list}
        for svc in ("add_child", "update_child", "remove_child",
                    "add_points", "remove_points", "set_points",
                    "add_coins", "remove_coins", "set_coins", "set_level",
                    "add_currency"):
            assert svc in registered, f"Service '{svc}' not registered"

    def test_reward_services_registered(self, svc_hass, svc_coordinator):
        from custom_components.kids_tasks.services._reward_services import register_reward_services
        register_reward_services(svc_hass, svc_coordinator)
        registered = {c[0][1] for c in svc_hass.services.async_register.call_args_list}
        for svc in ("add_reward", "update_reward", "remove_reward", "claim_reward"):
            assert svc in registered, f"Service '{svc}' not registered"
