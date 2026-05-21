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

---

### Section 4 — Modernisation des cartes Lovelace (priorité haute)

Objectifs : cartes **synthétiques** (info clé visible d'un coup d'œil), **pratiques** (actions en 1 tap, pas de navigation inutile) et **modernes** (Material Design 3, thème HA, responsive mobile).
Mockups Canva générés — choisir la variante préférée parmi :
- Variante 1 : https://www.canva.com/d/MMAqWVfvgS9QC3Q
- Variante 2 : https://www.canva.com/d/iJsfUFa3LKGU4pv
- Variante 3 : https://www.canva.com/d/jKTqVNYAqKmV-Y7
- Variante 4 : https://www.canva.com/d/1MKXtZvjGFB2oNc

#### 4.1 Architecture technique
Fichier : `www/kids_tasks/kids-tasks-card.js`
- **LitElement** (déjà disponible dans HA, pas de dépendance externe)
- Design tokens HA : `--primary-color`, `--card-background-color`, `--primary-text-color`, etc.
- Support thème clair/sombre automatique via variables CSS HA
- Enregistrement : `customElements.define('kids-tasks-card', KidsTasksCard)`
- 4 cartes indépendantes déclarées dans le même fichier JS

```
┌─────────────────────────────────────────┐
│  kids-tasks-card.js                     │
│  ├── KidsTasksChildCard                 │
│  ├── KidsTasksValidationCard            │
│  ├── KidsTasksTaskListCard              │
│  └── KidsTasksRewardCard               │
└─────────────────────────────────────────┘
```

#### 4.2 Carte enfant (kids-tasks-child-card)
Vue compacte d'un enfant — à placer en grille (1 carte par enfant).

```
┌──────────────────────────────────┐
│  🧙 Léo              Niv. 4  ⭐  │
│  ████████░░░░  320 pts  💰 45   │
│  ✅ Chambre  ✅ Devoirs  ⏳ Dents │
│  [Valider 2]           [Détails] │
└──────────────────────────────────┘
```
- Avatar (emoji/image) + nom + badge niveau
- Barre de progression XP avec points / seuil prochain niveau
- Chips de tâches du jour : ✅ fait / ⏳ en attente / ⬜ à faire
- Bouton "Valider N" si tâches en attente de validation
- Gradient de couleur configurable par enfant (`card_gradient_start/end`)
- Config YAML : `type: kids-tasks-child-card`, `child_id: xxx`

#### 4.3 Carte validation parentale (kids-tasks-validation-card)
Queue de validation — vue parent, zéro scroll inutile.

```
┌──────────────────────────────────┐
│  À valider          3 en attente │
├──────────────────────────────────┤
│  🛏️ Ranger chambre   👦 Léo      │
│  [✓ Valider]      [✗ Rejeter]   │
├──────────────────────────────────┤
│  📚 Devoirs maths   👧 Emma      │
│  [✓ Valider]      [✗ Rejeter]   │
├──────────────────────────────────┤
│  🍽️ Mettre la table  👦 Léo      │
│  [✓ Valider]      [✗ Rejeter]   │
└──────────────────────────────────┘
```
- Liste uniquement les tâches `pending_validation`
- Icône catégorie + nom tâche + avatar enfant sur chaque ligne
- Boutons Valider/Rejeter inline (appelle `kids_tasks.validate_task` / `reject_task`)
- Badge de compteur dans le header
- Masquée / affiche "Tout est validé ✅" si queue vide

#### 4.4 Carte liste de tâches (kids-tasks-task-list-card)
Vue complète des tâches avec filtres — pour dashboard parent.

```
┌──────────────────────────────────┐
│  Tâches du jour   [+ Ajouter]   │
│  [Tous] [Quotidien] [En cours]  │
├──────────────────────────────────┤
│  🛏️ Ranger chambre  ●todo  15pts │
│     👦 Léo                      │
│  📚 Devoirs         ●done  20pts │
│     👧 Emma                     │
│  🍽️ Mettre la table ●wait  10pts │
│     👦 Léo          [✓][✗]      │
└──────────────────────────────────┘
```
- Chips de filtre : fréquence, statut, enfant assigné
- Indicateur de statut coloré (todo=gris, done=vert, wait=orange, fail=rouge)
- Points badge à droite
- Actions inline uniquement pour `pending_validation`
- Bouton "Ajouter" ouvre un dialog HA natif (via `ha-dialog`)

#### 4.5 Carte récompenses (kids-tasks-reward-card)
Catalogue visuel — vue enfant ou parent selon contexte.

```
┌──────────────────────────────────┐
│  Récompenses          Emma 320pts│
├─────────────┬────────────────────┤
│ 📱 Écran    │ 🚗 Sortie          │
│ +30min      │ Cinéma             │
│ 💰 200 pts  │ 💰 500 pts         │
│ [Échanger]  │ [Pas assez]        │
├─────────────┼────────────────────┤
│ 🍭 Friandise│ 👑 Privilège       │
│ Glace       │ Choisir le repas   │
│ 💰 50 pts   │ 💰 150 pts         │
│ [Échanger]  │ [Échanger]         │
└─────────────┴────────────────────┘
```
- Grille 2 colonnes, tuiles avec icône + nom + coût
- Bouton "Échanger" actif si points suffisants, grisé sinon
- Filtre par catégorie en header
- Config : `child_id` optionnel (si absent = vue admin sans échange)
- Quantité limitée affichée si `limited_quantity` défini

#### 4.6 Intégration dans install.py
Mettre à jour `install.py` pour copier `www/kids_tasks/kids-tasks-card.js` automatiquement.
Mettre à jour `INTERFACE_GUIDE.md` avec les nouveaux types de cartes et leur config YAML.
