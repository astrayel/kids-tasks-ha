# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-08-16

### Corrigé

#### Perte de données à la mise à jour (BUG-002)
- `Store.async_load()` vérifie lui-même la version du fichier `.storage` et appelle `_async_migrate_func()`, dont l'implémentation par défaut lève `NotImplementedError`. La migration, placée après `store.async_load()`, n'était donc **jamais atteinte** sur une installation v1 : le chargement échouait, le coordinator repartait vide, et la première sauvegarde écrasait les données.
- Nouveau module `storage.py` : `KidsTasksStore` implémente la migration là où Home Assistant l'appelle.
- `async_save_data()` refuse d'écrire tant que le stockage n'a pas été chargé — aucun échec de chargement futur ne peut plus effacer les données.

#### Validation multi-enfants
- `validate_task` et `reject_task` acceptent un `child_id` : valider un enfant ne valide plus ses frères et sœurs, et ne les crédite plus.
- Même correction sur `switch.async_turn_off`, qui remettait la tâche à zéro pour tous les enfants assignés.

#### Cartes ↔ intégration
- Trois services appelés par les cartes n'existaient pas : `equip_cosmetic`, `adjust_points`, `adjust_coins`.
- `undoTransaction()` et `showGiveCosmeticModal()` étaient appelées sans jamais être définies.
- La création d'un enfant depuis la carte Manager ne faisait rien : l'appel était en commentaire.
- Les identifiants de tâches et de récompenses étaient reconstruits depuis l'`entity_id`, où les tirets des UUID sont devenus des underscores — ils ne correspondaient donc à rien.
- La carte enfant affichait le statut global de la tâche au lieu de celui de l'enfant.
- Aucune tâche hebdomadaire n'apparaissait au calendrier : la table des jours n'acceptait que `monday`, le modèle stocke `mon`.

#### Divers
- Six `datetime.now()` naïfs subsistaient dans `models.py`. Tous les horodatages sont désormais tz-aware, les valeurs déjà stockées étant relues comme heure locale.
- Doublon `async_activate_cosmetic` supprimé.
- `backup_data` et `get_child_history` renvoient enfin leur résultat (`SupportsResponse.ONLY`) au lieu de le déverser dans le journal.

### Ajouté

#### Contrôle d'accès (`permissions.py`)
- Quatre régimes : **parent** (administrateur), **enfant** (compte lié via `person_entity_id`, agit pour lui seul), **tablette** (compte partagé listé dans l'option `kiosk_users`, agit pour n'importe quel enfant mais ne valide ni ne touche aux points), **invité** (lecture seule).
- Les 38 services sont enregistrés via `build_registrar()` : un service non explicitement ouvert est réservé aux parents par défaut.
- Option `kiosk_users` dans le flux d'options, et masquage des vues parentales côté cartes.
- `docs/permissions.md`.

#### Statut `not_applicable`
- Une tâche quotidienne restreinte à certains jours était marquée « validée » les autres jours pour éviter la pénalité, ce qui gonflait les compteurs et les statistiques. Le nouveau statut dit ce qui est vrai et reste exempté de pénalité.

#### Autres
- Cinq services enregistrés mais absents de `services.yaml` y sont déclarés : `set_points`, `set_coins`, `set_level`, `get_child_history`, `cleanup_old_entities`.
- Le capteur enfant expose sa collection de cosmétiques et ceux qu'il porte.
- `docs/dashboards.md` : vues enfant, tablette et parent, exclusion recorder.

### Modifié

- **`unique_id` des capteurs enfants dérivés de `child.id`** et non plus du prénom : renommer un enfant orphelinait ses entités et perdait son historique. Migration du registre incluse.
- **Plateformes `number`, `select` et `button` retirées.** Les deux premières écrivaient directement dans le coordinator en contournant toute la garde ; la troisième ne créait ses entités qu'au démarrage. Leurs entités résiduelles sont purgées du registre.
- Intervalle de rafraîchissement porté de 30 s à 60 s.
- `OptionsFlowWithConfigEntry` (déprécié depuis HA 2024.11) remplacé par `OptionsFlow`.
- Documentation remise en phase : `INTERFACE_GUIDE.md` décrivait quatre cartes supprimées de ce dépôt.

### Tests

- **290 tests** (contre 174) : stockage et migration, permissions, validation par enfant, statut `not_applicable`, `switch`, `calendar`, `statistics`.
- Côté cartes, `npm test` vérifie que chaque service `kids_tasks` appelé existe réellement dans `services.yaml`.

## [2.0.0] - 2026-05-22

### Ajouté

#### Nouvelles plateformes HA
- **Plateforme `switch`** : interrupteur par tâche × enfant — ON complète la tâche, OFF la remet à zéro
- **Plateforme `calendar`** : entité `calendar.kids_tasks` — tâches avec deadline en événements horaires, tâches quotidiennes en événements toute la journée, tâches hebdomadaires sur les jours assignés

#### Cartes Lovelace personnalisées (`www/kids_tasks/kids-tasks-card.js`)
- **`kids-tasks-child-card`** : vue compacte par enfant — avatar, barre de progression XP, chips de tâches du jour, bouton de validation directe
- **`kids-tasks-validation-card`** : queue de validation parentale — liste les tâches `pending_validation` avec boutons Valider/Rejeter inline
- **`kids-tasks-task-list-card`** : tableau de bord des tâches avec filtres par fréquence et statut
- **`kids-tasks-reward-card`** : catalogue de récompenses en grille 2 colonnes, bouton Échanger actif selon solde de points
- Support automatique thème clair/sombre via design tokens HA (`--primary-color`, etc.)

#### Blueprints d'automatisation (`blueprints/automation/kids_tasks/`)
- **`notify_pending_validation.yaml`** : notifie les parents à chaque nouvelle soumission de tâche
- **`remind_incomplete_tasks.yaml`** : rappel quotidien à heure configurable pour les tâches non complétées
- **`notify_level_up.yaml`** : félicitations automatiques lors d'une montée de niveau

#### Support multilingue étendu
- Traductions ajoutées : **allemand** (de), **espagnol** (es), **néerlandais** (nl)
- Couverture complète : config flow, options, états des sélecteurs, noms des capteurs
- Total : 5 langues (FR, EN, DE, ES, NL)

#### Infrastructure de tests
- 122 tests unitaires couvrant models, coordinator, config flow, sensors
- CI GitHub Actions (`tests.yaml`) sur Python 3.12
- `pyproject.toml` + `requirements_test.txt`

#### Qualité HACS
- `diagnostics.py` — niveau Silver HACS Quality Scale
- Données sensibles masquées automatiquement (`name`, `avatar`, `person_entity_id`)

### Modifié

#### Refactorisation architecturale
- `coordinator.py` (1549 lignes) → package `coordinator/` avec 4 mixins :
  - `_storage.py` — persistence, backup, restore, migration
  - `_resets.py` — resets quotidien/hebdo/mensuel, pénalités
  - `_deadlines.py` — vérification deadlines, notifications
  - `_business.py` — CRUD et logique métier
- `services.py` (947 lignes) → package `services/` avec 3 modules :
  - `_child_services.py` — CRUD enfants, points, coins, cosmétiques, historique
  - `_task_services.py` — CRUD tâches, complétion/validation/rejet, resets, pénalités
  - `_reward_services.py` — CRUD récompenses, réclamation, catalogue

#### Conformité HA modernes
- `hass.data` → `entry.runtime_data` avec dataclass `KidsTasksData`
- `DeviceInfo` ajouté sur toutes les entités (sensor, button, select, number, switch)
- API entity_registry publique (`er.async_get()`, `er.async_entries_for_config_entry()`)
- Logs `f-string` → format `%`
- Version minimale `homeassistant` : `2024.1.0` → `2024.11.0`
- Suppression des labels de catégorie hardcodés en français

#### Schéma de stockage v1 → v2
- `STORAGE_VERSION = 2`
- Migration automatique : `assigned_child_id` (string) → `assigned_child_ids` (liste)
- Ajout du champ `coins = 0` pour les profils existants

### Corrigé

- **Storage rechargé toutes les 30 s** : flag `_initialized` — `_load_data()` n'est plus appelé à chaque refresh
- **Race condition sur les resets** : `asyncio.Lock()` remplace le booléen `_reset_in_progress`
- **Timezone incorrecte** : `dt_util.now()` remplace `datetime.now()` dans coordinator, models et sensor
- **Callbacks invalidés après reload** : `coordinator._platform_add_entities` remplace le stockage dans `hass.data`
- **Services non supprimés au déchargement** : suppression dynamique via `hass.services.async_services()` dans `async_unload_entry`

---

## [1.0.0] - 2025-01-07

### Ajouté
- Première version de l'intégration Kids Tasks Manager
- Gestion complète des profils enfants avec système de points/niveaux
- Système de tâches récurrentes avec catégorisation
- Validation parentale optionnelle avec notifications
- Système de récompenses personnalisable
- Services complets pour la gestion via Home Assistant
- Support multilingue (français/anglais)
- Dashboards dédiés parents et enfants
- Entités automatiques : capteurs, boutons, sélecteurs
- Configuration flow intégrée
- Stockage persistant des données
- Événements système pour automatisations
- Support HACS complet
- Documentation complète

### Fonctionnalités
- `kids_tasks.add_child` - Ajouter un enfant
- `kids_tasks.add_task` - Créer une tâche récurrente  
- `kids_tasks.add_reward` - Définir une récompense
- `kids_tasks.complete_task` - Marquer une tâche terminée
- `kids_tasks.validate_task` - Valider une tâche (parents)
- `kids_tasks.claim_reward` - Réclamer une récompense
- `kids_tasks.reset_task` - Remettre une tâche à zéro

### Entités créées
- Capteurs de points, niveaux, tâches complétées par enfant
- Capteurs globaux (tâches en attente, total journalier)
- Boutons de completion et validation des tâches
- Sélecteurs de statut des tâches
- Contrôles numériques pour les points des tâches

[2.0.0]: https://github.com/astrayel/kids-tasks-ha/releases/tag/v2.0.0
[1.0.0]: https://github.com/astrayel/kids-tasks-ha/releases/tag/v1.0.0