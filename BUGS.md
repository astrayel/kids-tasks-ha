# Bugs en cours

Suivi des problèmes identifiés non encore résolus.

---

## [BUG-001] Les cartes personnalisées n'apparaissent pas dans le sélecteur de tuiles HA

**Statut** : Corrigé (commit sur `dev`)  
**Sévérité** : Haute  
**Composant** : `__init__.py`, `install.py`  
**Signalé le** : 2026-05-23

### Symptôme

Les 4 cartes (`kids-tasks-child-card`, `kids-tasks-validation-card`, `kids-tasks-task-list-card`, `kids-tasks-reward-card`) n'apparaissent pas dans la liste des tuiles proposées lors de l'ajout d'une carte à un dashboard Lovelace.

### Cause identifiée

Trois problèmes distincts :

1. **Le JS n'était pas embarqué dans le composant.** Lors d'une installation HACS ou manuelle (copie de `custom_components/kids_tasks/`), le dossier `www/` du dépôt n'est pas inclus. Le fichier n'arrivait donc jamais dans `config/www/kids_tasks/`.

2. **`install.py` ne copiait pas les sous-répertoires.** La boucle `source_dir.glob("*")` ne descendait pas dans `coordinator/`, `services/`, etc. Ces packages n'étaient pas déployés, ce qui causait des `ImportError` au démarrage.

3. **La copie dans `www/` est fragile.** HA enregistre la route statique `/local/` → `config/www/` **au démarrage**. Si le dossier `www/` n'existait pas à ce moment-là, la route n'est jamais créée — même si le fichier est copié ensuite, il reste inaccessible (404) jusqu'au prochain redémarrage complet de HA.

### Correction appliquée

- **JS embarqué dans le composant** : le fichier est dans `custom_components/kids_tasks/lovelace/kids-tasks-card.js`.
- **Chemin statique dédié** : `async_setup_entry` enregistre `/kids_tasks_lovelace` → répertoire `lovelace/` du composant via `hass.http.async_register_static_paths()`. Cette route est indépendante de `www/` et fonctionne même si `www/` n'existait pas au démarrage.
- **Flag module-level** `_FRONTEND_REGISTERED` : évite le double-enregistrement lors des rechargements de l'intégration (qui lèverait une `RuntimeError`).
- **`install.py` corrigé** : utilise `shutil.copytree()` pour tous les sous-répertoires non-`__pycache__`.
- La ressource Lovelace doit être déclarée manuellement une seule fois : Settings → Dashboards → Resources, URL `/kids_tasks_lovelace/kids-tasks-card.js`, type `JavaScript Module`.

### Références

- `custom_components/kids_tasks/__init__.py` — `async_setup_entry()`, flag `_FRONTEND_REGISTERED`
- `custom_components/kids_tasks/lovelace/kids-tasks-card.js` — fichier JS bundlé
- `install.py` — fonction `update_lovelace_resources()`, ligne ~67

---

## [BUG-002] Perte totale des données après mise à jour vers v2.0.0

**Statut** : Ouvert  
**Sévérité** : Critique  
**Composant** : `coordinator/_storage.py`, `const.py`  
**Signalé le** : 2026-05-23

### Symptôme

Après installation de la branche `dev` (v2.0.0), toutes les données sont perdues : enfants, tâches, récompenses, points, historique, configuration des cartes. L'intégration repart de zéro comme lors d'une première installation.

### Causes candidates à investiguer

1. **Migration v1 → v2 défectueuse** — `_migrate_data()` dans `coordinator/_storage.py` est appelée quand `STORAGE_VERSION` passe de 1 à 2. Si la fonction retourne un dict vide ou mal formé au lieu des données migrées, toutes les données sont silencieusement écrasées.

2. **Clé de stockage modifiée** — `STORAGE_KEY = f"{DOMAIN}.storage"` est identique entre v1 et v2, mais vérifier que le fichier `.storage/kids_tasks.storage` est bien présent sur le système après la mise à jour.

3. **`async_remove_entry` appelé par erreur** — cette fonction dans `__init__.py` appelle `storage.async_remove()` et supprime toutes les entités. Elle ne doit être appelée que lors d'une désinstallation, pas d'un rechargement. À vérifier dans les logs HA au moment du redémarrage.

4. **Rechargement de l'intégration** — si l'intégration est rechargée (plutôt que HA redémarré) pendant la mise à jour, des race conditions entre `async_unload_entry` et `async_setup_entry` pourraient corrompre l'état en mémoire avant la sauvegarde.

### Données à collecter pour diagnostiquer

- [ ] Contenu du fichier `.storage/kids_tasks.storage` **avant** et **après** la mise à jour (backup HA ou accès SSH)
- [ ] Logs HA complets au moment du redémarrage — chercher `kids_tasks` et `storage`
- [ ] Vérifier si `async_remove_entry` apparaît dans les logs
- [ ] Vérifier la valeur de `version` dans `.storage/kids_tasks.storage` (doit passer de 1 à 2 après migration)

### Risque

Perte irréversible des données utilisateur si le fichier `.storage/kids_tasks.storage` a été écrasé ou supprimé. Bloquerait toute mise à jour v1 → v2 en production.

### Références

- `custom_components/kids_tasks/coordinator/_storage.py` — `_migrate_data()`, `_load_data()`
- `custom_components/kids_tasks/const.py` — `STORAGE_VERSION = 2`, `STORAGE_KEY`
- `custom_components/kids_tasks/__init__.py` — `async_remove_entry()`

---

## [BUG-004] `AttributeError: 'State' object has no attribute 'unique_id'` dans switch.py

**Statut** : Corrigé (commit sur `dev`)  
**Sévérité** : Haute — 148 occurrences, erreur à chaque refresh du coordinator  
**Composant** : `custom_components/kids_tasks/switch.py`  
**Signalé le** : 2026-05-23

### Symptôme

```
Unexpected error updating listener for kids_tasks
AttributeError: 'State' object has no attribute 'unique_id'
  File "switch.py", line 30, in _add_new_switches
      e.unique_id
```

### Cause

`_add_new_switches()` itérait sur `hass.states.async_all()` qui retourne des objets `State`. Ces objets exposent `entity_id` mais **pas** `unique_id`. Or le code tentait de lire `e.unique_id` pour construire le set des switches déjà existants.

### Correction appliquée

Remplacement par l'entity registry qui expose bien `unique_id` :

```python
# Avant (incorrect)
existing = {
    e.unique_id
    for e in hass.states.async_all()
    if e.entity_id.startswith("switch.kidtasks_")
}

# Après (correct)
registry = er.async_get(hass)
existing = {
    e.unique_id
    for e in er.async_entries_for_config_entry(registry, entry.entry_id)
    if e.domain == "switch"
}
```

### Références

- `custom_components/kids_tasks/switch.py` — fonction `_add_new_switches()`, ligne ~29

---

## [BUG-003] Statistiques : `Invalid statistic_id` + erreur listener coordinator

**Statut** : Ouvert  
**Sévérité** : Haute  
**Composant** : `custom_components/kids_tasks/statistics.py`  
**Signalé le** : 2026-05-23

### Logs observés

```
WARNING  Failed to record statistics: Invalid statistic_id
ERROR    Unexpected error updating listener 139741625821632 for kids_tasks
```

### Cause identifiée

HA impose que le segment après `:` dans un `statistic_id` ne contienne que des caractères `[a-z0-9_]`. Les IDs d'enfants sont des UUID au format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` — les **tirets `-` sont invalides**.

Le code actuel construit par exemple :
```
kids_tasks:child_3f2a1b4c-8e7d-4f9a-b2c1-0d5e6f7a8b9c_points
```
ce qui déclenche l'erreur `Invalid statistic_id`.

L'erreur listener est une conséquence : l'exception levée dans `_maybe_record_statistics()` remonte jusqu'au coordinator malgré le `try/except`, probablement parce que `async_add_external_statistics` appelle un callback interne de manière synchrone avant que l'exception soit rattrapée.

### Correction à apporter

Dans `statistics.py`, sanitiser le `child_id` avant de l'utiliser dans le `statistic_id` :

```python
safe_id = child_id.replace("-", "_")
statistic_id=f"{DOMAIN}:child_{safe_id}_points"
```

### Références

- `custom_components/kids_tasks/statistics.py` — fonction `async_record_statistics()`, tous les appels à `_push()`
