# Bugs en cours

Suivi des problèmes identifiés non encore résolus.

---

## [BUG-001] Les cartes personnalisées n'apparaissent pas dans le sélecteur de tuiles HA

**Statut** : Ouvert  
**Sévérité** : Haute  
**Composant** : `www/kids_tasks/kids-tasks-card.js`  
**Signalé le** : 2026-05-23

### Symptôme

Les 4 cartes (`kids-tasks-child-card`, `kids-tasks-validation-card`, `kids-tasks-task-list-card`, `kids-tasks-reward-card`) n'apparaissent pas dans la liste des tuiles proposées lors de l'ajout d'une carte à un dashboard Lovelace.

### Cause probable

HA utilise `window.customCards` pour peupler le sélecteur de tuiles. Plusieurs raisons possibles :

1. La ressource `/local/kids_tasks/kids-tasks-card.js` n'est pas déclarée dans Lovelace (Paramètres → Tableaux de bord → Ressources)
2. Le fichier JS est chargé après que HA scanne `window.customCards` au démarrage
3. Le champ `preview: true` absent des entrées `window.customCards` — certaines versions HA l'exigent pour afficher la carte dans le picker

### Pistes de résolution

- [ ] Vérifier que la ressource est bien déclarée avec le type `module`
- [ ] Ajouter `preview: true` dans chaque entrée de `window.customCards`
- [ ] Tester l'enregistrement via `customElements.whenDefined()` pour s'assurer que le push dans `window.customCards` se fait après la définition de l'élément
- [ ] Vérifier dans la console du navigateur que `window.customCards` contient bien les 4 entrées après le chargement de la page

### Références

- [HA Custom Cards documentation](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/)
- `www/kids_tasks/kids-tasks-card.js` — section HACS / Lovelace registration (fin du fichier)

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
