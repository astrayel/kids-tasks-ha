# Kids Tasks HA — Notes pour Claude Code

Intégration Home Assistant pour gérer les tâches quotidiennes des enfants avec contrôle parental et système de récompenses.

## Contexte technique

- **Cible** : Home Assistant 2024.11.0+, Python 3.12
- **Branche de travail** : `claude/home-assistant-integration-analysis-k9qHo`
- **Tests** : `pytest tests/ -v` — nécessite Python 3.12 et `pip install -r requirements_test.txt`

## Ce qui a déjà été fait

### Bugs critiques corrigés
- **Storage rechargé toutes les 30s** : flag `_initialized` dans `coordinator.py` — `_load_data()` appelé une seule fois
- **Race condition sur les resets** : `asyncio.Lock()` remplace le booléen `_reset_in_progress`
- **Timezone incorrecte** : `dt_util.now()` remplace `datetime.now()` dans coordinator, models, sensor
- **Callbacks invalidés après reload** : `coordinator._platform_add_entities` remplace `hass.data`
- **Services non supprimés au déchargement** : `hass.services.async_services()` dynamique dans `async_unload_entry`

### Anti-patterns HA corrigés
- `hass.data` → `entry.runtime_data` avec dataclass `KidsTasksData` (`__init__.py`)
- `DeviceInfo` ajouté sur toutes les entités (sensor, button, select, number)
- `entity_registry` : API publique `er.async_get()` / `er.async_entries_for_config_entry()`
- Logs `_LOGGER.info(f"...")` → format `%`
- Version minimale `manifest.json` : `2024.1.0` → `2024.11.0`
- Suppression de `CATEGORY_LABELS` / `REWARD_CATEGORY_LABELS` hardcodés en français

### Infrastructure de tests (122 tests)
- `pyproject.toml`, `requirements_test.txt`, `tests/conftest.py`
- `tests/test_models.py` — 33 tests : Child, Task, Reward
- `tests/test_coordinator.py` — 30 tests : resets, penalties, CRUD, backup/restore
- `tests/test_config_flow.py` — 16 tests : schema, ConfigFlow, OptionsFlow
- `tests/test_sensor.py` — 43 tests : toutes les classes sensor
- `.github/workflows/tests.yaml` — CI sur Python 3.12

---

## Plan restant

### Section 1 — Architecture (priorité moyenne)

#### 1.1 Découper coordinator.py (~70KB, God Class)
`coordinator.py` contient tout : storage, resets, deadlines, logique métier, CRUD.
Créer un package `custom_components/kids_tasks/coordinator/` avec :
- `__init__.py` — réexporte `KidsTasksDataUpdateCoordinator`
- `storage.py` — `_load_data()`, `_save_data()`, `async_backup_data()`, `async_restore_data()`
- `resets.py` — `_check_automatic_resets()`, `_reset_tasks_with_penalty()`
- `deadlines.py` — `_check_deadlines()`
- `business.py` — `async_complete_task()`, `async_validate_task()`, `async_claim_reward()`, CRUD enfants/tâches/récompenses

#### 1.2 Découper services.py (~36KB)
Créer un package `custom_components/kids_tasks/services/` avec :
- `__init__.py` — `async_setup_services()`, `async_unregister_services()`
- `child_services.py` — services relatifs aux enfants
- `task_services.py` — services relatifs aux tâches
- `reward_services.py` — services relatifs aux récompenses

#### 1.3 Ajouter diagnostics.py
Requis pour la HACS Quality Scale (niveau Silver).
Créer `custom_components/kids_tasks/diagnostics.py` :
```python
from homeassistant.components.diagnostics import async_redact_data
TO_REDACT = {"name", "avatar"}

async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = entry.runtime_data.coordinator
    return async_redact_data({
        "children_count": len(coordinator.children),
        "tasks_count": len(coordinator.tasks),
        "rewards_count": len(coordinator.rewards),
        "last_daily_reset": str(coordinator.last_daily_reset),
        "last_weekly_reset": str(coordinator.last_weekly_reset),
        "last_monthly_reset": str(coordinator.last_monthly_reset),
    }, TO_REDACT)
```
Ajouter `"diagnostics"` dans les `platforms` de `__init__.py`.

#### 1.4 Migration de schéma storage
Bumper `STORAGE_VERSION = 2` dans `const.py` et ajouter dans `coordinator.py` :
```python
async def _migrate_data(self, data: dict) -> dict:
    version = data.get("version", 1)
    if version < 2:
        # migration v1 → v2 : ajouter coins=0 à tous les enfants
        for child in data.get("children", {}).values():
            child.setdefault("coins", 0)
        data["version"] = 2
    return data
```

---

### Section 2 — Tests

#### 2.1 ✅ Infrastructure complète — DONE (PR #3)

---

### Section 3 — Nouvelles fonctionnalités (priorité basse)

#### 3.1 Plateforme switch
Créer `custom_components/kids_tasks/switch.py` pour compléter une tâche depuis l'UI HA.
Pattern : `SwitchEntity` + `CoordinatorEntity`, état ON = tâche validée.

#### 3.2 Statistiques (statistics.py)
Intégrer avec le recorder HA pour les graphiques long terme.
Utiliser `StatisticData` / `async_add_external_statistics`.

#### 3.3 Calendrier (calendar.py)
Créer une entité `CalendarEntity` qui expose les deadlines comme événements.
Permet de voir les tâches à faire dans le calendrier HA.

#### 3.4 Blueprints
Ajouter `blueprints/automation/kids_tasks/` avec des automatisations types :
- notifier quand une tâche est en attente de validation
- envoyer un rappel si deadline approche

#### 3.5 Support multilingue
Ajouter `translations/de.json`, `translations/es.json`, `translations/nl.json`.
Base existante : `translations/fr.json` et `translations/en.json`.
