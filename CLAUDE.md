# Kids Tasks HA — Notes pour Claude Code

Intégration Home Assistant pour gérer les tâches récurrentes de trois enfants,
avec récompenses, validation parentale et contrôle d'accès.

Les cartes Lovelace sont dans un dépôt séparé :
[kids-tasks-ha-card](https://github.com/astrayel/kids-tasks-ha-card).

## Contexte technique

- **Cible** : Home Assistant 2024.11.0+, Python 3.12
- **Branche de travail** : `claude/home-assistant-tasks-rewards-wsch9z`
- **Tests** : `pytest tests/ -v` — Python 3.12 requis, `pip install -r requirements_test.txt`
- **290 tests**, CI GitHub Actions sur Python 3.12

## Architecture

```
custom_components/kids_tasks/
├── __init__.py         setup, migrations de registre, purge des plateformes retirées
├── storage.py          KidsTasksStore + migrate_payload — migration de schéma
├── permissions.py      contrôle d'accès à quatre régimes
├── models.py           Child, Task, Reward, TaskChildStatus, PointsHistoryEntry
├── coordinator/        _storage · _resets · _deadlines · _business (mixins)
├── services/           _child_ · _task_ · _reward_ + services système
├── sensor.py           capteurs enfants, tâches, récompenses, globaux
├── switch.py           un interrupteur par tâche × enfant
├── calendar.py         échéances et tâches récurrentes
├── statistics.py       snapshot horaire vers le recorder
└── diagnostics.py      export de diagnostic
```

**Plateformes actives** : `sensor`, `switch`, `calendar`.
`number`, `select` et `button` ont été retirées — voir `REMOVED_PLATFORMS`
dans `__init__.py` pour la raison. Leurs entités résiduelles sont purgées du
registre au démarrage.

## Invariants à ne pas casser

- **La migration de stockage vit dans `KidsTasksStore._async_migrate_func`**, pas
  après `store.async_load()`. HA vérifie la version avant de rendre la main ;
  une migration placée après n'est jamais atteinte (BUG-002).
- **`async_save_data()` refuse d'écrire tant que `_storage_loaded` est faux.**
  Ne pas contourner : c'est ce qui empêche un échec de chargement d'effacer les
  données de l'utilisateur.
- **Les services s'enregistrent via `build_registrar()`**, jamais directement
  par `hass.services.async_register`. Un service non listé dans
  `POLICY_CHILD_SCOPED` ou `POLICY_PUBLIC` est réservé aux parents par défaut.
- **Les `unique_id` des capteurs enfants dérivent de `child.id`**, jamais du
  prénom. Le prénom ne sert qu'à l'`entity_id` et au nom affiché.
- **Tout ce qui touche à un enfant précis prend un `child_id`.** Valider,
  rejeter, ou éteindre un interrupteur ne doit jamais affecter les frères et
  sœurs assignés à la même tâche.
- **Les horodatages sont tz-aware.** Utiliser `_now()` et `_parse_dt()` de
  `models.py`, jamais `datetime.now()`.

## Statuts de tâche

`todo` · `in_progress` · `completed` · `pending_validation` · `validated` ·
`failed` · `not_applicable`

`not_applicable` = jour non planifié pour une tâche quotidienne restreinte à
certains jours. Ni dû, ni gagné : exempté de pénalité, exclu des compteurs.

## Documentation

- `docs/permissions.md` — les quatre régimes, la configuration, la vérification
- `docs/dashboards.md` — vues enfant, tablette et parent, exclusion recorder
- `INTERFACE_GUIDE.md` — les quatre cartes et leur configuration YAML
- `BUGS.md` — suivi des bugs, avec cause et correction

## Travail restant

- Fusion `dev` → `main` et tag v2.1.0 (demande une validation explicite)
- Vérification d'une installation de bout en bout sur une instance neuve
