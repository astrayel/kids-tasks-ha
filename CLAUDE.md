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

### Architecture refactorisée

#### 1.3 ✅ diagnostics.py — DONE (PR #4)
`custom_components/kids_tasks/diagnostics.py` — HACS Quality Scale niveau Silver.
`TO_REDACT = {"name", "avatar", "avatar_data", "person_entity_id"}`.

#### 1.4 ✅ Migration storage v1 → v2 — DONE (PR #4)
`STORAGE_VERSION = 2` dans `const.py`.
`_migrate_data()` dans `coordinator/_storage.py` : rename `assigned_child_id` → `assigned_child_ids`, ajout `coins=0`.

#### 1.1 ✅ Découpage coordinator.py — DONE (PR #4)
`coordinator/` package avec mixins :
- `__init__.py` — `KidsTasksDataUpdateCoordinator` (83 lignes)
- `_storage.py` — `StorageMixin` : persistence, backup, restore, migration
- `_resets.py` — `ResetsMixin` : resets quotidien/hebdo/mensuel, pénalités
- `_deadlines.py` — `DeadlinesMixin` : vérification deadlines, notifications
- `_business.py` — `BusinessMixin` : CRUD et logique métier

#### 1.2 ✅ Découpage services.py — DONE (PR #4)
`services/` package :
- `__init__.py` — `async_setup_services()` + services système (backup/restore/clear)
- `_child_services.py` — CRUD enfants, points, coins, level, cosmétiques, historique
- `_task_services.py` — CRUD tâches, complétion/validation/rejet, resets, pénalités
- `_reward_services.py` — CRUD récompenses, réclamation, catalogue cosmétiques

---

### Section 2 — Tests

#### 2.1 ✅ Infrastructure complète — DONE (PR #3 + PR #4)

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
